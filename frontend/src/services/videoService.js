// Call adapter interface. Replace createCallAdapter with a WebRTC implementation later.
// TODO(real): signaling client, STUN/TURN from getJoinDetails().ice_servers, ICE restart / reconnection.
export const ICE_CONFIG={iceServers:[]};
export function createCallAdapter(){
  const s={status:'idle',quality:'good',mic:true,camera:true,audioOnly:false};const subs=new Set();
  const set=p=>{Object.assign(s,p);subs.forEach(f=>f({...s}));};
  return{isDemo:true,
    subscribe(f){subs.add(f);f({...s});return()=>subs.delete(f);},
    async join(){set({status:'connecting'});await new Promise(r=>setTimeout(r,1200));set({status:'connected'});},
    toggleMic(){set({mic:!s.mic});},toggleCamera(){set({camera:!s.camera,audioOnly:false});},
    setAudioOnly(v){set({audioOnly:v,camera:!v});},
    simulateQuality(q){set({quality:q,status:q==='poor'?'reconnecting':'connected'});},
    async end(){set({status:'ended'});}};
}
