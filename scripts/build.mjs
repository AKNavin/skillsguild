import {readFile,readdir,mkdir,writeFile,copyFile,lstat} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=fileURLToPath(new URL('..',import.meta.url));
const validCategories=['algotrading','hr','content'];
const dist=path.join(root,'dist');
const config=JSON.parse(await readFile(path.join(root,'site.config.json'),'utf8'));
if(config.repository&&!/^[\w.-]+\/[\w.-]+$/.test(config.repository))throw new Error('repository must be owner/repository');
const licence=await readFile(path.join(root,'LICENSE'));
const catalogue=[];
async function filesIn(dir,prefix=''){
  const result=[];
  for(const entry of await readdir(dir,{withFileTypes:true})){
    const p=path.join(dir,entry.name),name=prefix+entry.name;
    if(entry.name.startsWith('.'))throw new Error(`Hidden files are not allowed in skill packages: ${name}`);
    const info=await lstat(p);if(info.isSymbolicLink())throw new Error(`Symlink rejected: ${name}`);
    if(entry.isDirectory())result.push(...await filesIn(p,name+'/'));
    else if(entry.isFile()){if(info.size>1024*1024)throw new Error(`Skill file exceeds 1 MB: ${name}`);result.push({name,data:await readFile(p)});}
  }return result;
}
const crcTable=Array.from({length:256},(_,n)=>{for(let i=0;i<8;i++)n=(n&1)?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
function crc32(bytes){let crc=0xffffffff;for(const b of bytes)crc=crcTable[(crc^b)&255]^(crc>>>8);return(crc^0xffffffff)>>>0;}
function zip(files){
  let offset=0;const parts=[],central=[];
  for(const f of files){const name=Buffer.from(f.name),data=Buffer.from(f.data),crc=crc32(data),header=Buffer.alloc(30);header.writeUInt32LE(0x04034b50);header.writeUInt16LE(20,4);header.writeUInt16LE(0x800,6);header.writeUInt16LE(33,12);header.writeUInt32LE(crc,14);header.writeUInt32LE(data.length,18);header.writeUInt32LE(data.length,22);header.writeUInt16LE(name.length,26);parts.push(header,name,data);const c=Buffer.alloc(46);c.writeUInt32LE(0x02014b50);c.writeUInt16LE(20,4);c.writeUInt16LE(20,6);c.writeUInt16LE(0x800,8);c.writeUInt16LE(33,14);c.writeUInt32LE(crc,16);c.writeUInt32LE(data.length,20);c.writeUInt32LE(data.length,24);c.writeUInt16LE(name.length,28);c.writeUInt32LE(offset,42);central.push(c,name);offset+=header.length+name.length+data.length;}
  const directory=Buffer.concat(central),end=Buffer.alloc(22);end.writeUInt32LE(0x06054b50);end.writeUInt16LE(files.length,8);end.writeUInt16LE(files.length,10);end.writeUInt32LE(directory.length,12);end.writeUInt32LE(offset,16);return Buffer.concat([...parts,directory,end]);
}
for(const category of (await readdir(path.join(root,'skills'))).sort()){
  if(!validCategories.includes(category))throw new Error(`Unknown category: ${category}`);
  for(const name of (await readdir(path.join(root,'skills',category))).sort()){
    if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)||name.length>=64)throw new Error(`Invalid skill name: ${name}`);
    const folder=path.join(root,'skills',category,name),files=await filesIn(folder);
    const metadata=JSON.parse((files.find(f=>f.name==='metadata.json')?.data||'').toString());
    const instructions=(files.find(f=>f.name==='SKILL.md')?.data||'').toString();
    for(const field of ['title','description','author','version'])if(typeof metadata[field]!=='string'||!metadata[field].trim())throw new Error(`Missing ${field}: ${name}`);
    if(!/^\d+\.\d+\.\d+$/.test(metadata.version))throw new Error(`Invalid version: ${name}`);
    if(metadata.license!=='MIT')throw new Error(`Only MIT skills accepted in this library: ${name}`);
    if(!['starter','community'].includes(metadata.status))throw new Error(`Invalid status: ${name}`);
    if(!Array.isArray(metadata.tags)||!metadata.tags.length||metadata.tags.some(t=>typeof t!=='string'||t.length>40))throw new Error(`Invalid tags: ${name}`);
    const front=instructions.match(/^---\r?\n([\s\S]+?)\r?\n---\r?\n/);
    if(!front||!new RegExp(`^name: ${name}$`,'m').test(front[1])||!/^description: .+/m.test(front[1]))throw new Error(`Invalid SKILL.md frontmatter: ${name}`);
    if(catalogue.some(s=>s.id===name))throw new Error(`Duplicate skill name: ${name}`);
    const download=`downloads/${name}.zip`;
    let image='preview-default.svg';
    if(metadata.image){
      if(typeof metadata.image!=='string'||!/^preview\.(svg|png|jpg|webp)$/.test(metadata.image))throw new Error(`Image must be preview.svg, preview.png, preview.jpg or preview.webp: ${name}`);
      const preview=files.find(f=>f.name===metadata.image);if(!preview)throw new Error(`Preview image missing: ${name}`);
      const digest=createHash('sha256').update(preview.data).digest('hex').slice(0,12);
      image=`previews/${name}.${digest}${path.extname(metadata.image)}`;
      if(!process.argv.includes('--check')){await mkdir(path.join(dist,'previews'),{recursive:true});await writeFile(path.join(dist,image),preview.data);}
    }
    if(metadata.image_alt!=null&&typeof metadata.image_alt!=='string')throw new Error(`Image alt must be text: ${name}`);
    catalogue.push({...metadata,id:name,category,download,instructions,image});
    if(!process.argv.includes('--check')){await mkdir(path.join(dist,'downloads'),{recursive:true});await writeFile(path.join(dist,download),zip([...files,{name:'LICENSE',data:licence}].map(f=>({...f,name:`${name}/${f.name}`}))));}
  }
}
if(!process.argv.includes('--check')){
  await mkdir(dist,{recursive:true});
  for(const name of await readdir(path.join(root,'src')))await copyFile(path.join(root,'src',name),path.join(dist,name));
  await writeFile(path.join(dist,'catalogue.json'),JSON.stringify(catalogue,null,2)+'\n');
  await writeFile(path.join(dist,'config.json'),JSON.stringify(config,null,2)+'\n');
  const versioned=async(base,extension,content)=>{
    const digest=createHash('sha256').update(content).digest('hex').slice(0,12);
    const name=`${base}.${digest}.${extension}`;
    await writeFile(path.join(dist,name),content);return name;
  };
  const catalogueFile=await versioned('catalogue','json',JSON.stringify(catalogue,null,2)+'\n');
  const configFile=await versioned('config','json',JSON.stringify(config,null,2)+'\n');
  const styleFile=await versioned('styles','css',await readFile(path.join(root,'src/styles.css'),'utf8'));
  const appSource=(await readFile(path.join(root,'src/app.js'),'utf8')).replace("fetch('catalogue.json')",`fetch('${catalogueFile}')`).replace("fetch('config.json')",`fetch('${configFile}')`);
  const appFile=await versioned('app','js',appSource);
  for(const name of ['index.html','contributing.html']){
    const html=(await readFile(path.join(root,'src',name),'utf8')).replace('href="styles.css"',`href="${styleFile}"`).replace('src="app.js"',`src="${appFile}"`);
    await writeFile(path.join(dist,name),html);
  }
  await copyFile(path.join(root,'LICENSE'),path.join(dist,'LICENSE'));
  await writeFile(path.join(dist,'.nojekyll'),'');
}
console.log(`${process.argv.includes('--check')?'Validated':'Built'} ${catalogue.length} skills across ${validCategories.length} categories.`);
