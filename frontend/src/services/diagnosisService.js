import {pick,request,USE_MOCKS} from './apiClient.js';import {cases,makeCase,wait} from '../mocks/data.js';
export const reportsProgress=USE_MOCKS; // real progress is shown only if the backend provides it
const getCase=async id=>{await wait();const c=cases[id];if(!c)throw new Error('Case not found');return c;};
const mock={
  async analyzeCase(payload,{onProgress,signal}={}){
    for(let i=0;i<5;i++){onProgress?.(i);await wait(700);if(signal?.aborted)throw new Error('cancelled');}
    const c=makeCase(payload);return {case_id:c.case_id,status:c.status};},
  async listCases(){await wait();return Object.values(cases).map(c=>({case_id:c.case_id,created_at:c.created_at,status:c.status,top:c.differential_diagnoses[0]?.condition}));},
  getCase,getCaseResults:getCase};
const real={
  analyzeCase:(payload,{signal}={})=>request('/analyze',{method:'POST',body:payload,signal,timeout:180000}),
  listCases:()=>request('/cases'),getCase:id=>request(`/cases/${id}`),getCaseResults:id=>request(`/cases/${id}/results`)};
export default pick(mock,real);
