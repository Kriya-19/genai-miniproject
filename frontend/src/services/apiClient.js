const BASE=(import.meta.env.VITE_API_BASE_URL||'http://localhost:8000/api').replace(/\/$/,'');
export const USE_MOCKS=import.meta.env.VITE_USE_MOCKS==='true';
export const pick=(mock,real)=>USE_MOCKS?mock:real;
let token=localStorage.getItem('diagnosure_access_token');
export const setToken=t=>{token=t;if(t)localStorage.setItem('diagnosure_access_token',t);else localStorage.removeItem('diagnosure_access_token');};
export class ApiError extends Error{constructor(m,status=0,details=null){super(m);this.status=status;this.details=details;}}
function queryString(query){return query?'?'+new URLSearchParams(Object.entries(query).filter(([,v])=>v!==''&&v!=null&&v!==false)):'';}
function headers(body){const value={Accept:'application/json'};if(token)value.Authorization=`Bearer ${token}`;if(body)value['Content-Type']='application/json';return value;}
export async function request(path,{method='GET',body,form,query,timeout=15000,signal}={}){
  const ctrl=new AbortController();const timer=setTimeout(()=>ctrl.abort(),timeout);signal?.addEventListener('abort',()=>ctrl.abort());
  try{
    const res=await fetch(BASE+path+queryString(query),{method,headers:headers(body),body:form||(body?JSON.stringify(body):undefined),signal:ctrl.signal});
    const text=await res.text();let data=null;try{data=text?JSON.parse(text):null;}catch{throw new ApiError('Server returned an invalid response',res.status);}
    if(!res.ok)throw new ApiError(data?.detail||res.statusText||'Request failed',res.status,data);
    return data;
  }catch(e){if(e instanceof ApiError)throw e;if(e.name==='AbortError')throw new ApiError('Request timed out or was cancelled');throw new ApiError('Network error: could not reach the server');}
  finally{clearTimeout(timer);}
}
export async function requestBlob(path,{method='GET',query,timeout=60000}={}){
  const ctrl=new AbortController();const timer=setTimeout(()=>ctrl.abort(),timeout);
  try{const res=await fetch(BASE+path+queryString(query),{method,headers:headers()});if(!res.ok)throw new ApiError('Download failed',res.status);return res.blob();}
  finally{clearTimeout(timer);}
}
