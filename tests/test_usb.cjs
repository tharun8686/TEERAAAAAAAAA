const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const tick = () => new Promise(setImmediate);
test('file-opened dashboard redirects to HTTP before opening USB or posting data',()=>{
  let destination;
  vm.runInNewContext(fs.readFileSync('hardware/usb.js','utf8'), {
    location:{protocol:'file:',hostname:'',replace:url=>destination=url},
    document:{getElementById:()=>{throw Error('Must redirect before connecting');}},
    fetch:()=>{throw Error('Must not post from file origin');}
  });
  assert.equal(destination,'http://127.0.0.1:8000/live');
});
function mount({failOpen=false, failPost=false}={}) {
  const elements = new Map(), events = {}, posts = [];
  const el = id => {
    if (!elements.has(id)) elements.set(id, {textContent:'', disabled:false});
    return elements.get(id);
  };
  let pending, closed=0, released=0;
  const reader = {read:()=>new Promise(resolve=>pending=resolve),
    cancel:async()=>pending?.({done:true}), releaseLock:()=>released++};
  const port = {open:async()=>{if(failOpen)throw Error('Port busy');},
    close:async()=>closed++, readable:{getReader:()=>reader}};
  const serial = {requestPort:async()=>port, getPorts:async()=>[], addEventListener:(name,fn)=>events[name]=fn};
  const context={document:{getElementById:el},navigator:{serial},location:{protocol:'http:',hostname:'127.0.0.1'},TextDecoder,AbortSignal,
    setTimeout,clearTimeout,fetch:async(url,options)=>{
      posts.push({url,body:JSON.parse(options.body)});
      if(failPost && posts.length===1)throw Error('network');
      return {ok:true,json:async()=>({status:'complete'})};
    }};
  vm.runInNewContext(fs.readFileSync('hardware/usb.js','utf8'),context);
  return {el,posts,events,port,closed:()=>closed,released:()=>released,
    send:async message=>{pending({value:new TextEncoder().encode(JSON.stringify(message)+'\n'),done:false});await tick();}};
}
test('identifies receiver, forwards exact envelope, disconnects and reconnects',async()=>{
  const ui=mount();let run=ui.el('connect').onclick();await tick();
  await ui.send({type:'READY',role:'receiver',protocol:4,radio_ready:true});
  assert.match(ui.el('usb-status').textContent,/Receiver detected/);
  const packet={type:'RX',size:3,data:'616263',rssi:-70,snr:8};
  await ui.send(packet);assert.deepEqual(ui.posts[0].body,packet);
  assert.equal(ui.posts[0].url,'http://127.0.0.1:8000/api/hardware');
  await ui.el('disconnect').onclick();await run;
  assert.equal(ui.closed(),1);assert.equal(ui.released(),1);
  assert.equal(ui.el('connect').disabled,false);assert.equal(ui.el('disconnect').disabled,true);
  run=ui.el('connect').onclick();await tick();await ui.el('disconnect').onclick();await run;
  assert.equal(ui.closed(),2);
});
test('busy port restores controls and offers actionable error',async()=>{
  const ui=mount({failOpen:true});await ui.el('connect').onclick();
  assert.match(ui.el('error').textContent,/Port busy/);assert.equal(ui.el('connect').disabled,false);
  assert.equal(ui.closed(),0);
});
test('unplug cancels reader and releases USB',async()=>{
  const ui=mount();const run=ui.el('connect').onclick();await tick();
  ui.events.disconnect({target:ui.port});await run;assert.equal(ui.closed(),1);
});
test('retry preserves envelope and receiver reports radio failure',async()=>{
  const ui=mount({failPost:true});const run=ui.el('connect').onclick();await tick();
  await ui.send({type:'READY',role:'receiver',protocol:4,radio_ready:false});
  assert.match(ui.el('usb-status').textContent,/LoRa unavailable/);
  await ui.send({type:'RX',size:1,data:'00',rssi:-60,snr:3});
  assert.equal(ui.posts.length,2);assert.deepEqual(ui.posts[0],ui.posts[1]);
  await ui.el('disconnect').onclick();await run;
});
