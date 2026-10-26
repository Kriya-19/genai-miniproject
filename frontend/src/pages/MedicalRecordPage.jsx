import {useState} from 'react';import {useParams,useNavigate,Link} from 'react-router-dom';import {Download,Trash2,Pencil} from 'lucide-react';
import useAsync from '../hooks/useAsync.js';import hp from '../services/healthPassportService.js';import {Card,Button,Field,Badge,Modal,Confirm,Async,useToast} from '../components/ui.jsx';
export default function MedicalRecord(){
  const {recordId}=useParams();const nav=useNavigate();const toast=useToast();const st=useAsync(()=>hp.getMedicalRecord(recordId),[recordId]);
  const [edit,setEdit]=useState(null);const [del,setDel]=useState(false);
  const download=r=>{if(r.file_path){toast('Use the secure record download endpoint from the backend.');return;}const b=new Blob([JSON.stringify(r,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=`${r.id}-metadata.json`;a.click();URL.revokeObjectURL(a.href);toast('Record metadata downloaded');};
  return <Async state={st}>{r=><div className="stack"><Link to="/health-passport">← Health Passport</Link>
    <Card title={r.title}><dl className="dl"><dt>Category</dt><dd>{r.category}</dd><dt>Date</dt><dd>{r.date}</dd><dt>Origin</dt><dd><Badge>{r.origin}-entered</Badge></dd><dt>File</dt><dd>{r.fileType}, {(r.size/1024).toFixed(0)} KB</dd><dt>Notes</dt><dd>{r.notes||'-'}</dd></dl>
      <div className="preview">Private document preview is available through the authenticated backend download endpoint.</div>
      <div className="row"><Button variant="secondary" icon={Download} onClick={()=>download(r)}>Download</Button><Button variant="secondary" icon={Pencil} onClick={()=>setEdit({title:r.title,notes:r.notes||''})}>Edit</Button><Button variant="danger" icon={Trash2} onClick={()=>setDel(true)}>Delete</Button></div></Card>
    {edit&&<Modal title="Edit record" onClose={()=>setEdit(null)}><form className="stack" onSubmit={async e=>{e.preventDefault();if(!edit.title.trim())return;await hp.updateMedicalRecord(r.id,edit);setEdit(null);toast('Record updated');st.reload();}}>
      <Field label="Title"><input required value={edit.title} onChange={e=>setEdit({...edit,title:e.target.value})}/></Field><Field label="Notes"><textarea value={edit.notes} onChange={e=>setEdit({...edit,notes:e.target.value})}/></Field><Button type="submit">Save</Button></form></Modal>}
    {del&&<Confirm title="Delete record?" text="This permanently removes the record from your Health Passport." yes="Delete" onNo={()=>setDel(false)} onYes={async()=>{await hp.deleteMedicalRecord(r.id);toast('Record deleted');nav('/health-passport');}}/>}</div>}</Async>;
}
