const categories = [{id:'all',name:'All skills'},{id:'algotrading',name:'Algo Trading'},{id:'hr',name:'HR'},{id:'content',name:'Content'}];
const state = {category:'all',query:'',sort:'curated',skills:[]};
const $ = selector => document.querySelector(selector);
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const businessName = id => categories.find(c=>c.id===id)?.name||id;
let config = {};
function render(){
  $('#categories').innerHTML = categories.map(c => `<button class="category-button" data-category="${c.id}" aria-pressed="${state.category===c.id}">${c.name}<span class="category-count">${state.skills.filter(s=>c.id==='all'||s.category===c.id).length}</span></button>`).join('');
  const query = state.query.toLowerCase().trim();
  const skills = state.skills.filter(s => (state.category==='all'||s.category===state.category) && `${s.title} ${s.description} ${s.tags.join(' ')} ${businessName(s.category)} ${s.category==='hr'?'human resources':''}`.toLowerCase().includes(query));
  if(state.sort==='az')skills.sort((a,b)=>a.title.localeCompare(b.title));
  else skills.sort((a,b)=>categories.findIndex(c=>c.id===a.category)-categories.findIndex(c=>c.id===b.category));
  $('#skills').innerHTML = skills.map(s=>`<article class="skill-card" aria-labelledby="title-${s.id}"><h2 class="card-title" id="title-${s.id}"><button class="title-button" data-skill="${s.id}" title="${escape(s.title)}">${escape(s.title)}</button></h2><button class="preview-button" data-skill="${s.id}" aria-label="Preview ${escape(s.title)}"><img src="${escape(s.image||'preview-default.svg')}" alt="${escape(s.image_alt||`Workflow preview for ${s.title}`)}" width="640" height="480" loading="eager"></button><div class="card-description"><p title="${escape(s.description)}">${escape(s.description)}</p><div class="card-actions"><button class="detail-button" data-skill="${s.id}" aria-label="View ${escape(s.title)} instructions">View skill ↗</button><a class="download-button" href="${escape(s.download)}" download aria-label="Download ${escape(s.title)} ZIP">Download <span aria-hidden="true">↓</span></a></div></div></article>`).join('');
  $('#result-count').textContent = `${skills.length} ${skills.length===1?'skill':'skills'} · ${state.category==='all'?'All businesses':businessName(state.category)}`;
  $('#empty').hidden = skills.length>0; $('#clear').hidden = !query && state.category==='all';
  $('#search').placeholder=state.category==='all'?'Search skills, tasks or tags':`Search ${businessName(state.category)} skills`;
}
function showSkill(id){
  const s = state.skills.find(skill=>skill.id===id);if(!s)return;
  const d=$('#detail');
  d.innerHTML=`<span class="category-pill ${s.category}">${businessName(s.category)}</span><h2 id="detail-title">${escape(s.title)}</h2><p class="detail-description">${escape(s.description)}</p><div class="detail-meta"><span>Version ${escape(s.version)}</span><span>MIT licence</span><span>${escape(s.author)}</span><span>${s.status==='starter'?'Starter skill':'Community skill'}</span></div><div class="detail-actions"><a class="button dark" href="${escape(s.download)}" download>Download skill ZIP ↓</a><button class="button plain-button" id="copy-skill">Copy instructions</button></div><p class="preview-label">SKILL.md · INSTRUCTIONS</p><pre class="skill-preview"></pre><p id="copy-status" class="toast" role="status"></p>`;
  d.querySelector('pre').textContent=s.instructions;
  $('#copy-skill').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(s.instructions);$('#copy-status').textContent='Instructions copied.';}catch{$('#copy-status').textContent='Clipboard unavailable. Select the instructions below, or download the ZIP.';}});
  $('#skill-dialog').showModal();
}
function reset(){state.category='all';state.query='';$('#search').value='';render();}
$('#categories').addEventListener('click',e=>{const b=e.target.closest('[data-category]');if(b){state.category=b.dataset.category;render();}});
$('#search').addEventListener('input',e=>{state.query=e.target.value;render();});
$('#sort').addEventListener('change',e=>{state.sort=e.target.value;render();});
$('#clear').addEventListener('click',reset);$('#reset').addEventListener('click',reset);
$('#skills').addEventListener('click',e=>{const b=e.target.closest('[data-skill]');if(b)showSkill(b.dataset.skill);});
$('.close-dialog').addEventListener('click',()=>$('#skill-dialog').close());
$('#skill-dialog').addEventListener('click',e=>{if(e.target===$('#skill-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!$('#skill-dialog').open){e.preventDefault();$('#search').focus();}});
try{
  const [catalogueResponse,configResponse] = await Promise.all([fetch('catalogue.json'),fetch('config.json')]);
  if(!catalogueResponse.ok||!configResponse.ok)throw new Error('Catalogue unavailable');
  state.skills=await catalogueResponse.json();config=await configResponse.json();
  if(config.repository)$('#github-link').href=`https://github.com/${config.repository}`;
  render();
}catch(error){$('#result-count').textContent='Catalogue unavailable. Please reload.';$('#skills').innerHTML='<p>You can still read our <a href="contributing.html">contribution guide</a>.</p>';}
