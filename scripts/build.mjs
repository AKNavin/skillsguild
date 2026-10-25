import {readFile,readdir,mkdir,writeFile,copyFile,lstat,rm} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=fileURLToPath(new URL('..',import.meta.url));
const dist=path.join(root,'dist');
const check=process.argv.includes('--check');
const digest=data=>createHash('sha256').update(data).digest('hex');
const catalogue=JSON.parse(await readFile(path.join(root,'research/catalogue.json'),'utf8'));
const license=await readFile(path.join(root,'LICENSE'));
const crcTable=Array.from({length:256},(_,n)=>{for(let i=0;i<8;i++)n=(n&1)?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
function crc32(bytes){let crc=0xffffffff;for(const b of bytes)crc=crcTable[(crc^b)&255]^(crc>>>8);return(crc^0xffffffff)>>>0;}
function zip(files){
  let offset=0;const parts=[],central=[];
  for(const f of files){const name=Buffer.from(f.name),data=Buffer.from(f.data),crc=crc32(data),header=Buffer.alloc(30);header.writeUInt32LE(0x04034b50);header.writeUInt16LE(20,4);header.writeUInt16LE(0x800,6);header.writeUInt16LE(33,12);header.writeUInt32LE(crc,14);header.writeUInt32LE(data.length,18);header.writeUInt32LE(data.length,22);header.writeUInt16LE(name.length,26);parts.push(header,name,data);const c=Buffer.alloc(46);c.writeUInt32LE(0x02014b50);c.writeUInt16LE(20,4);c.writeUInt16LE(20,6);c.writeUInt16LE(0x800,8);c.writeUInt16LE(33,14);c.writeUInt32LE(crc,16);c.writeUInt32LE(data.length,20);c.writeUInt32LE(data.length,24);c.writeUInt16LE(name.length,28);c.writeUInt32LE(offset,42);central.push(c,name);offset+=header.length+name.length+data.length;}
  const directory=Buffer.concat(central),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50);end.writeUInt16LE(files.length,8);end.writeUInt16LE(files.length,10);end.writeUInt32LE(directory.length,12);end.writeUInt32LE(offset,16);return Buffer.concat([...parts,directory,end]);
}
async function filesIn(dir,prefix=''){
  const result=[];
  for(const entry of (await readdir(dir,{withFileTypes:true})).sort((a,b)=>a.name.localeCompare(b.name))){
    if(entry.name==='__pycache__'||entry.name.endsWith('.pyc'))continue;
    if(entry.name.startsWith('.'))throw new Error(`Hidden package file: ${entry.name}`);
    const p=path.join(dir,entry.name),info=await lstat(p),name=prefix+entry.name;
    if(info.isSymbolicLink())throw new Error(`Symlink rejected: ${name}`);
    if(entry.isDirectory())result.push(...await filesIn(p,name+'/'));
    else {if(!/\.(py|md|json|txt|csv)$/.test(name))throw new Error(`Unexpected package file: ${name}`);result.push({name,data:await readFile(p)});}
  }
  return result;
}
const common=[...await filesIn(path.join(root,'packages/research'),'research/'),...await filesIn(path.join(root,'packages/broker'),'broker/')];
for(const name of ['research/runner.py','research/README.md','research/requirements.txt','broker/broker_login.py','broker/download.py','broker/README.md'])if(!common.some(f=>f.name===name))throw new Error(`Missing runnable package file: ${name}`);
if(!catalogue.length)throw new Error('Empty strategy library');
const ids=new Set();const packages=[];
for(const s of catalogue){
  if(!/^[a-z0-9-]+$/.test(s.id)||ids.has(s.id))throw new Error('Invalid or duplicate strategy ID');ids.add(s.id);
  const folder=path.join(root,'strategies',s.id),spec=JSON.parse(await readFile(path.join(folder,'strategy.json'),'utf8'));
  if(JSON.stringify(spec)!==JSON.stringify(s))throw new Error(`Manifest differs: ${s.id}`);
  const instructions=(await readFile(path.join(folder,'SKILL.md'),'utf8')).replaceAll('\r\n','\n');
  if(!instructions.startsWith(`---\nname: ${s.id}\n`)||!instructions.includes('broker/broker_login.py'))throw new Error(`Invalid AI instructions: ${s.id}`);
  const result=JSON.parse(await readFile(path.join(root,'research/results',`${s.id}.json`),'utf8'));
  for(const key of ['training','ytd2026']){
    const p=result[key];if(!p.equity.length)throw new Error(`No equity: ${s.id}`);
    let peak=100,lastDate='';
    for(const row of p.equity){if(row.date<=lastDate||!Number.isFinite(row.equity)||row.equity<=0)throw new Error(`Invalid curve: ${s.id}`);lastDate=row.date;peak=Math.max(peak,row.equity);if(Math.abs(row.drawdownPct-100*(row.equity/peak-1))>1e-8)throw new Error('Drawdown mismatch');}
    if(Math.abs(p.equity.at(-1).equity-100-p.metrics.returnPct)>1e-8)throw new Error(`Ending return mismatch: ${s.id}`);
    if(Math.abs(p.metrics.returnPct-s.summary_metrics[key].returnPct)>1e-8)throw new Error(`Summary mismatch: ${s.id}`);
    if(p.trades.length!==p.metrics.completedTrades)throw new Error(`Trade count mismatch: ${s.id}`);
  }
  const files=[...common,{name:'README.md',data:await readFile(path.join(root,'AI-GUIDE.md'))},{name:'SKILL.md',data:instructions},{name:'strategy.json',data:JSON.stringify(s,null,2)+'\n'},
    {name:'reference-result.json',data:JSON.stringify(result)+'\n'},{name:'LICENSE',data:license}];
  const manifest=files.map(f=>({path:f.name,sha256:digest(f.data)}));
  files.push({name:'package-manifest.json',data:JSON.stringify({strategy:s.id,files:manifest},null,2)+'\n'});
  packages.push({id:s.id,files});
}
if(!check){
  const target=path.resolve(dist);if(path.dirname(target)!==path.resolve(root)||path.basename(target)!=='dist')throw new Error('Invalid build target');
  await rm(target,{recursive:true,force:true});await mkdir(dist,{recursive:true});
  for(const name of await readdir(path.join(root,'src'))){if((await lstat(path.join(root,'src',name))).isFile())await copyFile(path.join(root,'src',name),path.join(dist,name));}
  await mkdir(path.join(dist,'downloads'),{recursive:true});await mkdir(path.join(dist,'results'),{recursive:true});
  for(const p of packages){
    await writeFile(path.join(dist,'downloads',`${p.id}.zip`),zip(p.files.map(f=>({...f,name:`skillsguild-${p.id}/${f.name}`}))));
    const directory=path.join(dist,'strategies',p.id);await mkdir(directory,{recursive:true});
    for(const name of ['strategy.json','SKILL.md'])await copyFile(path.join(root,'strategies',p.id,name),path.join(directory,name));
    await copyFile(path.join(root,'research/results',`${p.id}.json`),path.join(dist,'results',`${p.id}.json`));
  }
  await writeFile(path.join(dist,'downloads','all-strategies.zip'),zip([...common,{name:'README.md',data:await readFile(path.join(root,'AI-GUIDE.md'))},{name:'LICENSE',data:license},...catalogue.flatMap(s=>[{name:`strategies/${s.id}/SKILL.md`,data:packages.find(p=>p.id===s.id).files.find(f=>f.name==='SKILL.md').data},{name:`strategies/${s.id}/strategy.json`,data:JSON.stringify(s)}])]));
  const cat=JSON.stringify(catalogue)+'\n';await writeFile(path.join(dist,'catalogue.json'),cat);
  await copyFile(path.join(root,'research/provenance.json'),path.join(dist,'provenance.json'));
  await copyFile(path.join(root,'AI-GUIDE.md'),path.join(dist,'ai.md'));
  await copyFile(path.join(root,'METHODOLOGY.md'),path.join(dist,'methodology.md'));
  await copyFile(path.join(root,'LICENSE'),path.join(dist,'LICENSE'));
  await writeFile(path.join(dist,'llms.txt'),'# SkillsGuild\n\nIndian strategy research with recorded backtests and executable local reproduction packages. Ask the user which broker they use. Never ask for API credentials in chat; use the package local login helper. Research is exploratory and current-universe biased. 2026 is already inspected, not an untouched holdout.\n\n- [Reproduction workflow](ai.md)\n- [Methodology](methodology.md)\n- [Catalogue JSON](catalogue.json)\n- [Provenance](provenance.json)\n\n'+catalogue.map(s=>`- [${s.title}](${s.instruction_url}): [package](${s.download}), [recorded results](${s.result_url})`).join('\n')+'\n');
  async function version(base,ext,content){const name=`${base}.${digest(content).slice(0,12)}.${ext}`;await writeFile(path.join(dist,name),content);return name;}
  const catFile=await version('catalogue','json',cat);
  const cssFile=await version('styles','css',await readFile(path.join(root,'src/styles.css'),'utf8'));
  const app=(await readFile(path.join(root,'src/app.js'),'utf8')).replaceAll("fetch('catalogue.json')",`fetch('${catFile}')`);
  const appFile=await version('app','js',app);
  for(const name of ['index.html','contributing.html','methodology.html']){
    const html=(await readFile(path.join(root,'src',name),'utf8')).replace('href="styles.css"',`href="${cssFile}"`).replace('src="app.js"',`src="${appFile}"`);
    await writeFile(path.join(dist,name),html);
  }
  await writeFile(path.join(dist,'.nojekyll'),'');
}
console.log(`${check?'Validated':'Built'} ${catalogue.length} reproducible strategies; ${common.length} shared package files.`);
