const $ = selector => document.querySelector(selector);
const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const number = value => typeof value === 'number' && Number.isFinite(value);
const percent = (value, digits = 1) => number(value) ? `${value < 0 ? '−' : ''}${Math.abs(value).toFixed(digits)}%` : '—';
const fixed = (value, digits = 2) => number(value) ? value.toFixed(digits) : '—';
const sign = value => number(value) ? value < 0 ? 'negative' : value > 0 ? 'positive' : '' : '';
const state = {catalogue:[], selected:null, period:'training', chart:'equity', query:'', family:'all', sort:'original', result:null, ledgerPage:0};
const resultsCache = new Map();
const rulePictures = {
  high52:'252-session highs → rank close / high → up to 10 stocks; review in January and July. Proximity, not a breakout trigger.',
  residual:'504-return market regression → 126 residual returns ending 21 sessions ago → rank residual momentum; up to 30 stocks quarterly.',
  absolute:'126-session return → keep positive returns, rank highest first → up to 30 stocks quarterly.',
  lowvol:'126 daily returns → sample volatility, lowest first → up to 20 stocks quarterly.',
  riskmom:'126-session momentum ending 21 sessions ago ÷ recent annualised volatility → positive scores, up to 10 stocks quarterly.',
  industry:'Rank positive industry momentum → top three groups → alternate their leading stocks, up to 20 quarterly.',
  fip:'Positive top-20% formation momentum → prefer more frequent up days → up to 10 stocks monthly.',
  reversal:'42-session return minus industry mean → most negative relative returns → up to 10 stocks monthly.',
  lowbeta:'252 stock and market returns → regression beta, lowest first → up to 20 stocks quarterly.',
  lowmax:'Largest five daily returns in 21 sessions → average and rank lowest first → up to 30 stocks monthly.',
  mad:'50-session mean ÷ 200-session mean → rank highest ratios → up to 30 stocks quarterly. A ranking, not a crossover.',
  smad:'Current close ÷ 10-session mean → rank lowest ratios → up to 10 stocks monthly.'
};
let requestSequence = 0;

// Public metadata is rendered as text; only HTTP(S) resource links are accepted.
function resourceURL(value, base = location.href) {
  try { const url = new URL(String(value || ''), base); return ['https:','http:'].includes(url.protocol) ? url.href : '#'; }
  catch { return '#'; }
}
function metricValue(strategy, period, name) { return strategy.summary_metrics?.[period]?.[name]; }
function renderCatalogue() {
  const words = state.query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  const items = state.catalogue.filter(strategy => (state.family === 'all' || strategy.family === state.family) && words.every(word => `${strategy.title} ${strategy.summary} ${strategy.family} ${strategy.rebalance}`.toLowerCase().includes(word)));
  if (state.sort === 'name') items.sort((a,b) => a.title.localeCompare(b.title));
  else if (state.sort === 'cagr') items.sort((a,b) => (metricValue(b,'training','cagrPct') ?? -Infinity) - (metricValue(a,'training','cagrPct') ?? -Infinity));
  else if (state.sort === 'drawdown') items.sort((a,b) => Math.abs(metricValue(a,'training','maxDrawdownPct') ?? Infinity) - Math.abs(metricValue(b,'training','maxDrawdownPct') ?? Infinity));
  else if (state.sort === 'ytd') items.sort((a,b) => (metricValue(b,'ytd2026','returnPct') ?? -Infinity) - (metricValue(a,'ytd2026','returnPct') ?? -Infinity));
  else items.sort((a,b) => (a.number ?? 0) - (b.number ?? 0));
  $('#strategy-rows').innerHTML = items.map(strategy => `<tr data-strategy="${escape(strategy.id)}" class="${strategy.id === state.selected?.id ? 'selected' : ''}"><td><button class="strategy-title" data-select="${escape(strategy.id)}" ${strategy.id === state.selected?.id ? 'aria-current="true"' : ''}>${escape(strategy.title)}</button><span class="strategy-meta">${escape(strategy.family)} · ${escape(strategy.rebalance)}</span></td><td>${percent(metricValue(strategy,'training','cagrPct'))}</td><td>${percent(metricValue(strategy,'training','maxDrawdownPct'))}</td><td class="${sign(metricValue(strategy,'ytd2026','returnPct'))}">${percent(metricValue(strategy,'ytd2026','returnPct'))}</td></tr>`).join('');
  $('#result-count').textContent = `${items.length} of ${state.catalogue.length} strategies`;
  $('#total-count').textContent = state.catalogue.length;
  $('#clear-filters').hidden = !state.query && state.family === 'all';
  $('#empty-state').hidden = items.length > 0;
}
function selectedPeriod() { return state.result?.[state.period]; }
function metric(label, value, note, className = '') { return `<div class="metric"><span class="metric-label">${label}</span><span class="metric-value ${className}">${value}</span><span class="metric-note">${note}</span></div>`; }
function renderDetail() {
  const strategy = state.selected;
  const result = selectedPeriod();
  if (!strategy || !result) return;
  const metrics = result.metrics || {};
  const training = state.period === 'training';
  const caption = training ? '2018–2025 · selection period; parameters were chosen using this history.' : '2026 through 22 October · comparison period; already inspected.';
  const rules = strategy.rules || {};
  const assumptions = Array.isArray(result.assumptions) ? result.assumptions : [];
  const limitations = Array.isArray(strategy.limitations) ? strategy.limitations : [];
  const trades = Array.isArray(result.trades) ? result.trades : [];
  const annual = Array.isArray(result.annualReturns) ? result.annualReturns : [];
  $('#strategy-detail').innerHTML = `<div class="detail-top"><div class="detail-kicker"><span class="blue-dot"></span>${escape(strategy.family)} <span> / </span>${escape(strategy.rebalance)} review</div><h2 id="detail-title">${escape(strategy.title)}</h2><p class="detail-description">${escape(strategy.summary)}</p><div class="detail-actions"><button class="button primary" id="open-reproduce">Reproduce with AI <span aria-hidden="true">↗</span></button><a class="button secondary" href="${escape(resourceURL(strategy.download))}" download>Download ZIP ↓</a><a class="raw-link" href="${escape(resourceURL(strategy.instruction_url))}">Read SKILL.md ↗</a></div></div>
  <section class="results-area" aria-labelledby="results-title"><div class="results-header"><h3 id="results-title">Recorded backtest</h3><div class="segmented" aria-label="Backtest period"><button data-period="training" aria-pressed="${training}">2018–25</button><button data-period="ytd2026" aria-pressed="${!training}">2026 comparison</button></div></div><p class="period-caption">${caption}</p><div class="metrics">${metric(training ? 'Net CAGR' : 'Net return',percent(training ? metrics.cagrPct : metrics.returnPct),training ? 'Annualised · selected history' : 'To 22 Oct · not annualised')}${metric('Max drawdown',percent(metrics.maxDrawdownPct),'Peak to trough','negative')}${metric('Sharpe',fixed(metrics.sharpe),'Daily returns · 0% risk-free')}${metric('Closed trades',number(metrics.completedTrades) ? metrics.completedTrades.toLocaleString('en-IN') : '—','Includes terminal estimates')}</div><div class="chart-header"><span class="chart-title" id="chart-title">Growth of 100 · net of modelled costs</span><div class="chart-tabs" aria-label="Chart view"><button data-chart="equity" aria-pressed="${state.chart === 'equity'}">Equity</button><button data-chart="drawdown" aria-pressed="${state.chart === 'drawdown'}">Drawdown</button></div></div><div id="chart-container"></div><div class="chart-legend"><span><i class="legend-key"></i>Strategy · daily observations</span><button class="chart-download" id="download-equity">Download curve CSV ↓</button></div><div class="annual-section"><div class="annual-header">Calendar returns<span>${training ? 'Net of modelled costs' : 'Partial year · through 22 October'}</span></div><div class="annual-returns ${annual.length < 2 ? 'single' : ''}">${annual.map(row => `<div class="annual-return ${row.returnPct < 0 ? 'loss' : ''}"><span class="year">${escape(row.year)}</span><span class="return ${sign(row.returnPct)}">${percent(row.returnPct)}</span></div>`).join('')}</div></div></section>
  <section class="rules-section"><div class="section-heading"><h3 class="section-title">The trading logic</h3><a href="${escape(resourceURL(strategy.manifest_url || `strategies/${strategy.id}/strategy.json`))}">Strategy JSON ↗</a></div><dl class="rule-list"><dt>Universe</dt><dd>${escape(strategy.universe)}</dd><dt>Selection</dt><dd>${escape(rules.entry)}</dd><dt>Exit</dt><dd>${escape(rules.exit)}</dd><dt>Position size</dt><dd>${escape(rules.sizing)}</dd><dt>Execution</dt><dd>${escape(rules.execution)}</dd></dl></section>
  <div class="detail-disclosures"><details><summary>Assumptions & limitations<span class="summary-count">Read before using</span></summary><div class="disclosure-body"><div class="assumption-pills"><span>Long only</span><span>No leverage</span><span>Fractional adjusted shares</span><span>Equity starts at 100</span></div><ul>${[...assumptions,...limitations].map(item => `<li>${escape(item)}</li>`).join('')}</ul></div></details><details id="trade-details"><summary>Trade ledger<span class="summary-count">${trades.length.toLocaleString('en-IN')} closed trades</span></summary><div class="disclosure-body"><div class="table-scroll" id="ledger-table"></div><div class="ledger-actions"><span id="ledger-range"></span><button class="text-button" id="ledger-previous">Previous</button><button class="text-button" id="ledger-next">Next</button><button class="text-button" id="download-trades">Download all CSV ↓</button></div><p style="margin-top:10px">P&amp;L is in normalised equity points. Terminal exits are modelled close-price estimates.</p></div></details><details><summary>Parameters & result files<span class="summary-count">Machine readable</span></summary><div class="disclosure-body"><pre class="json-preview">${escape(JSON.stringify(strategy.configuration || strategy.parameters || {},null,2))}</pre><div class="ledger-actions"><a href="${escape(resourceURL(strategy.result_url))}" download>Download recorded result JSON ↓</a><a href="${escape(resourceURL(strategy.instruction_url))}">Read AI instructions ↗</a></div></div></details><details><summary>Curve observations<span class="summary-count">Accessible data table</span></summary><div class="disclosure-body"><p>First and last five observations shown. Download the curve CSV for the full daily series.</p><div class="table-scroll">${curveTable(result.equity || [])}</div></div></details></div><p class="source-note">Research adaptation · <a href="${escape(resourceURL(strategy.source))}" target="_blank" rel="noopener noreferrer">Original research ↗</a> · <a href="methodology.html">Data, accounting & limitations</a><br>These saved results are exploratory. Reproduction with another broker or dataset can produce different results.</p>`;
  $('#strategy-detail').setAttribute('aria-busy','false');
  $('#strategy-detail').setAttribute('aria-labelledby','detail-title');
  const rulesSection = document.querySelector('.rules-section');
  if (rulesSection && rulePictures[strategy.id]) {
    const figure = document.createElement('figure'); figure.className = 'strategy-visual';
    const picture = document.createElement('img'); picture.src = `visual-${strategy.id}.svg`; picture.alt = rulePictures[strategy.id]; picture.width = 640; picture.height = 156;
    const caption = document.createElement('figcaption'); caption.textContent = rulePictures[strategy.id];
    const label = document.createElement('span'); label.className = 'visual-label'; label.textContent = 'RULE ILLUSTRATION · NOT PERFORMANCE';
    figure.append(label,picture,caption); rulesSection.prepend(figure);
  }
  renderChart();
  renderLedger();
}
function curveTable(rows) {
  const sample = rows.length > 10 ? [...rows.slice(0,5),...rows.slice(-5)] : rows;
  return `<table class="small-table"><thead><tr><th>Date</th><th>Net equity</th><th>Drawdown</th></tr></thead><tbody>${sample.map(row => `<tr><td>${escape(row.date)}</td><td>${fixed(row.equity)}</td><td>${percent(row.drawdownPct,2)}</td></tr>`).join('')}</tbody></table>`;
}
function renderChart() {
  const rows = (selectedPeriod()?.equity || []).filter(row => number(row.equity) && number(row.drawdownPct));
  const container = $('#chart-container');
  if (!container) return;
  if (rows.length < 2) { container.innerHTML = '<p class="no-data">No daily curve is available for this period.</p>'; return; }
  const drawdown = state.chart === 'drawdown';
  $('#chart-title').textContent = drawdown ? 'Drawdown from the previous peak' : 'Growth of 100 · net of modelled costs';
  $('.legend-key').style.backgroundColor = drawdown ? '#a96156' : '#1456b8';
  const values = rows.map(row => drawdown ? row.drawdownPct : row.equity);
  let low = drawdown ? Math.min(...values) : Math.min(100,...values);
  let high = drawdown ? 0 : Math.max(...values);
  if (high === low) high = low + 1;
  if (!drawdown) { const padding = (high-low) * .08; low = Math.max(0,low-padding); high += padding; }
  const width = 640, height = 250, left = 43, top = 14, right = 12, bottom = 29;
  const plotWidth = width-left-right, plotHeight = height-top-bottom;
  const x = index => left+index/(rows.length-1)*plotWidth;
  const y = value => top+(high-value)/(high-low)*plotHeight;
  const path = values.map((value,index) => `${index ? 'L' : 'M'}${x(index).toFixed(2)},${y(value).toFixed(2)}`).join(' ');
  const fillBase = drawdown ? y(0) : top+plotHeight;
  const area = `${path} L${x(rows.length-1).toFixed(2)},${fillBase.toFixed(2)} L${left},${fillBase.toFixed(2)} Z`;
  const grid = Array.from({length:5},(_,index) => { const value = low + (high-low)*index/4; return `<line class="chart-grid" x1="${left}" x2="${width-right}" y1="${y(value)}" y2="${y(value)}"/><text x="${left-9}" y="${y(value)+3}" text-anchor="end">${drawdown ? `${Math.round(value)}%` : Math.round(value).toLocaleString('en-IN')}</text>`; }).join('');
  const labels = Array.from({length:5},(_,index) => { const rowIndex = Math.round((rows.length-1)*index/4); const date = rows[rowIndex].date; const label = state.period === 'training' ? date.slice(0,7) : date.slice(5); return `<text x="${x(rowIndex)}" y="${height-7}" text-anchor="${index === 0 ? 'start' : index === 4 ? 'end' : 'middle'}">${escape(label)}</text>`; }).join('');
  const title = `${state.selected.title}: ${drawdown ? 'drawdown' : 'net equity'}, ${rows[0].date} to ${rows.at(-1).date}`;
  container.innerHTML = `<svg class="chart" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="curve-title curve-description"><title id="curve-title">${escape(title)}</title><desc id="curve-description">${rows.length} daily observations. ${drawdown ? `Maximum drawdown ${percent(Math.min(...values))}.` : `Starts at ${fixed(values[0])}; ends at ${fixed(values.at(-1))}.`} Full data available as CSV and in the observations table.</desc><defs><linearGradient id="curve-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${drawdown ? '#ad6658' : '#3977ca'}" stop-opacity="${drawdown ? '.04' : '.12'}"/><stop offset="100%" stop-color="${drawdown ? '#ad6658' : '#3977ca'}" stop-opacity="${drawdown ? '.14' : '0'}"/></linearGradient></defs>${grid}<path d="${area}" fill="url(#curve-fill)"/><path class="chart-line ${drawdown ? 'drawdown' : ''}" d="${path}"/>${labels}</svg>`;
  document.querySelectorAll('[data-chart]').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.chart === state.chart)));
}
function renderLedger() {
  const rows = selectedPeriod()?.trades || [];
  const pageSize = 12;
  const maxPage = Math.max(0,Math.ceil(rows.length/pageSize)-1);
  state.ledgerPage = Math.min(Math.max(0,state.ledgerPage),maxPage);
  const start = state.ledgerPage*pageSize;
  const page = rows.slice(start,start+pageSize);
  $('#ledger-table').innerHTML = page.length ? `<table class="small-table"><thead><tr><th>Symbol</th><th>Entry</th><th>Exit</th><th>P&amp;L pts</th><th>Return</th></tr></thead><tbody>${page.map(row => `<tr><td>${escape(row.symbol)}</td><td>${escape(row.entry_date)}</td><td>${escape(row.exit_date)}</td><td>${fixed(row.net_pnl,3)}</td><td>${percent(row.returnPct)}</td></tr>`).join('')}</tbody></table>` : '<p>No closed trades in this result.</p>';
  $('#ledger-range').textContent = rows.length ? `${start+1}–${Math.min(start+pageSize,rows.length)} of ${rows.length}` : '0 trades';
  $('#ledger-previous').disabled = state.ledgerPage === 0;
  $('#ledger-next').disabled = state.ledgerPage === maxPage;
}
async function selectStrategy(id, scroll = false) {
  const strategy = state.catalogue.find(item => item.id === id);
  if (!strategy) return;
  const sequence = ++requestSequence;
  state.selected = strategy; state.result = null; state.ledgerPage = 0;
  renderCatalogue();
  const url = new URL(location.href); url.searchParams.set('strategy',id); url.searchParams.delete('business'); history.replaceState(null,'',url);
  document.title = `${strategy.title} — SkillsGuild`;
  const detail = $('#strategy-detail');
  detail.setAttribute('aria-busy','true'); detail.removeAttribute('aria-labelledby');
  detail.innerHTML = '<div class="loading-state"><span class="loading-dot"></span><p>Loading recorded results…</p></div>';
  if (scroll && matchMedia('(max-width:979px)').matches) detail.scrollIntoView({behavior:'smooth',block:'start'});
  try {
    let result = resultsCache.get(id);
    if (!result) { const response = await fetch(resourceURL(strategy.result_url)); if (!response.ok) throw new Error('Result unavailable'); result = await response.json(); if (!result.training || !result.ytd2026) throw new Error('Incomplete result'); resultsCache.set(id,result); }
    if (sequence !== requestSequence) return;
    state.result = result; renderDetail();
  } catch {
    if (sequence !== requestSequence) return;
    detail.setAttribute('aria-busy','false');
    detail.innerHTML = `<div class="error-state"><h2>Recorded results could not be loaded.</h2><p>You can still download ${escape(strategy.title)} and inspect its instructions.</p><button class="button secondary" id="retry-result">Try again</button> <a class="button primary" href="${escape(resourceURL(strategy.download))}" download>Download ZIP ↓</a></div>`;
  }
}
function aiPrompt() {
  const broker = $('#broker').value;
  const names = {zerodha:'Zerodha Kite',dhan:'Dhan',fyers:'FYERS'};
  const publicBase = 'https://aknavin.github.io/skillsguild/';
  const instruction = resourceURL(state.selected.instruction_url, publicBase);
  const download = resourceURL(state.selected.download, publicBase);
  return `Read the strategy instructions at ${instruction}\nDownload the complete strategy package at ${download}\n\nReproduce “${state.selected.title}” locally. ${broker === 'ask' ? 'First ask which broker I use: Zerodha Kite, Dhan or FYERS.' : `Use my ${names[broker]} account for authorised historical data.`} Inspect the package README and use the bundled local broker login helper. Keep credentials and tokens on my computer; never paste them into this website, a public repository or chat.\n\nUse the exact selected configuration and documented accounting assumptions. Explain data, universe and adjustment differences before running. Produce the equity curve, drawdown, calendar returns, trade ledger and cost attribution; compare with the saved 2018–2025 selection period and already-inspected 2026 comparison. Do not place orders. Do not describe these results as an untouched out-of-sample test.`;
}
function updatePrompt() {
  if (!state.selected) return;
  $('#ai-prompt').value = aiPrompt();
  const names = {zerodha:'Zerodha Kite',dhan:'Dhan',fyers:'FYERS'};
  const broker = $('#broker').value;
  $('#broker-instructions').textContent = broker === 'ask' ? 'Choose your broker with the agent. Complete the broker’s login flow on your own computer.' : `Ask your AI to use the bundled local helper for ${names[broker]}. Complete authentication on your computer; this website receives no credentials.`;
}
function openReproduce() {
  $('#reproduce-strategy-name').textContent = state.selected.title;
  $('#dialog-download').href = resourceURL(state.selected.download);
  $('#dialog-status').textContent = '';
  updatePrompt(); $('#reproduce-dialog').showModal();
}
async function copyPrompt() {
  try { await navigator.clipboard.writeText($('#ai-prompt').value); $('#dialog-status').textContent = 'Copied. Paste these instructions into your AI agent.'; }
  catch { $('#ai-prompt').focus(); $('#ai-prompt').select(); $('#dialog-status').textContent = 'Select and copy the instructions above; clipboard access is unavailable.'; }
}
function downloadCSV(rows, keys, filename) {
  const cell = value => { let text = String(value ?? ''); if (/^[=+@\t\r]/.test(text) || (text.startsWith('-') && !Number.isFinite(Number(text)))) text = `'${text}`; return `"${text.replace(/"/g,'""')}"`; };
  const csv = [keys.join(','),...rows.map(row => keys.map(key => cell(row[key])).join(','))].join('\r\n');
  const url = URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const link = document.createElement('a'); link.href = url; link.download = filename; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url),2000);
}
function resetFilters() { state.query = ''; state.family = 'all'; $('#search').value = ''; $('#family').value = 'all'; renderCatalogue(); }
$('#search').addEventListener('input',event => { state.query = event.target.value; renderCatalogue(); });
$('#family').addEventListener('change',event => { state.family = event.target.value; renderCatalogue(); });
$('#sort').addEventListener('change',event => { state.sort = event.target.value; renderCatalogue(); });
$('#clear-filters').addEventListener('click',resetFilters); $('#reset').addEventListener('click',resetFilters);
$('#strategy-rows').addEventListener('click',event => { const row = event.target.closest('[data-strategy]'); if (row) selectStrategy(row.dataset.strategy,true); });
$('#strategy-detail').addEventListener('click',event => {
  const period = event.target.closest('[data-period]'); const chart = event.target.closest('[data-chart]'); const id = event.target.closest('button')?.id;
  if (period) { state.period = period.dataset.period; state.ledgerPage = 0; renderDetail(); $(`[data-period="${state.period}"]`).focus({preventScroll:true}); }
  else if (chart) { state.chart = chart.dataset.chart; renderChart(); }
  else if (id === 'open-reproduce') openReproduce();
  else if (id === 'retry-result') selectStrategy(state.selected.id);
  else if (id === 'ledger-previous' || id === 'ledger-next') { state.ledgerPage += id === 'ledger-next' ? 1 : -1; renderLedger(); }
  else if (id === 'download-trades') downloadCSV(selectedPeriod()?.trades || [],['symbol','entry_date','exit_date','net_pnl','returnPct','exit_reason'],`${state.selected.id}-${state.period}-trades.csv`);
  else if (id === 'download-equity') downloadCSV(selectedPeriod()?.equity || [],['date','equity','drawdownPct'],`${state.selected.id}-${state.period}-equity.csv`);
});
$('#broker').addEventListener('change',updatePrompt); $('#copy-prompt').addEventListener('click',copyPrompt);
$('.close-dialog').addEventListener('click',() => $('#reproduce-dialog').close());
$('#reproduce-dialog').addEventListener('click',event => { if (event.target === $('#reproduce-dialog')) { const box = event.target.getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) event.target.close(); } });
document.addEventListener('keydown',event => { if (event.key === '/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !$('#reproduce-dialog').open) { event.preventDefault(); $('#search').focus(); } });
try {
  const response = await fetch('catalogue.json'); if (!response.ok) throw new Error('Catalogue unavailable');
  const data = await response.json(); if (!Array.isArray(data) || !data.length) throw new Error('Empty catalogue');
  state.catalogue = data;
  $('#family').innerHTML = '<option value="all">All families</option>' + [...new Set(data.map(item => item.family))].sort().map(family => `<option value="${escape(family)}">${escape(family)}</option>`).join('');
  const requested = new URLSearchParams(location.search).get('strategy');
  await selectStrategy(data.find(item => item.id === requested)?.id || data[0].id);
} catch {
  $('#result-count').textContent = 'Research catalogue unavailable';
  $('#strategy-detail').setAttribute('aria-busy','false');
  $('#strategy-detail').innerHTML = '<div class="error-state"><h2>The research library could not be loaded.</h2><p>Reload the page to try again, or read the source files on GitHub.</p><a class="button primary" href="https://github.com/AKNavin/skillsguild">Open source repository ↗</a></div>';
}
