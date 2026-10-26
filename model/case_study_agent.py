# # import asyncio
# # import logging
# # from typing import Dict, List, Any
# # from datetime import datetime

# # import aiohttp
# # from sklearn.feature_extraction.text import TfidfVectorizer
# # from sklearn.metrics.pairwise import cosine_similarity

# # logger = logging.getLogger(__name__)

# # class CaseStudyAgent:
# #     """Agent for reviewing historical cases and validating diagnoses"""

# #     def __init__(self):
# #         self.name = "CaseStudyAgent"
# #         self.version = "1.0.1"
# #         self.case_studies_db = []  # List of case dicts
# #         self.vectorizer = None
# #         self.symptom_vectors = None
# #         self.similarity_threshold = 0.7
# #         self.session = None

# #     async def _load_models(self) -> None:
# #         try:
# #             self.vectorizer = TfidfVectorizer(
# #                 max_features=500,
# #                 stop_words='english',
# #                 ngram_range=(1, 2)
# #             )
# #             self.session = aiohttp.ClientSession(
# #                 timeout=aiohttp.ClientTimeout(total=30),
# #                 headers={'User-Agent': 'Diagnosure-Medical-AI/1.0'}
# #             )
# #             logger.info("Case study analysis models and HTTP session initialized")
# #         except Exception as e:
# #             logger.error(f"Failed to load models/session: {str(e)}")
# #             raise

# #     async def _load_data(self, conditions: List[str]) -> None:
# #         """Load case studies from ClinicalTrials.gov public API based on input diagnosis conditions"""
# #         try:
# #             self.case_studies_db = []
# #             logger.info(f"Loading case studies for conditions: {conditions}")
# #             for condition in conditions:
# #                 api_url = "https://clinicaltrials.gov/api/query/full_studies"
# #                 params = {
# #                     'expr': condition,
# #                     'min_rnk': 1,
# #                     'max_rnk': 20,
# #                     'fmt': 'json'
# #                 }
# #                 async with self.session.get(api_url, params=params) as response:
# #                     if response.status == 200:
# #                         data = await response.json()
# #                         studies = data.get('FullStudiesResponse', {}).get('FullStudies', [])
# #                         logger.info(f"Fetched {len(studies)} studies for condition: {condition}")
# #                         for study in studies:
# #                             study_data = study.get('Study', {})
# #                             protocol_section = study_data.get('ProtocolSection', {})
# #                             description = protocol_section.get('DescriptionModule', {}).get('BriefSummary', 'No description available')
# #                             condition_list = protocol_section.get('ConditionsModule', {}).get('ConditionList', {}).get('Condition', [])
# #                             eligibility = protocol_section.get('EligibilityModule', {}).get('EligibilityCriteria', 'No eligibility criteria')
# #                             self.case_studies_db.append({
# #                                 'case_id': study_data.get('StudyIdentificationModule', {}).get('NCTId', 'Unknown'),
# #                                 'conditions': condition_list,
# #                                 'case_description': description,
# #                                 'eligibility_criteria': eligibility,
# #                                 'treatment_outcome': '',  # Not typically available in ClinicalTrials API
# #                                 'symptoms': condition_list,  # Using conditions as proxy for symptoms
# #                             })
# #             symptom_texts = [
# #                 " ".join(case.get('symptoms', [])) + " " + case.get('case_description', '')
# #                 for case in self.case_studies_db
# #             ]
# #             if symptom_texts:
# #                 self.symptom_vectors = self.vectorizer.fit_transform(symptom_texts)
# #             logger.info(f"Total loaded case studies: {len(self.case_studies_db)}")
# #         except Exception as e:
# #             logger.error(f"Failed to load case studies from ClinicalTrials.gov API: {str(e)}")
# #             self.case_studies_db = []
# #             self.symptom_vectors = None
    
# #     async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
# #         extracted_symptoms = input_data.get('extracted_symptoms', [])
# #         demographics = input_data.get('demographics', {})
# #         initial_diagnoses = input_data.get('initial_diagnoses', [])

# #         similar_cases = await self._find_similar_cases(extracted_symptoms, demographics)
# #         validated_diagnoses = await self._validate_diagnoses_with_cases(initial_diagnoses, similar_cases)
# #         insights = await self._generate_case_insights(similar_cases, demographics)

# #         return {
# #             'similar_cases': similar_cases,
# #             'validated_diagnoses': validated_diagnoses,
# #             'case_insights': insights,
# #             'case_study_metadata': {
# #                 'total_cases_analyzed': len(self.case_studies_db),
# #                 'similar_cases_found': len(similar_cases),
# #                 'similarity_threshold': self.similarity_threshold,
# #                 'agent_name': self.name,
# #                 'version': self.version,
# #                 'timestamp': datetime.now().isoformat()
# #             }
# #         }

# #     async def _find_similar_cases(self, symptoms: List[Dict[str, Any]], demographics: Dict[str, Any]) -> List[Dict[str, Any]]:
# #         if not symptoms or self.symptom_vectors is None:
# #             return []
# #         try:
# #             current_symptoms = [s['name'] for s in symptoms]
# #             current_text = " ".join(current_symptoms)
# #             current_vector = self.vectorizer.transform([current_text])
# #             similarities = cosine_similarity(current_vector, self.symptom_vectors).flatten()
# #             similar_cases = []
# #             for i, similarity in enumerate(similarities):
# #                 if similarity >= self.similarity_threshold:
# #                     case = self.case_studies_db[i]
# #                     if self._demographic_match(case, demographics):
# #                         case['similarity_score'] = float(similarity)
# #                         similar_cases.append(case)
# #             similar_cases.sort(key=lambda x: x['similarity_score'], reverse=True)
# #             return similar_cases[:10]
# #         except Exception as e:
# #             logger.error(f"Failed to find similar cases: {str(e)}")
# #             return []

# #     def _demographic_match(self, case: Dict[str, Any], demographics: Dict[str, Any]) -> bool:
# #         user_age = demographics.get('age')
# #         case_age_range = case.get('age_range')
# #         if user_age and case_age_range:
# #             try:
# #                 if '-' in case_age_range:
# #                     min_age, max_age = map(int, case_age_range.split('-'))
# #                     if not (min_age <= user_age <= max_age):
# #                         return False
# #                 elif case_age_range.isdigit():
# #                     if abs(user_age - int(case_age_range)) > 5:
# #                         return False
# #             except:
# #                 pass
# #         user_gender = demographics.get('gender')
# #         case_gender = case.get('gender')
# #         if user_gender and case_gender:
# #             if user_gender.lower() != case_gender.lower() and case_gender.lower() not in ['other', 'unknown']:
# #                 return False
# #         return True

# #     async def _validate_diagnoses_with_cases(self, diagnoses: List[Dict[str, Any]], similar_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
# #         validated_diagnoses = []
# #         for diagnosis in diagnoses:
# #             condition_name = diagnosis.get('condition', '').lower()
# #             matching_cases = [case for case in similar_cases if any(condition_name == cond.lower() for cond in case.get('conditions', []))]
# #             validation_score = self._calculate_case_validation_score(diagnosis, matching_cases)
# #             original_confidence = diagnosis.get('confidence', 0.5)
# #             case_validated_confidence = (original_confidence + validation_score) / 2
# #             validated_diagnosis = diagnosis.copy()
# #             validated_diagnosis['confidence'] = case_validated_confidence
# #             validated_diagnosis['case_validation_score'] = validation_score
# #             validated_diagnosis['supporting_cases_count'] = len(matching_cases)
# #             validated_diagnosis['case_outcomes'] = [case.get('treatment_outcome', '') for case in matching_cases]
# #             validated_diagnoses.append(validated_diagnosis)
# #         validated_diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
# #         return validated_diagnoses

# #     def _calculate_case_validation_score(self, diagnosis: Dict[str, Any], matching_cases: List[Dict[str, Any]]) -> float:
# #         if not matching_cases:
# #             return 0.5  # Neutral score
# #         similarity_scores = [case.get('similarity_score', 0) for case in matching_cases]
# #         avg_similarity = sum(similarity_scores) / len(similarity_scores)
# #         case_weight = min(len(matching_cases) / 5.0, 1.0)
# #         # ClinicalTrials.gov does not generally report outcomes; assume neutral 0.5
# #         outcome_score = 0.5
# #         validation_score = (avg_similarity * 0.7) + (case_weight * 0.3) + (outcome_score * 0.0)
# #         return min(validation_score, 1.0)

# #     async def _generate_case_insights(self, similar_cases: List[Dict[str, Any]], demographics: Dict[str, Any]) -> Dict[str, Any]:
# #         if not similar_cases:
# #             return {'insights': [], 'recommendations': [], 'warnings': []}

# #         symptom_counts = {}
# #         condition_counts = {}

# #         for case in similar_cases:
# #             for symptom in case.get('symptoms', []):
# #                 symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
# #             for condition in case.get('conditions', []):
# #                 condition_counts[condition] = condition_counts.get(condition, 0) + 1

# #         total_cases = len(similar_cases)
# #         threshold = total_cases * 0.3

# #         common_symptoms = [s for s, count in symptom_counts.items() if count >= threshold]
# #         common_conditions = [c for c, count in condition_counts.items() if count >= threshold]

# #         insights = []
# #         if common_symptoms:
# #             insights.append({'type': 'symptom_pattern', 'description': f"Common symptoms: {', '.join(common_symptoms[:3])}", 'confidence': 0.8})
# #         if common_conditions:
# #             insights.append({'type': 'condition_pattern', 'description': f"Common conditions: {', '.join(common_conditions[:3])}", 'confidence': 0.7})

# #         recommendations = []
# #         warnings = []

# #         return {
# #             'insights': insights,
# #             'recommendations': recommendations,
# #             'warnings': warnings,
# #             'statistics': {
# #                 'total_similar_cases': total_cases
# #             }
# #         }

# #     async def cleanup(self) -> None:
# #         if self.session:
# #             await self.session.close()




# #########################################################################################

# import asyncio
# import logging
# from typing import Dict, List, Any
# from datetime import datetime
# import aiohttp
# import xml.etree.ElementTree as ET

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class CaseStudyAgent:
#     """Agent for validating diagnoses using PubMed clinical case reports."""

#     def __init__(self):
#         self.name = "CaseStudyAgent"
#         self.version = "1.0.0"
#         self.session = None
#         self.case_studies_db = []

#     async def _load_models(self) -> None:
#         self.session = aiohttp.ClientSession(
#             timeout=aiohttp.ClientTimeout(total=60),
#             headers={'User-Agent': 'Diagnosure-Medical-AI/1.0'}
#         )
#         logger.info("HTTP session initialized for PubMed queries")

#     async def _search_pubmed_case_reports(self, condition: str, max_results: int = 20) -> List[Dict[str, Any]]:
#         esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
#         efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

#         params_search = {
#             'db': 'pubmed',
#             'term': f'{condition} AND "Case Reports"[Publication Type]',
#             'retmax': str(max_results),
#             'retmode': 'json'
#         }

#         async with self.session.get(esearch_url, params=params_search) as resp:
#             if resp.status != 200:
#                 logger.error(f"PubMed esearch failed for {condition} status {resp.status}")
#                 return []
#             search_data = await resp.json()
#             id_list = search_data.get('esearchresult', {}).get('idlist', [])
#             if not id_list:
#                 return []

#         params_fetch = {
#             'db': 'pubmed',
#             'id': ",".join(id_list),
#             'retmode': 'xml'
#         }

#         async with self.session.get(efetch_url, params=params_fetch) as resp:
#             if resp.status != 200:
#                 logger.error(f"PubMed efetch failed for {condition} status {resp.status}")
#                 return []
#             xml_text = await resp.text()

#         articles = []
#         try:
#             root = ET.fromstring(xml_text)
#             for article in root.findall(".//PubmedArticle"):
#                 title = article.findtext(".//ArticleTitle", default="No title")
#                 abstract = article.findtext(".//Abstract/AbstractText", default="No abstract")
#                 pmid = article.findtext(".//PMID")
#                 url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
#                 authors = []
#                 for author in article.findall(".//Author"):
#                     lastname = author.findtext("LastName")
#                     firstname = author.findtext("ForeName")
#                     if lastname and firstname:
#                         authors.append(f"{lastname}, {firstname}")
#                 articles.append({
#                     'source': 'PubMed',
#                     'title': title,
#                     'authors': authors,
#                     'abstract': abstract,
#                     'url': url
#                 })
#         except Exception as e:
#             logger.error(f"Failed to parse PubMed XML: {e}")
#             return []

#         return articles

#     async def _load_data(self, conditions: List[str]) -> None:
#         self.case_studies_db = []
#         for condition in conditions:
#             logger.info(f"Searching PubMed for case reports on condition: {condition}")
#             articles = await self._search_pubmed_case_reports(condition)
#             for article in articles:
#                 self.case_studies_db.append({
#                     'case_title': article['title'],
#                     'case_abstract': article['abstract'],
#                     'case_url': article['url'],
#                     'symptoms': condition.lower().split(),
#                     'source': 'PubMed Case Reports'
#                 })
#         logger.info(f"Loaded {len(self.case_studies_db)} case reports")

#     async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
#         extracted_symptoms = input_data.get('extracted_symptoms', [])
#         initial_diagnoses = input_data.get('initial_diagnoses', [])

#         # Simple matching between extracted symptoms and case report symptoms
#         validated_diagnoses = []
#         for diag in initial_diagnoses:
#             cond_lower = diag['condition'].lower()
#             related_cases = [case for case in self.case_studies_db if cond_lower in case['symptoms']]
#             validation_score = min(1.0, len(related_cases) / 10)
#             confidence = (diag.get('confidence', 0.5) + validation_score) / 2
#             validated_diagnoses.append({
#                 **diag,
#                 'confidence': confidence,
#                 'supporting_cases_count': len(related_cases),
#             })

#         # Reduce to top 5 relevant case studies for output
#         top_cases = self.case_studies_db[:5]

#         # return {
#         #     'validated_diagnoses': validated_diagnoses,
#         #     'case_studies': top_cases,
#         #     'metadata': {
#         #         'agent': self.name,
#         #         'version': self.version,
#         #         'timestamp': datetime.now().isoformat()
#         #     }
#         # }
     
   
        
#         return {
#             'validated_diagnoses': validated_diagnoses,
#             'case_studies': [
#                 {
#                     'case_title': cs['case_title'],
#                     'case_abstract': cs['case_abstract'],
#                     'case_url': cs['case_url'],  # ensure URL included here
#                     'similarity_score': cs.get('similarity_score'),
#                     'extracted_symptoms': cs.get('extracted_symptoms', []),
#                     'source': cs.get('source', 'Unknown')
#                 }
#                 for cs in top_cases  # your filtered top cases list
#             ],
#             'metadata': {
#                 'agent': self.name,
#                 'version': self.version,
#                 'timestamp': datetime.now().isoformat()
#             }
#         }


#     async def cleanup(self) -> None:
#         if self.session:
#             await self.session.close()

# # Sample runnable code to test the agent

# async def main():
#     agent = CaseStudyAgent()
#     await agent._load_models()

#     test_input = {
#         'extracted_symptoms': [{'name': 'fever'}, {'name': 'cough'}, {'name': 'fatigue'}],
#         'initial_diagnoses': [{'condition': 'Influenza', 'confidence': 0.7}, {'condition': 'Common Cold', 'confidence': 0.6}]
#     }

#     await agent._load_data([diag['condition'] for diag in test_input['initial_diagnoses']])
#     output = await agent.process(test_input)
#     print("Validated Diagnoses Output:")
#     for vd in output['validated_diagnoses']:
#         print(vd)
#     print(f"Loaded {len(output['case_studies'])} case studies")

#     await agent.cleanup()

# if __name__ == "__main__":
#     asyncio.run(main())








import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
import aiohttp
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaseStudyAgent:
    """Agent for validating diagnoses using PubMed clinical case reports."""

    def __init__(self):
        self.name = "CaseStudyAgent"
        self.version = "1.0.0"
        self.session = None
        self.case_studies_db = []

    async def _load_models(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            headers={'User-Agent': 'Diagnosure-Medical-AI/1.0'}
        )
        logger.info("HTTP session initialized for PubMed queries")

    def _generate_case_study_summary(self, case_studies: List[Dict[str, Any]], validated_diagnoses: List[Dict[str, Any]], top_diagnosis: str) -> str:
        """Generate a summarized case study review with validation"""
        if not case_studies:
            return f"No case studies found to validate the diagnosis of {top_diagnosis}. Recommend searching additional medical case report databases for clinical validation."
        
        summary_parts = []
        
        # Add validation header
        summary_parts.append(f"Case Study Validation for {top_diagnosis}:")
        
        # Analyze case studies
        relevant_cases = []
        for case in case_studies[:5]:  # Top 5 cases
            if top_diagnosis.lower() in case.get('case_title', '').lower() or \
               top_diagnosis.lower() in case.get('case_abstract', '').lower():
                relevant_cases.append(case)
        
        if relevant_cases:
            summary_parts.append(f"\nRelevant Clinical Cases ({len(relevant_cases)} cases):")
            for i, case in enumerate(relevant_cases, 1):
                title = case.get('case_title', 'Unknown case')
                url = case.get('case_url', '')
                abstract = case.get('case_abstract', '')
                
                if url:
                    summary_parts.append(f"• Case {i}: {title} - {url}")
                else:
                    summary_parts.append(f"• Case {i}: {title}")
                
                # Extract key clinical insights from abstract
                if abstract:
                    # Look for key clinical terms in abstract
                    clinical_terms = ['treatment', 'outcome', 'therapy', 'response', 'recovery', 'complications']
                    found_terms = [term for term in clinical_terms if term in abstract.lower()]
                    if found_terms:
                        summary_parts.append(f"  Clinical insights: {', '.join(found_terms[:3])} mentioned")
                    
                    # Extract outcome information if available
                    if 'successful' in abstract.lower() or 'recovered' in abstract.lower():
                        summary_parts.append(f"  Outcome: Positive treatment response reported")
                    elif 'complications' in abstract.lower() or 'adverse' in abstract.lower():
                        summary_parts.append(f"  Outcome: Complications noted")
        else:
            summary_parts.append(f"\nNo directly relevant cases found for {top_diagnosis}")
            summary_parts.append(f"Available cases ({len(case_studies)} total) may provide indirect clinical insights:")
            for i, case in enumerate(case_studies[:2], 1):
                title = case.get('case_title', 'Unknown case')
                url = case.get('case_url', '')
                if url:
                    summary_parts.append(f"• Related case {i}: {title} - {url}")
                else:
                    summary_parts.append(f"• Related case {i}: {title}")
        
        # Validation assessment based on case study support
        if validated_diagnoses:
            top_validated = max(validated_diagnoses, key=lambda x: x.get('confidence', 0))
            supporting_cases = top_validated.get('supporting_cases_count', 0)
            
            summary_parts.append(f"\nCase Study Validation Assessment:")
            if supporting_cases >= 3:
                summary_parts.append(f"STRONG VALIDATION - {supporting_cases} supporting cases found")
                summary_parts.append("Multiple clinical cases demonstrate similar presentations and outcomes")
            elif supporting_cases >= 1:
                summary_parts.append(f"MODERATE VALIDATION - {supporting_cases} supporting case(s) found")
                summary_parts.append("Limited but relevant clinical evidence supports this diagnosis")
            else:
                summary_parts.append("WEAK VALIDATION - No directly supporting cases found")
                summary_parts.append("Consider consulting additional case report databases")
        
        # Clinical recommendations based on case studies
        summary_parts.append(f"\nClinical Insights from Case Studies:")
        if len(case_studies) >= 3:
            summary_parts.append("• Multiple case presentations available for reference")
            summary_parts.append("• Review individual cases for treatment approaches and outcomes")
        else:
            summary_parts.append("• Limited case study evidence available")
            summary_parts.append("• Consider expanding search to include related conditions")
        
        summary_parts.append("• Recommend clinical correlation with patient presentation")
        summary_parts.append("• Consider consulting recent medical literature for additional cases")
        
        return "\n".join(summary_parts)

    async def _search_pubmed_case_reports(self, condition: str, max_results: int = 20) -> List[Dict[str, Any]]:
        esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

        params_search = {
            'db': 'pubmed',
            'term': f'{condition} AND "Case Reports"[Publication Type]',
            'retmax': str(max_results),
            'retmode': 'json'
        }

        async with self.session.get(esearch_url, params=params_search) as resp:
            if resp.status != 200:
                logger.error(f"PubMed esearch failed for {condition} status {resp.status}")
                return []
            search_data = await resp.json()
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return []

        params_fetch = {
            'db': 'pubmed',
            'id': ",".join(id_list),
            'retmode': 'xml'
        }

        async with self.session.get(efetch_url, params=params_fetch) as resp:
            if resp.status != 200:
                logger.error(f"PubMed efetch failed for {condition} status {resp.status}")
                return []
            xml_text = await resp.text()

        articles = []
        try:
            root = ET.fromstring(xml_text)
            for article in root.findall(".//PubmedArticle"):
                title = article.findtext(".//ArticleTitle", default="No title")
                abstract = article.findtext(".//Abstract/AbstractText", default="No abstract")
                pmid = article.findtext(".//PMID")
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                authors = []
                for author in article.findall(".//Author"):
                    lastname = author.findtext("LastName")
                    firstname = author.findtext("ForeName")
                    if lastname and firstname:
                        authors.append(f"{lastname}, {firstname}")
                articles.append({
                    'source': 'PubMed',
                    'pmid': pmid or '',
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'url': url
                })
        except Exception as e:
            logger.error(f"Failed to parse PubMed XML: {e}")
            return []

        return articles

    async def _load_data(self, conditions: List[str]) -> None:
        self.case_studies_db = []
        seen_pmids = set()
        for condition in conditions:
            logger.info(f"Searching PubMed for case reports on condition: {condition}")
            articles = await self._search_pubmed_case_reports(condition)
            for article in articles:
                if article.get('pmid') and article['pmid'] in seen_pmids:
                    continue
                if article.get('pmid'):
                    seen_pmids.add(article['pmid'])
                self.case_studies_db.append({
                    'case_title': article['title'],
                    'case_abstract': article.get('abstract', ''),
                    'case_url': article['url'],
                    'pmid': article.get('pmid', ''),
                    'condition': condition,
                    'symptoms': [],
                    'source': 'PubMed Case Reports'
                })
        logger.info(f"Loaded {len(self.case_studies_db)} case reports")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        extracted_symptoms = input_data.get('extracted_symptoms', [])
        initial_diagnoses = input_data.get('initial_diagnoses', [])

        symptom_terms = {
            str(item.get('name', item.get('symptom', ''))).lower()
            for item in extracted_symptoms if isinstance(item, dict)
        }
        for case in self.case_studies_db:
            text = f"{case.get('condition', '')} {case.get('case_title', '')} {case.get('case_abstract', '')}".lower()
            matches = sum(1 for term in symptom_terms if term and term in text)
            case['similarity_score'] = round(
                min(1.0, 0.7 * (1.0 if case.get('condition', '').lower() in text else 0.0)
                    + 0.3 * (matches / max(len(symptom_terms), 1))), 3
            )
        self.case_studies_db.sort(
            key=lambda case: (-case.get('similarity_score', 0.0), case.get('pmid', ''))
        )

        validated_diagnoses = []
        for diag in initial_diagnoses:
            cond_lower = diag.get('condition', '').lower()
            related_cases = [
                case for case in self.case_studies_db
                if cond_lower in (
                    f"{case.get('condition', '')} {case.get('case_title', '')} "
                    f"{case.get('case_abstract', '')}"
                ).lower()
            ]
            validated_diagnoses.append({
                **diag,
                'case_relevance_score': max(
                    (case.get('similarity_score', 0.0) for case in related_cases),
                    default=0.0,
                ),
                'supporting_cases_count': len(related_cases),
            })

        # Reduce to top 5 relevant case studies for output
        top_cases = self.case_studies_db[:5]
        
        # Get top diagnosis for summary
        top_diagnosis = max(validated_diagnoses, key=lambda x: x.get('confidence', 0)) if validated_diagnoses else {'condition': 'Unknown'}
        case_study_summary = self._generate_case_study_summary(top_cases, validated_diagnoses, top_diagnosis['condition'])
        
        return {
            'validated_diagnoses': validated_diagnoses,
            'case_studies': [
                {
                    'case_title': cs['case_title'],
                    # 'case_abstract': cs['case_abstract'],
                    'case_url': cs['case_url'],
                    'pmid': cs.get('pmid', ''),
                    'case_abstract': cs.get('case_abstract', ''),
                    'similarity_score': cs.get('similarity_score'),
                    'extracted_symptoms': cs.get('extracted_symptoms', []),
                    'source': cs.get('source', 'Unknown')
                }
                for cs in top_cases
            ],
            # 'case_study_summary': case_study_summary,
            # 'metadata': {
            #     'agent': self.name,
            #     'version': self.version,
            #     'timestamp': datetime.now().isoformat()
        }
    

    async def cleanup(self) -> None:
        if self.session:
            await self.session.close()

# Sample runnable code to test the agent
async def main():
    agent = CaseStudyAgent()
    await agent._load_models()

    test_input = {
        'extracted_symptoms': [{'name': 'fever'}, {'name': 'cough'}, {'name': 'fatigue'}],
        'initial_diagnoses': [{'condition': 'Influenza', 'confidence': 0.7}, {'condition': 'Common Cold', 'confidence': 0.6}]
    }

    await agent._load_data([diag['condition'] for diag in test_input['initial_diagnoses']])
    output = await agent.process(test_input)
    print("Case Study Summary:")
    print(output['case_study_summary'])
    print(f"\nLoaded {len(output['case_studies'])} case studies")

    await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())