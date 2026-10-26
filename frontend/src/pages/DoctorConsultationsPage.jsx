import {useState} from 'react';
import {Link} from 'react-router-dom';
import useAsync from '../hooks/useAsync.js';
import svc from '../services/consultationService.js';
import {Card,Button,Badge,Async,Empty,fmt,useToast} from '../components/ui.jsx';

export default function DoctorConsultations(){
  const st=useAsync(()=>svc.listConsultations());
  const [busy,setBusy]=useState(null);const toast=useToast();
  async function update(id,status){setBusy(id);try{await svc.updateStatus(id,status);toast(`Consultation ${status}`);st.reload();}catch(e){toast(e.message,'bad');}finally{setBusy(null);}}
  return <Async state={st}>{d=><div className="stack">
    <Card title="Doctor consultation workspace"><p>Review assigned patient requests, accept them, and open the secure Jitsi meeting when ready.</p></Card>
    {!d.items.length?<Empty title="No assigned consultations"/>:d.items.map(c=><Card key={c.id} className="rowcard"><div><b>{c.doctor==='Assigned clinician'?'Patient consultation':c.doctor}</b><small>{fmt(c.scheduledAt)} · {c.reason||'No reason provided'}</small></div><Badge>{c.status}</Badge>
      {c.status==='scheduled'&&<><Button disabled={busy===c.id} onClick={()=>update(c.id,'accepted')}>Accept</Button><Button variant="danger" disabled={busy===c.id} onClick={()=>update(c.id,'cancelled')}>Decline</Button></>}
      {c.status==='accepted'&&<><Link className="btn primary" to={`/consultations/${c.id}`}>Join Jitsi room</Link><Button variant="secondary" onClick={()=>update(c.id,'completed')}>Complete</Button></>}</Card>)}
  </div>}</Async>;
}
