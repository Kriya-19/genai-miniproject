import {Link,useParams} from 'react-router-dom';import {AlertTriangle,Printer} from 'lucide-react';
import useAsync from '../hooks/useAsync.js';import diagnosis from '../services/diagnosisService.js';import {Card,Badge,Async,fmt} from '../components/ui.jsx';
const L=({items})=>items?.length?<ul>{items.map((x,i)=><li key={i}>{x}</li>)}</ul>:<p className="muted">None provided</p>;
export default function Results(){
  const {caseId}=useParams();const st=useAsync(()=>diagnosis.getCaseResults(caseId),[caseId]);
  return <Async state={st}>{c=><div className="stack">
    <div className="warn"><AlertTriangle size={20}/><div><b>Decision support, not a definitive diagnosis.</b> Results must be reviewed by a qualified clinician. Ranking scores are not probabilities.</div></div>
    {c.is_demo&&<div className="note amber">Demo output: this sample result was NOT generated from your input and is not clinically valid.</div>}
    {c.safety_warnings?.map((w,i)=><div className="warn urgent" key={i}><AlertTriangle size={20}/>{w}</div>)}
    <Card title="Assessment summary"><dl className="dl"><dt>Case reference</dt><dd>{c.case_id}</dd><dt>Date</dt><dd>{fmt(c.created_at)}</dd><dt>Status</dt><dd><Badge tone="green">{c.status}</Badge></dd>
      <dt>Symptoms provided</dt><dd>{c.symptoms.map(s=>(s.name||s.symptom||'')).filter(Boolean).join(', ')}</dd><dt>History used</dt><dd>{c.history_used?.join(', ')||'None'}</dd></dl></Card>
    <h2>Differential diagnosis</h2>
    {c.differential_diagnoses.map(d=><Card key={d.rank} className="dx"><header><span className="rank">#{d.rank}</span><h3>{d.condition}</h3><Badge tone="teal">ranking score {d.ranking_score}</Badge>{d.evidence_quality&&<Badge>{d.evidence_quality} evidence</Badge>}</header>
      <p>{d.explanation}</p><div className="grid2"><div><h4>Supporting</h4><L items={d.supporting_evidence}/></div><div><h4>Contradictory / absent</h4><L items={d.contradictory_evidence}/></div></div>
      <h4>Sources</h4><ul>{d.sources.map((s,i)=><li key={i}>{s.url?<a href={s.url} target="_blank" rel="noreferrer">{s.title}</a>:s.title} <small>({s.relation}; unverified)</small></li>)}</ul><p className="muted">Uncertainty: {d.uncertainty}</p></Card>)}
    <Card title="Evidence review"><ul>{c.differential_diagnoses.flatMap(d=>d.sources.map((s,i)=><li key={d.rank+'-'+i}><b>{s.title}</b>: {s.summary} <small>Relates to {d.condition} ({s.relation}). {s.details}</small></li>))}</ul>
      <h4>Case comparisons</h4><L items={c.case_comparisons?.map(x=>`${x.label}: ${x.note}`)}/></Card>
    <Card title="Model recommendations"><div className="grid2"><div><h4>Medications</h4><L items={c.recommendations?.medications}/></div><div><h4>Precautions</h4><L items={c.recommendations?.precautions}/></div><div><h4>Exercises</h4><L items={c.recommendations?.exercises}/></div><div><h4>Diet</h4><L items={c.recommendations?.diet}/></div></div></Card>
    <Card title="Literature review"><p>{c.literature_review||'No literature review was returned by the model.'}</p><h4>Case-study review</h4><p>{c.case_study_review||'No case-study review was returned by the model.'}</p></Card>
    <Card title="Explainability"><div className="grid3"><div><h4>Missing information</h4><L items={c.missing_information}/></div><div><h4>Contradictory evidence</h4><L items={c.differential_diagnoses[0]?.contradictory_evidence}/></div><div><h4>Limitations</h4><L items={c.limitations}/></div></div></Card>
    <div className="row wrap"><Link className="btn primary" to="/diagnosis">Start another assessment</Link><Link className="btn secondary" to="/health-passport">View patient history</Link>
      <Link className="btn secondary" to="/consultations">Prepare a doctor consultation</Link><Link className="btn secondary" to="/clinics">Find nearby clinics</Link>
      <button className="btn secondary" onClick={()=>window.print()}><Printer size={16}/>Print report</button></div></div>}</Async>;
}
