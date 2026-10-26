import {createContext,useContext,useState,useCallback,useEffect} from 'react';
import {X,Loader2,AlertTriangle,Inbox,FlaskConical} from 'lucide-react';
const T=createContext(()=>{});export const useToast=()=>useContext(T);
export function ToastProvider({children}){
  const [list,set]=useState([]);
  const push=useCallback((msg,kind='ok')=>{const id=Math.random();set(l=>[...l,{id,msg,kind}]);setTimeout(()=>set(l=>l.filter(x=>x.id!==id)),3500);},[]);
  return <T.Provider value={push}>{children}<div className="toasts" role="status" aria-live="polite">{list.map(t=><div key={t.id} className={`toast ${t.kind}`}>{t.msg}</div>)}</div></T.Provider>;
}
export const fmt=d=>d?new Date(d).toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short'}):'-';
export const fmtDate=d=>d?new Date(d).toLocaleDateString('en-IN',{dateStyle:'medium'}):'-';
export const Badge=({tone='grey',children})=><span className={`badge ${tone}`}>{children}</span>;
export const tone=s=>({completed:'green',scheduled:'teal',active:'green',missed:'red',cancelled:'grey',revoked:'grey',skipped:'amber',snoozed:'amber',failed:'red'}[s]||'grey');
export const Card=({title,action,children,className=''})=><section className={`card ${className}`}>{(title||action)&&<header><h2>{title}</h2>{action}</header>}{children}</section>;
export const Button=({variant='primary',icon:I,children,...p})=><button className={`btn ${variant}`} {...p}>{I&&<I size={16}/>}{children}</button>;
export const Field=({label,error,hint,children})=><label className="field"><span>{label}</span>{children}{hint&&<small>{hint}</small>}{error&&<em role="alert">{error}</em>}</label>;
export const DemoBanner=({children})=><div className="demo"><FlaskConical size={16}/><span>{children||'Demo mode: all data is fictional and nothing is stored on a server.'}</span></div>;
export const Loading=({text='Loading…'})=><div className="state"><Loader2 className="spin" size={22}/><p>{text}</p></div>;
export const ErrorState=({error,onRetry})=><div className="state err" role="alert"><AlertTriangle size={22}/><p>{error?.message||'Something went wrong.'}</p>{onRetry&&<Button variant="secondary" onClick={onRetry}>Retry</Button>}</div>;
export const Empty=({title,text,children})=><div className="state"><Inbox size={22}/><strong>{title}</strong>{text&&<p>{text}</p>}{children}</div>;
export function Async({state,children}){
  if(state.loading&&!state.data)return <Loading/>;
  if(state.error)return <ErrorState error={state.error} onRetry={state.reload}/>;
  if(state.data==null)return <Empty title="No data returned"/>;
  return children(state.data);
}
export function Modal({title,onClose,children}){
  useEffect(()=>{const h=e=>e.key==='Escape'&&onClose();window.addEventListener('keydown',h);return()=>window.removeEventListener('keydown',h);},[onClose]);
  return <div className="overlay" onMouseDown={onClose}><div className="modal" role="dialog" aria-modal="true" aria-label={title} onMouseDown={e=>e.stopPropagation()}>
    <div className="modal-h"><h2>{title}</h2><button className="icon-btn" aria-label="Close dialog" onClick={onClose}><X size={18}/></button></div>{children}</div></div>;
}
export const Confirm=({title,text,yes='Confirm',onYes,onNo})=><Modal title={title} onClose={onNo}><p>{text}</p><div className="row end"><Button variant="secondary" onClick={onNo}>Keep</Button><Button variant="danger" onClick={onYes}>{yes}</Button></div></Modal>;
