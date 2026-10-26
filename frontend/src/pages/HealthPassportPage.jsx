import {useState} from 'react';import {Link} from 'react-router-dom';
import useAsync from '../hooks/useAsync.js';import hp from '../services/healthPassportService.js';import consult from '../services/consultationService.js';
import {Card,Button,Field,Badge,tone,Modal,Async,Empty,useToast,fmt,fmtDate} from '../components/ui.jsx';
export const cats=[['lab','Laboratory reports'],['prescription','Prescriptions'],['consultation','Consultation notes'],['vaccination','Vaccination records'],['condition','Diagnoses and conditions'],['other','Other documents']];
const OK=['application/pdf','image/png','image/jpeg'],MAX=5*1024*1024;
function Upload({onClose,onDone}){
  const [f,setF]=useState({title:'',category:'lab',date:new Date().toISOString().slice(0,10)});const [file,setFile]=useState(null);const [err,setErr]=useState('');const [p,setP]=useState(null);const toast=useToast();
  const pickFile=e=>{const x=e.target.files[0];setErr('');setFile(null);if(!x)return;if(!OK.includes(x.type))return setErr('Only PDF, PNG or JPEG files are allowed.');if(x.size>MAX)return setErr('File exceeds the 5 MB limit.');setFile(x);};
  async function go(e){e.preventDefault();if(!file)return setErr('Choose a file to upload.');setP(0);
    try{await hp.uploadMedicalRecord(file,f,{onProgress:setP});toast('Record uploaded securely');onDone();}catch(x){setErr(x.message);setP(null);}}
  return <Modal title="Upload document" onClose={onClose}><form onSubmit={go} className="stack" noValidate>
    <Field label="File (PDF, PNG, JPEG, max 5 MB)" error={err}><input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={pickFile}/></Field>
    <Field label="Title"><input value={f.title} onChange={e=>setF({...f,title:e.target.value})}/></Field>
    <Field label="Category"><select value={f.category} onChange={e=>setF({...f,category:e.target.value})}>{cats.map(([k,l])=><option key={k} value={k}>{l}</option>)}</select></Field>
    <Field label="Date"><input type="date" value={f.date} onChange={e=>setF({...f,date:e.target.value})}/></Field>
    {p!=null&&<progress max="100" value={p} aria-label="Upload progress"/>}
    <p className="muted">Files are stored privately and can only be downloaded by authorized users.</p><div className="row end"><Button type="button" variant="secondary" onClick={onClose}>Cancel</Button><Button type="submit" disabled={p!=null}>Upload</Button></div></form></Modal>;
}
function Share({records,doctors,onDone}){
  const [ids,setIds]=useState([]);const [rec,setRec]=useState('');const [exp,setExp]=useState('7');const [ok,setOk]=useState(false);const [err,setErr]=useState('');const toast=useToast();
  async function go(e){e.preventDefault();if(!ids.length||!rec||!ok)return setErr('Choose records, a recipient and confirm consent.');setErr('');
    await hp.createShareRequest({recordIds:ids,recipient:rec,expiresAt:new Date(Date.now()+exp*864e5).toISOString()});toast('Share request created');setIds([]);setOk(false);onDone();}
  return <Card title="Share records"><form onSubmit={go} className="stack" noValidate>
    <fieldset><legend>Records to share</legend>{records.map(r=><label className="check" key={r.id}><input type="checkbox" checked={ids.includes(r.id)} onChange={e=>setIds(e.target.checked?[...ids,r.id]:ids.filter(x=>x!==r.id))}/>{r.title}</label>)}</fieldset>
    <div className="grid2"><Field label="Recipient"><select value={rec} onChange={e=>setRec(e.target.value)}><option value="">Select…</option>{doctors.map(d=><option key={d.id} value={d.id}>{d.name}</option>)}</select></Field>
      <Field label="Expiry"><select value={exp} onChange={e=>setExp(e.target.value)}><option value="1">1 day</option><option value="7">7 days</option><option value="30">30 days</option></select></Field></div>
    <p className="muted">Permission: the recipient can view the selected records until expiry. Secure links/QR codes will be issued by the backend; none is generated here.</p>
    <label className="check"><input type="checkbox" checked={ok} onChange={e=>setOk(e.target.checked)}/>I consent to share the selected records.</label>{err&&<em className="err-t" role="alert">{err}</em>}
    <Button type="submit">Create share</Button></form></Card>;
}
export default function Passport(){
  const [tab,setTab]=useState('overview');const [q,setQ]=useState('');const [cat,setCat]=useState('all');const [up,setUp]=useState(false);
  const sum=useAsync(async()=>({p:await hp.getPatientProfile(),s:await hp.getHealthSummary()}));
  const passport=useAsync(()=>hp.getPassport());
  async function downloadPdf(){const blob=await hp.downloadPassport();const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='diagnosure-health-passport.pdf';a.click();URL.revokeObjectURL(url);}
  const recs=useAsync(()=>hp.listMedicalRecords({q,category:cat}),[q,cat]);const shares=useAsync(()=>hp.listShares());const docs=useAsync(async()=>(await consult.listConsultations()).doctors);const toast=useToast();
  return <div className="stack"><div className="tabs" role="tablist">{['overview','records','sharing'].map(t=><button key={t} role="tab" aria-selected={tab===t} onClick={()=>setTab(t)}>{t[0].toUpperCase()+t.slice(1)}</button>)}</div>
  {tab==='overview'&&<Async state={sum}>{({p,s})=><>
    <Card title="Patient profile"><p><b>{p.name}</b> · {p.age||'Age not provided'}, {p.sex||'Sex not provided'}</p><small>Last updated {fmtDate(p.lastUpdated)}</small><div className="row wrap"><Button onClick={downloadPdf}>Download PDF for doctor</Button><Async state={passport}>{x=><div><img src={x.qr_code_data_url} alt="Health Passport QR code" width="160" height="160"/><small>Scan to view a read-only passport for 24 hours.</small></div>}</Async></div></Card>
    <div className="grid2"><Card title="Conditions & allergies"><h4>Conditions</h4><ul>{s.conditions.map(x=><li key={x}>{x}</li>)}</ul><h4>Allergies</h4><ul>{s.allergies.map(x=><li key={x}>{x}</li>)}</ul></Card>
      <Card title="Medications & vaccinations"><h4>Medications</h4><ul>{s.medications.map(x=><li key={x}>{x}</li>)}</ul><h4>Vaccinations</h4><ul>{s.vaccinations.map(v=><li key={v.name}>{v.name}, {fmtDate(v.date)}</li>)}</ul></Card></div>
    <Card title="AI medical summary"><Badge tone="amber">AI-generated, not clinician-verified</Badge><p>{s.aiSummary.text}</p><small>Source records: {s.aiSummary.sources.map(id=><Link key={id} to={`/health-passport/records/${id}`}> {id}</Link>)}</small>
      <p className="muted">Data origins are labelled on each record: patient-entered, clinician-entered or OCR-extracted (unverified).</p></Card></>}</Async>}
  {tab==='records'&&<><div className="row wrap"><input aria-label="Search records" placeholder="Search records" value={q} onChange={e=>setQ(e.target.value)}/>
    <select aria-label="Category" value={cat} onChange={e=>setCat(e.target.value)}><option value="all">All categories</option>{cats.map(([k,l])=><option key={k} value={k}>{l}</option>)}</select><div className="spacer"/><Button onClick={()=>setUp(true)}>Upload document</Button></div>
    <Async state={recs}>{r=>!r.length?<Empty title="No records found" text="Adjust filters or upload a document."/>:<div className="stack">{r.map(x=><Card key={x.id} className="rowcard"><div><Link to={`/health-passport/records/${x.id}`}><b>{x.title}</b></Link><small>{cats.find(c=>c[0]===x.category)?.[1]} · {x.date}</small></div><Badge tone={x.origin==='clinician'?'green':'grey'}>{x.origin}-entered</Badge></Card>)}</div>}</Async>
    {up&&<Upload onClose={()=>setUp(false)} onDone={()=>{setUp(false);recs.reload();}}/>}</>}
  {tab==='sharing'&&<><Async state={recs}>{r=><Async state={docs}>{d=><Share records={r} doctors={d} onDone={shares.reload}/>}</Async>}</Async>
    <Card title="Sharing history"><Async state={shares}>{s=>!s.length?<Empty title="No sharing history"/>:<ul className="list">{s.map(x=><li key={x.id}><span>{x.recipient}: {x.recordIds.length} record(s), expires {fmtDate(x.expiresAt)}</span><Badge tone={x.status==='active'?'green':'grey'}>{x.status}</Badge>
      {x.status==='active'&&<Button variant="ghost" onClick={async()=>{await hp.revokeShare(x.id);toast('Sharing revoked');shares.reload();}}>Revoke</Button>}</li>)}</ul>}</Async></Card></>}</div>;
}
