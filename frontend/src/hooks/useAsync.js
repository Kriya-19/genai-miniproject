import {useState,useEffect,useCallback} from 'react';
export default function useAsync(fn,deps=[]){
  const [s,set]=useState({loading:true,data:null,error:null});
  const run=useCallback(()=>{set(x=>({...x,loading:true,error:null}));
    return fn().then(d=>set({loading:false,data:d,error:null})).catch(e=>set({loading:false,data:null,error:e}));},deps);
  useEffect(()=>{run();},[run]);
  return {...s,reload:run};
}
