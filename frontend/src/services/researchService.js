import {pick,request} from './apiClient.js';import {researchData,wait} from '../mocks/data.js';
const mock={async getEvaluationSummary(){await wait();return {is_sample:true,metrics:researchData.summary};},
  async getBaselineComparison(){await wait();return {is_sample:true,rows:researchData.summary};},
  async getAblationResults(){await wait();return {is_sample:true,rows:researchData.ablations};}};
const real={getEvaluationSummary:()=>request('/research/summary'),getBaselineComparison:()=>request('/research/baseline'),getAblationResults:()=>request('/research/ablations')};
export default pick(mock,real);
