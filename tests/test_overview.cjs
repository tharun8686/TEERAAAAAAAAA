const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor(){this.children=[];this.textContent='';this.value='';this.hidden=false;this.listeners={};}
  append(...items){this.children.push(...items);if(!this.value&&this.children.length)this.value=this.children[0].value;}
  replaceChildren(){this.children=[];this.value='';}
  get options(){return this.children;}
  addEventListener(name,fn){this.listeners[name]=fn;}
}
async function mount(data){
  const elements=new Map(), timers=[];
  const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
  let response=data;
  const context={document:{getElementById:get,createElement:()=>new Element()},location:{protocol:'http:',hostname:'127.0.0.1'},AbortSignal,Date,Number,JSON,
    setTimeout:fn=>timers.push(fn),fetch:async()=>{if(response instanceof Error)throw response;return {ok:true,json:async()=>response};}};
  vm.runInNewContext(fs.readFileSync('hardware/overview.js','utf8'),context);
  await new Promise(setImmediate);
  return {get,async refresh(next){response=next;await timers.shift()();},timers};
}
const reading={node_id:'TE-001',timestamp:new Date().toISOString(),hazard_results:{Flood:{model_status:'success',risk_pct:0,confidence_pct:0,severity:'NORMAL'},Wildfire:{model_status:'skipped',skip_reason:'Calibration required'}},alerts_triggered:[]};
test('empty gateway never fabricates scores',async()=>{const ui=await mount({nodes:[]});assert.equal(ui.get('ops-nodes').textContent,0);assert.equal(ui.get('ops-models').textContent,'—');assert.equal(ui.get('ops-empty').hidden,false);});
test('zero risk and confidence are preserved; missing models stay unavailable',async()=>{const ui=await mount({nodes:[reading]});const cards=ui.get('ops-results').children;assert.equal(cards[0].children[1].textContent,'0% risk');assert.equal(cards[0].children[3].textContent,'Input confidence 0%');assert.equal(cards[1].children[1].textContent,'Unavailable');assert.equal(ui.get('ops-models').textContent,'1 / 2');});
test('offline retains last reading but marks it stale',async()=>{const ui=await mount({nodes:[reading]});await ui.refresh(new Error('offline'));assert.match(ui.get('ops-source').textContent,/Stale/);assert.match(ui.get('ops-status').textContent,/Gateway unavailable/);assert.match(ui.get('ops-results').children[0].children[2].textContent,/Last known/);});
test('switching nodes changes alerts and stale state',async()=>{const old={...reading,node_id:'TE-002',timestamp:'2020-01-01T00:00:00Z',alerts_triggered:[{severity:'CRITICAL',details:{message:'<img onerror=alert(1)>'}}]};const ui=await mount({nodes:[reading,old]});ui.get('ops-node').value='TE-002';ui.get('ops-node').listeners.change();assert.equal(ui.get('ops-alert-count').textContent,1);assert.match(ui.get('ops-alerts').children[0].textContent,/Last reading/);assert.equal(ui.get('ops-alerts').children[0].children.length,0);});
