import {useRef,useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Check,Loader2,Circle} from 'lucide-react';
import {Card,Button,Badge,useToast,Async,Empty,ErrorState} from '../components/ui.jsx';
import useAsync from '../hooks/useAsync.js';
import diagnosis,{reportsProgress} from '../services/diagnosisService.js';
import research from '../services/researchService.js';

const steps=['Understanding your description','Ranking possible conditions','Reviewing literature','Comparing clinical cases','Preparing the explanation'];

function Research(){
  const base=useAsync(()=>research.getBaselineComparison());
  const abl=useAsync(()=>research.getAblationResults());
  return <div className="stack">
    <Card title="What is Research Mode?"><p>Research Mode is for evaluating the diagnosis pipeline itself. It compares a simpler baseline with the multi-agent workflow and can show ablation results when a reproducible evaluation dataset is configured.</p><p className="muted">It does not analyze your symptoms, change your diagnosis, or provide clinical advice. Run experiments from the repository root; the frontend is intentionally read-only so a patient cannot start expensive model calls.</p></Card>
    <Card title="Research outputs"><div className="grid3"><div><Badge tone="teal">Code</Badge><p className="muted">Dataset preparation, full-vs-primary runs, checkpointing and metric scripts are in <code>research/scripts</code>.</p></div><div><Badge tone="green">Evidence</Badge><p className="muted">Raw per-case predictions, labels, errors, metrics and manifests are saved under <code>research/results</code>.</p></div><div><Badge tone="amber">Documentation</Badge><p className="muted">Audit, protocol, dataset card, reproducibility steps and limitations are in <code>research</code>.</p></div></div><pre className="code-block">python -m research.scripts.run_experiment --dataset research/data/smoke_cases.jsonl --pipeline primary --name smoke</pre></Card>
    <Card title="Baseline vs multi-agent"><Async state={base}>{d=>!d.rows?.length?<Empty title="Evaluation dataset not configured" text={d.message||'Connect a versioned evaluation dataset to measure these metrics.'}/>:<div className="scroll"><table><thead><tr><th>Metric</th><th>Baseline</th><th>Multi-agent</th></tr></thead><tbody>{d.rows.map(r=><tr key={r.metric}><td>{r.metric}</td><td>{r.baseline}</td><td>{r.multi}</td></tr>)}</tbody></table></div>}</Async></Card>
    <Card title="Agent ablations"><Async state={abl}>{d=>!d.rows?.length?<Empty title="Evaluation dataset not configured" text={d.message||'Run the evaluation workflow before viewing ablations.'}/>:<div className="scroll"><table><thead><tr><th>Configuration</th><th>Top-1</th><th>Top-5 recall</th></tr></thead><tbody>{d.rows.map(r=><tr key={r.config}><td>{r.config}</td><td>{r.top1}</td><td>{r.top5}</td></tr>)}</tbody></table></div>}</Async></Card>
  </div>;
}

export default function DiagnosisPage(){
  const [tab,setTab]=useState('assess');
  const [text,setText]=useState('');
  const [error,setError]=useState('');
  const [run,setRun]=useState({state:'idle',step:-1,error:null});
  const ctrl=useRef();
  const nav=useNavigate();
  const toast=useToast();
  async function submit(e){
    e.preventDefault();
    const value=text.trim();
    if(!value){setError('Describe your symptoms or health concern in one sentence.');return;}
    ctrl.current=new AbortController();
    setError('');
    setRun({state:'loading',step:-1,error:null});
    try{
      const result=await diagnosis.analyzeCase({natural_language_input:value},{signal:ctrl.current.signal,onProgress:i=>setRun(x=>({...x,step:i}))});
      toast('Analysis complete');
      nav(`/diagnosis/results/${result.case_id}`);
    }catch(x){
      setRun(ctrl.current.signal.aborted?{state:'cancelled',step:-1,error:null}:{state:'failed',step:-1,error:x});
    }
  }
  if(run.state==='loading')return <Card title="Analyzing your concern"><div className="stack">
    {reportsProgress?<><Badge tone="amber">Running the diagnosis pipeline</Badge><ol className="steps">{steps.map((s,i)=><li key={s} className={i<run.step?'done':i===run.step?'now':''}>{i<run.step?<Check size={16}/>:i===run.step?<Loader2 className="spin" size={16}/>:<Circle size={16}/>} {s}</li>)}</ol></>:<><Loader2 className="spin"/><p>The model is reviewing your description. This may take a minute.</p></>}
    <Button variant="secondary" onClick={()=>ctrl.current.abort()}>Cancel analysis</Button></div></Card>;
  return <div className="stack">
    <div className="tabs" role="tablist"><button role="tab" aria-selected={tab==='assess'} onClick={()=>setTab('assess')}>New assessment</button><button role="tab" aria-selected={tab==='research'} onClick={()=>setTab('research')}>Research Mode</button></div>
    {tab==='research'?<Research/>:<form onSubmit={submit} className="stack" noValidate>
      {run.state==='failed'&&<ErrorState error={run.error}/>}
      {run.state==='cancelled'&&<div className="note amber">Analysis was cancelled.</div>}
      <Card title="Describe how you feel"><p className="muted">Write naturally. Include your main symptoms, how long they have been present, and anything else you think is relevant.</p>
        <textarea autoFocus required rows="9" maxLength="10000" value={text} onChange={e=>{setText(e.target.value);if(e.target.value.trim())setError('');}} placeholder="Example: I have had a sore throat, fever, and a dry cough for three days. I feel tired but I can breathe normally." aria-label="Describe your symptoms and health concern"/>
        <div className="row between"><small>{text.length}/10000 characters</small>{error&&<em className="err-t" role="alert">{error}</em>}</div>
      </Card>
      <div className="note">This is clinical decision support, not a confirmed diagnosis. Your description is sent to the configured DiagnoSure diagnosis model for analysis.</div>
      <div className="row"><Button type="submit">Diagnose</Button><Button type="button" variant="secondary" onClick={()=>{setText('');setError('');setRun({state:'idle',step:-1,error:null});}}>Clear</Button></div>
    </form>}
  </div>;
}
