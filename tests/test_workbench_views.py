"""Run the actual browser rendering functions against a minimal in-memory DOM.

No browser, sockets, licensed response rows or provider requests are involved.
Node is optional for contributors; the Python/runtime installation does not need it.
"""

import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Optional Node rendering regression check")
def test_actual_provider_field_names_and_visible_live_holds():
    source = Path(__file__).resolve().parents[1] / "src/margin/interfaces/workbench/static/app.js"
    result = subprocess.run(
        ["node", "-", str(source)],
        input=r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.dataset={}; this.classList={add(){}}; this._text=''; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children=items; }
  set textContent(value) { this._text=String(value); this.children=[]; }
  get textContent() { return this._text+this.children.map(x=>x.textContent).join(' '); }
  addEventListener() {}
  setAttribute() {}
}
const ids = new Map(), fetches=[];
const context = vm.createContext({
  Intl, URL,
  document:{
    getElementById(id) { if(!ids.has(id)) ids.set(id,new Element('div')); return ids.get(id); },
    createElement(tag) { return new Element(tag); },
    createElementNS(ns,tag) { return new Element(tag); },
  },
  fetch(path) { fetches.push(path); return new Promise(()=>{}); },
});
vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),context);
function descendants(element,tag) {
  return element.children.flatMap(child=>[...(child.tag===tag?[child]:[]),...descendants(child,tag)]);
}
// Invented numbers; keys reproduce the observed REST contract rather than fixture aliases.
context.input = {
  operation:'bharatstock.get_financials', provider:'bharatstock', mode:'live', status:'success',
  payload_kind:'rest_json', payload:{data:[{
    period_end_date:'2026-06-30', fiscal_year:'2026-27', quarter:'Q1', period_type:'quarterly',
    consolidation_type:'consolidated', revenue:123456789, net_profit:0, eps:1.25, cash_flow_operating:null,
  }]}, receipt:{retrieved_at:'test'}, warnings:[], citations:[],
};
vm.runInContext('appendResult(input)',context);
const cards = ids.get('cards');
assert.deepEqual(descendants(cards,'th').map(e=>e.textContent),[
  'period_end_date','fiscal_year','quarter','period_type','consolidation_type',
  'revenue','net_profit','eps','cash_flow_operating',
]);
assert.deepEqual(descendants(cards,'td').map(e=>e.textContent),[
  '2026-06-30','2026-27','Q1','quarterly','consolidated','12,34,56,789','0','1.25','— (not returned)',
]);
assert(!descendants(cards,'th').some(e=>['period_end','profit_after_tax','reported_unit'].includes(e.textContent)));
// Unknown fields remain visible rather than becoming an all-missing fixed table.
cards.replaceChildren();
context.input.payload.data=[{unknown_amount:17}];
vm.runInContext('appendResult(input)',context);
assert.deepEqual(descendants(cards,'th').map(e=>e.textContent),['unknown_amount']);
assert.deepEqual(descendants(cards,'td').map(e=>e.textContent),['17']);
vm.runInContext(`
capabilities = new Map([
 ['bharatstock.get_stock_quote',{enabled:true}],
 ['drishti.get_news',{enabled:false,held_reason:'Requires explicit MARGIN_ENABLE_OPERATIONS opt-in.'}],
]);
setupModules();
`,context);
assert(ids.get('access-note').textContent.includes('MARGIN_ENABLE_OPERATIONS'));
assert(ids.get('access-note').textContent.includes('not a provider subscription rejection'));
const news=descendants(ids.get('modules'),'input').find(input=>input.value==='news');
assert.equal(news.disabled,true);
assert.deepEqual(fetches,['/api/status']); // Rendering/hold explanation dispatch no data request.
console.log('Financial field rendering, null/zero fidelity, unknown shape fallback and local hold explanation passed.');

(async () => {
  let state='disconnected', resolveConnect, postCount=0, cleared=0;
  const connectionResponse=new Promise(resolve=>{resolveConnect=resolve;});
  const status=()=>({mode:'live',action_nonce:'fresh-local-nonce',
    providers:{drishti:{state,metadata_fresh:state==='connected'}},uncertain_providers:[],
    ledger:{http_attempts:{bharatstock:0,drishti:0},http_limits:{bharatstock:4,drishti:24},
      completed_estimated_credits:0,reserved_credits:0,estimated_credit_limit:7},
  });
  context.setInterval=()=>17;
  context.clearInterval=id=>{assert.equal(id,17);cleared++;};
  context.fetch=async(path,options)=>{
    fetches.push(path);
    if(path==='/api/status') return {ok:true,json:async()=>status()};
    if(path==='/api/provider-connections/drishti') {
      postCount++;
      assert.equal(options.headers['X-Margin-Action'],'fresh-local-nonce');
      return connectionResponse;
    }
    throw new Error('Unexpected request: '+path);
  };
  const first=vm.runInContext('connectDrishti()',context);
  const duplicate=vm.runInContext('connectDrishti()',context);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(postCount,1);
  assert.equal(ids.get('connect').disabled,true);
  assert.equal(ids.get('connect').textContent,'Connecting…');
  assert(ids.get('connection-status').textContent.includes('Please wait'));
  state='connected';
  resolveConnect({ok:true,json:async()=>({state:'connected',metadata_fresh:true})});
  await Promise.all([first,duplicate]);
  assert.equal(cleared,1);
  assert.equal(ids.get('connect').disabled,false);
  assert(ids.get('connection-status').textContent.startsWith('Connected.'));
  assert(ids.get('connection-status').textContent.includes('were not retried'));
  await vm.runInContext('connectDrishti()',context);
  assert.equal(postCount,1); // Fresh connection check must not refresh upstream schemas again.
  state='disconnected';
  await assert.rejects(
    vm.runInContext("submitPlan({operations:[{operation:'drishti.get_news'}]},'test-key')",context),
    /No run was submitted/
  );
  assert(!fetches.includes('/api/runs'));
  context.fetch=async(path)=>{
    if(path==='/api/status') return {ok:true,json:async()=>status()};
    return {ok:false,json:async()=>({error:{code:'metadata_failed',message:'Safe test failure.'}})};
  };
  await assert.rejects(vm.runInContext('connectDrishti()',context),/Safe test failure/);
  assert(ids.get('connection-status').textContent.includes('Connection failed: Safe test failure.'));
  assert.equal(ids.get('connect').disabled,false);
  console.log('Connection progress, double-click guard, fresh reuse, error feedback and run preflight passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});

""",
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr
