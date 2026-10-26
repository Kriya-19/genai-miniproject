# import asyncio
# import aiohttp
# import xml.etree.ElementTree as ET
# from typing import Dict, List, Any
# from datetime import datetime, timedelta
# import logging

# logger = logging.getLogger(__name__)

# class LiteratureAgent:
#     """Agent for searching medical literature and validating diagnoses"""

#     def __init__(self):
#         self.name = "LiteratureAgent"
#         self.version = "1.0.1"
#         self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
#         self.clinical_trials_url = "https://clinicaltrials.gov/api/v2/"
#         self.search_cache = {}
#         self.session = None

#     async def _load_models(self) -> None:
#         """Initialize HTTP session for API calls"""
#         try:
#             self.session = aiohttp.ClientSession(
#                 timeout=aiohttp.ClientTimeout(total=30),
#                 headers={
#                     'User-Agent': 'Diagnosure-Medical-AI/1.0'
#                 }
#             )
#             logger.info("HTTP session initialized for literature search")
#         except Exception as e:
#             logger.error(f"Failed to initialize HTTP session: {str(e)}")
#             raise

#     async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Search literature and validate diagnoses using public APIs"""
#         initial_diagnoses = input_data.get('initial_diagnoses', [])
#         extracted_symptoms = input_data.get('extracted_symptoms', [])

#         literature_evidence = []
#         # Search literature for each diagnosis
#         for diagnosis in initial_diagnoses:
#             condition_name = diagnosis['condition']
#             # Search PubMed
#             pubmed_results = await self._search_pubmed(condition_name, extracted_symptoms)
#             literature_evidence.extend(pubmed_results)
#             # Search Clinical Trials
#             clinical_results = await self._search_clinical_trials(condition_name, extracted_symptoms)
#             literature_evidence.extend(clinical_results)

#         # Validate diagnoses against literature
#         validated_diagnoses = await self._validate_diagnoses_with_literature(
#             initial_diagnoses, literature_evidence
#         )

#         # return {
#         #     'literature_evidence': literature_evidence,
#         #     'validated_diagnoses': validated_diagnoses,
#         #     'validation_metadata': {
#         #         'total_articles_found': len(literature_evidence),
#         #         'sources_searched': ['PubMed', 'ClinicalTrials.gov'],
#         #         'agent_name': self.name,
#         #         'version': self.version,
#         #         'timestamp': datetime.now().isoformat()
#         #     }
#         # }
        
#         return {
#             'literature_evidence': [
#                 {
#                     'title': lit['title'],
#                     'url': lit.get('url', ''),
#                     'source': lit.get('source', 'Unknown'),
#                     'abstract': lit.get('abstract', ''),
#                     'relevance_score': lit.get('relevance_score'),
#                     'keywords': lit.get('keywords', [])
#                 }
#                 for lit in literature_evidence  # your literature list variable
#             ],
#             'validated_diagnoses': validated_diagnoses,
#             'validation_metadata': {
#                 'total_articles_found': len(literature_evidence),
#                 'sources_searched': ['PubMed', 'ClinicalTrials.gov'],
#                 'agent_name': self.name,
#                 'version': self.version,
#                 'timestamp': datetime.now().isoformat()
#             }
#         }

#     async def _search_pubmed(self, condition: str, symptoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Search PubMed for relevant literature"""
#         try:
#             search_terms = [condition] + [symptom['name'] for symptom in symptoms[:3]]
#             query = " AND ".join(search_terms)
#             cache_key = f"{condition}_pubmed"
#             if cache_key in self.search_cache:
#                 cached_data = self.search_cache[cache_key]
#                 if datetime.now() - cached_data['timestamp'] < timedelta(hours=6):
#                     logger.info(f"Using cached PubMed results for {condition}")
#                     return [cached_data['evidence']]

#             search_url = f"{self.pubmed_base_url}esearch.fcgi"
#             params = {
#                 'db': 'pubmed',
#                 'term': query,
#                 'retmax': 10,
#                 'retmode': 'json',
#                 'sort': 'relevance'
#             }
#             async with self.session.get(search_url, params=params) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     pmids = data.get('esearchresult', {}).get('idlist', [])
#                     if pmids:
#                         articles = await self._fetch_pubmed_articles(pmids)
#                         for article in articles:
#                             self.search_cache[cache_key] = {'evidence': article, 'timestamp': datetime.now()}
#                         return articles
#             return []
#         except Exception as e:
#             logger.error(f"PubMed search failed for {condition}: {str(e)}")
#             return []

#     async def _fetch_pubmed_articles(self, pmids: List[str]) -> List[Dict[str, Any]]:
#         """Fetch detailed article info from PubMed by PMIDs"""
#         try:
#             fetch_url = f"{self.pubmed_base_url}efetch.fcgi"
#             params = {
#                 'db': 'pubmed',
#                 'id': ','.join(pmids),
#                 'retmode': 'xml'
#             }
#             async with self.session.get(fetch_url, params=params) as response:
#                 if response.status == 200:
#                     xml_content = await response.text()
#                     return self._parse_pubmed_xml(xml_content)
#             return []
#         except Exception as e:
#             logger.error(f"Failed to fetch PubMed articles: {str(e)}")
#             return []

#     def _parse_pubmed_xml(self, xml_content: str) -> List[Dict[str, Any]]:
#         """Parse PubMed XML response"""
#         articles = []
#         try:
#             root = ET.fromstring(xml_content)
#             for article in root.findall('.//PubmedArticle'):
#                 title = article.findtext('.//ArticleTitle', default="No title")
#                 authors = []
#                 for author in article.findall('.//Author'):
#                     last_name = author.find('LastName')
#                     first_name = author.find('ForeName')
#                     name = ''
#                     if last_name is not None:
#                         name = last_name.text
#                     if first_name is not None:
#                         name += f", {first_name.text}"
#                     if name:
#                         authors.append(name)
#                 abstract = article.findtext('.//Abstract/AbstractText', default="No abstract")
#                 year = article.findtext('.//PubDate/Year')
#                 year = int(year) if year and year.isdigit() else datetime.now().year
#                 pmid = article.findtext('.//PMID', default="")
#                 articles.append({
#                     'source': 'PubMed',
#                     'title': title,
#                     'authors': authors,
#                     'year': year,
#                     'abstract': abstract,
#                     'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
#                     'relevance_score': self._calculate_relevance_score(title, abstract),
#                     'keywords': self._extract_keywords(title, abstract)
#                 })
#         except Exception as e:
#             logger.error(f"Failed to parse PubMed XML: {str(e)}")
#         return articles

#     async def _search_clinical_trials(self, condition: str, symptoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Search ClinicalTrials.gov for relevant studies"""
#         try:
#             search_terms = [condition] + [symptom['name'] for symptom in symptoms[:2]]
#             query = " ".join(search_terms)
#             cache_key = f"{condition}_clinical_trials"
#             if cache_key in self.search_cache:
#                 cached_data = self.search_cache[cache_key]
#                 if datetime.now() - cached_data['timestamp'] < timedelta(hours=6):
#                     logger.info(f"Using cached ClinicalTrials.gov results for {condition}")
#                     return [cached_data['evidence']]

#             search_url = f"https://clinicaltrials.gov/api/query/study_fields?"
#             params = {
#                 'expr': query,
#                 'fields': 'NCTId,BriefTitle,Condition,BriefSummary,OverallStatus',
#                 'max_rnk': 5,
#                 'fmt': 'json'
#             }
#             async with self.session.get(search_url, params=params) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     studies = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
#                     articles = []
#                     for study in studies:
#                         title_list = study.get('BriefTitle', [])
#                         description_list = study.get('BriefSummary', [])
#                         nct_ids = study.get('NCTId', [])
#                         title = title_list[0] if title_list else "No title"
#                         description = description_list[0] if description_list else "No description"
#                         nct_id = nct_ids[0] if nct_ids else ""
#                         articles.append({
#                             'source': 'ClinicalTrials.gov',
#                             'title': title,
#                             'authors': ['Clinical Trial'],
#                             'year': datetime.now().year,
#                             'abstract': description,
#                             'url': f"https://clinicaltrials.gov/ct2/show/{nct_id}",
#                             'relevance_score': self._calculate_relevance_score(title, description),
#                             'keywords': self._extract_keywords(title, description)
#                         })
#                     for article in articles:
#                         self.search_cache[cache_key] = {'evidence': article, 'timestamp': datetime.now()}
#                     return articles
#             return []
#         except Exception as e:
#             logger.error(f"ClinicalTrials.gov search failed for {condition}: {str(e)}")
#             return []

#     def _calculate_relevance_score(self, title: str, abstract: str) -> float:
#         """Calculate relevance score for literature evidence based on keywords density"""
#         text = f"{title} {abstract}".lower()
#         medical_keywords = [
#             'diagnosis', 'treatment', 'symptoms', 'clinical', 'patient',
#             'therapy', 'medication', 'disease', 'condition', 'medical'
#         ]
#         keyword_count = sum(1 for keyword in medical_keywords if keyword in text)
#         total_words = len(text.split())
#         return min(keyword_count / (total_words / 100), 1.0) if total_words > 0 else 0.0

#     def _extract_keywords(self, title: str, abstract: str) -> List[str]:
#         """Extract relevant medical keywords from title and abstract"""
#         text = f"{title} {abstract}".lower()
#         medical_terms = [
#             'pain', 'fever', 'cough', 'headache', 'nausea', 'fatigue',
#             'inflammation', 'infection', 'chronic', 'acute', 'severe',
#             'mild', 'moderate', 'treatment', 'therapy', 'medication'
#         ]
#         return [term for term in medical_terms if term in text]

#     async def _validate_diagnoses_with_literature(self, diagnoses: List[Dict[str, Any]], literature_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """Validate diagnoses against literature evidence"""
#         validated_diagnoses = []
#         for diagnosis in diagnoses:
#             condition_name = diagnosis['condition']
#             relevant_evidence = [
#                 evidence for evidence in literature_evidence
#                 if condition_name.lower() in evidence['title'].lower() or condition_name.lower() in evidence['abstract'].lower()
#             ]
#             validation_score = self._calculate_validation_score(diagnosis, relevant_evidence)
#             original_confidence = diagnosis.get('confidence', 0.5)
#             validated_confidence = (original_confidence + validation_score) / 2
#             validated_diagnosis = diagnosis.copy()
#             validated_diagnosis['confidence'] = validated_confidence
#             validated_diagnosis['literature_validation_score'] = validation_score
#             validated_diagnosis['supporting_evidence_count'] = len(relevant_evidence)
#             validated_diagnoses.append(validated_diagnosis)
#         validated_diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
#         return validated_diagnoses

#     def _calculate_validation_score(self, diagnosis: Dict[str, Any], evidence: List[Dict[str, Any]]) -> float:
#         """Calculate validation score based on literature evidence"""
#         if not evidence:
#             return 0.5  # Neutral score
#         relevance_scores = [e['relevance_score'] for e in evidence]
#         avg_relevance = sum(relevance_scores) / len(relevance_scores)
#         evidence_weight = min(len(evidence) / 5.0, 1.0)  # capped at 5 articles
#         validation_score = (avg_relevance * 0.7) + (evidence_weight * 0.3)
#         return min(validation_score, 1.0)

#     async def cleanup(self) -> None:
#         """Cleanup resources"""
#         if self.session:
#             await self.session.close()
















import asyncio
import aiohttp
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LiteratureAgent:
    """Agent for searching medical literature and validating diagnoses"""

    def __init__(self):
        self.name = "LiteratureAgent"
        self.version = "1.0.1"
        self.pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.clinical_trials_url = "https://clinicaltrials.gov/api/v2/"
        self.search_cache = {}
        self.session = None

    async def _load_models(self) -> None:
        """Initialize HTTP session for API calls"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Diagnosure-Medical-AI/1.0'
                }
            )
            logger.info("HTTP session initialized for literature search")
        except Exception as e:
            logger.error(f"Failed to initialize HTTP session: {str(e)}")
            raise

    def _generate_literature_summary(self, literature_evidence: List[Dict[str, Any]], top_diagnosis: str) -> str:
        """Generate a summarized literature review with validation"""
        if not literature_evidence:
            return f"No literature evidence found to validate the diagnosis of {top_diagnosis}. Recommend consulting medical databases and recent publications for more comprehensive validation."
        
        # Group by source
        pubmed_articles = [lit for lit in literature_evidence if lit.get('source') == 'PubMed']
        clinical_trials = [lit for lit in literature_evidence if lit.get('source') == 'ClinicalTrials.gov']
        
        summary_parts = []
        
        # Add validation header
        summary_parts.append(f"Literature Validation for {top_diagnosis}:")
        
        # Summarize PubMed findings
        if pubmed_articles:
            summary_parts.append(f"\nPubMed Evidence ({len(pubmed_articles)} studies):")
            for i, article in enumerate(pubmed_articles[:3], 1):
                title = article.get('title', 'Unknown study')
                url = article.get('url', '')
                keywords = article.get('keywords', [])
                relevance = article.get('relevance_score', 0)
                
                if url:
                    summary_parts.append(f"• Study {i}: {title} (Relevance: {relevance:.2f}) - {url}")
                else:
                    summary_parts.append(f"• Study {i}: {title} (Relevance: {relevance:.2f})")
                
                if keywords:
                    summary_parts.append(f"  Key findings: {', '.join(keywords[:4])}")
            
            # Calculate average relevance
            avg_relevance = sum(art.get('relevance_score', 0) for art in pubmed_articles) / len(pubmed_articles)
            if avg_relevance > 0.7:
                summary_parts.append(f"  Validation: HIGH - Strong literature support (avg relevance: {avg_relevance:.2f})")
            elif avg_relevance > 0.4:
                summary_parts.append(f"  Validation: MODERATE - Some literature support (avg relevance: {avg_relevance:.2f})")
            else:
                summary_parts.append(f"  Validation: LOW - Limited literature support (avg relevance: {avg_relevance:.2f})")
        
        # Summarize Clinical Trials
        if clinical_trials:
            summary_parts.append(f"\nClinical Trials Evidence ({len(clinical_trials)} trials):")
            for i, trial in enumerate(clinical_trials[:2], 1):
                title = trial.get('title', 'Unknown trial')
                url = trial.get('url', '')
                
                if url:
                    summary_parts.append(f"• Trial {i}: {title} - {url}")
                else:
                    summary_parts.append(f"• Trial {i}: {title}")
        
        # Overall validation summary
        total_sources = len(literature_evidence)
        high_relevance_count = sum(1 for lit in literature_evidence if lit.get('relevance_score', 0) > 0.6)
        
        summary_parts.append(f"\nOverall Literature Validation:")
        if high_relevance_count >= 2:
            summary_parts.append(f"STRONG VALIDATION - {high_relevance_count}/{total_sources} high-quality sources support this diagnosis")
        elif total_sources >= 2:
            summary_parts.append(f"MODERATE VALIDATION - {total_sources} sources found with mixed relevance")
        else:
            summary_parts.append(f"WEAK VALIDATION - Limited literature evidence ({total_sources} sources)")
        
        return "\n".join(summary_parts)

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search literature and validate diagnoses using public APIs"""
        initial_diagnoses = input_data.get('initial_diagnoses', [])
        extracted_symptoms = input_data.get('extracted_symptoms', [])

        literature_evidence = []
        # Search literature for each diagnosis
        for diagnosis in initial_diagnoses:
            condition_name = diagnosis.get('condition', '').strip()
            if not condition_name:
                continue
            # Search PubMed
            pubmed_results = await self._search_pubmed(condition_name, extracted_symptoms)
            literature_evidence.extend(pubmed_results)
            # Search Clinical Trials
            clinical_results = await self._search_clinical_trials(condition_name, extracted_symptoms)
            literature_evidence.extend(clinical_results)

        # Validate diagnoses against literature
        query_terms = [
            diagnosis.get('condition', '').lower()
            for diagnosis in initial_diagnoses
            if diagnosis.get('condition')
        ] + [
            str(symptom.get('name', symptom.get('symptom', ''))).lower()
            for symptom in extracted_symptoms if isinstance(symptom, dict)
        ]
        for evidence in literature_evidence:
            evidence['relevance_score'] = self._calculate_relevance_score(
                evidence.get('title', ''),
                evidence.get('abstract', ''),
                query_terms,
            )
        validated_diagnoses = await self._validate_diagnoses_with_literature(
            initial_diagnoses, literature_evidence
        )
        
        # Get top diagnosis for summary
        top_diagnosis = max(validated_diagnoses, key=lambda x: x.get('confidence', 0)) if validated_diagnoses else {'condition': 'Unknown'}
        literature_summary = self._generate_literature_summary(literature_evidence, top_diagnosis['condition'])
        
        unique = {}
        for evidence in literature_evidence:
            identifier = evidence.get('pmid') or evidence.get('url') or evidence.get('title')
            if identifier and identifier not in unique:
                unique[identifier] = evidence
        ranked = sorted(
            unique.values(),
            key=lambda item: item.get('relevance_score', 0.0),
            reverse=True,
        )
        return {
            'literature_evidence': [
                {
                    'pmid': lit.get('pmid', ''),
                    'title': lit.get('title', ''),
                    'url': lit.get('url', ''),
                    'source': lit.get('source', 'Unknown'),
                    'abstract': lit.get('abstract', ''),
                    'authors': lit.get('authors', []),
                    'year': lit.get('year'),
                    'relevance_score': lit.get('relevance_score', 0.0),
                    'keywords': lit.get('keywords', [])
                }
                for lit in ranked
            ],
            'validated_diagnoses': validated_diagnoses,
            'validation_metadata': {
                'total_articles_found': len(ranked),
                'sources_searched': ['PubMed', 'ClinicalTrials.gov'],
                'agent_name': self.name,
                'version': self.version,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def _search_pubmed(self, condition: str, symptoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search PubMed for relevant literature"""
        try:
            symptom_names = [
                str(symptom.get('name', symptom.get('symptom', ''))).strip()
                for symptom in symptoms if isinstance(symptom, dict)
            ]
            symptom_names = [name for name in symptom_names if name]
            query = f'"{condition}"[Title/Abstract]'
            if symptom_names:
                query += " AND (" + " OR ".join(
                    f'"{name}"[Title/Abstract]' for name in symptom_names[:5]
                ) + ")"
            cache_key = f"{condition}|{'|'.join(symptom_names[:5])}|pubmed"
            if cache_key in self.search_cache:
                cached_data = self.search_cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < timedelta(hours=6):
                    logger.info(f"Using cached PubMed results for {condition}")
                    return cached_data['evidence']

            search_url = f"{self.pubmed_base_url}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': 10,
                'retmode': 'json',
                'sort': 'relevance'
            }
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pmids = data.get('esearchresult', {}).get('idlist', [])
                    if pmids:
                        articles = await self._fetch_pubmed_articles(pmids)
                        self.search_cache[cache_key] = {
                            'evidence': articles, 'timestamp': datetime.now()
                        }
                        return articles
            return []
        except Exception as e:
            logger.error(f"PubMed search failed for {condition}: {str(e)}")
            return []

    async def _fetch_pubmed_articles(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed article info from PubMed by PMIDs"""
        try:
            fetch_url = f"{self.pubmed_base_url}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml'
            }
            async with self.session.get(fetch_url, params=params) as response:
                if response.status == 200:
                    xml_content = await response.text()
                    return self._parse_pubmed_xml(xml_content)
            return []
        except Exception as e:
            logger.error(f"Failed to fetch PubMed articles: {str(e)}")
            return []

    def _parse_pubmed_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response"""
        articles = []
        try:
            root = ET.fromstring(xml_content)
            for article in root.findall('.//PubmedArticle'):
                title = article.findtext('.//ArticleTitle', default="No title")
                authors = []
                for author in article.findall('.//Author'):
                    last_name = author.find('LastName')
                    first_name = author.find('ForeName')
                    name = ''
                    if last_name is not None:
                        name = last_name.text
                    if first_name is not None:
                        name += f", {first_name.text}"
                    if name:
                        authors.append(name)
                abstract = article.findtext('.//Abstract/AbstractText', default="No abstract")
                year = article.findtext('.//PubDate/Year')
                year = int(year) if year and year.isdigit() else datetime.now().year
                pmid = article.findtext('.//PMID', default="")
                articles.append({
                    'source': 'PubMed',
                    'pmid': pmid,
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'abstract': abstract,
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'relevance_score': self._calculate_relevance_score(title, abstract),
                    'keywords': self._extract_keywords(title, abstract)
                })
        except Exception as e:
            logger.error(f"Failed to parse PubMed XML: {str(e)}")
        return articles

    async def _search_clinical_trials(self, condition: str, symptoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search ClinicalTrials.gov for relevant studies"""
        try:
            search_terms = [condition] + [
                str(symptom.get('name', symptom.get('symptom', '')))
                for symptom in symptoms[:2] if isinstance(symptom, dict)
            ]
            query = " ".join(search_terms)
            cache_key = f"{condition}_clinical_trials"
            if cache_key in self.search_cache:
                cached_data = self.search_cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < timedelta(hours=6):
                    logger.info(f"Using cached ClinicalTrials.gov results for {condition}")
                    return [cached_data['evidence']]

            search_url = f"https://clinicaltrials.gov/api/query/study_fields?"
            params = {
                'expr': query,
                'fields': 'NCTId,BriefTitle,Condition,BriefSummary,OverallStatus',
                'max_rnk': 5,
                'fmt': 'json'
            }
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    studies = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
                    articles = []
                    for study in studies:
                        title_list = study.get('BriefTitle', [])
                        description_list = study.get('BriefSummary', [])
                        nct_ids = study.get('NCTId', [])
                        title = title_list[0] if title_list else "No title"
                        description = description_list[0] if description_list else "No description"
                        nct_id = nct_ids[0] if nct_ids else ""
                        articles.append({
                            'source': 'ClinicalTrials.gov',
                            'title': title,
                            'authors': ['Clinical Trial'],
                            'year': datetime.now().year,
                            'abstract': description,
                            'url': f"https://clinicaltrials.gov/ct2/show/{nct_id}",
                            'relevance_score': self._calculate_relevance_score(title, description),
                            'keywords': self._extract_keywords(title, description)
                        })
                    for article in articles:
                        self.search_cache[cache_key] = {'evidence': article, 'timestamp': datetime.now()}
                    return articles
            return []
        except Exception as e:
            logger.error(f"ClinicalTrials.gov search failed for {condition}: {str(e)}")
            return []

    def _calculate_relevance_score(
        self, title: str, abstract: str, query_terms: Optional[List[str]] = None
    ) -> float:
        """Score overlap with the current query; this is not clinical evidence strength."""
        text = f"{title} {abstract}".lower()
        if query_terms:
            terms = [term.strip().lower() for term in query_terms if term.strip()]
            if terms:
                title_text = title.lower()
                matches = sum(1 for term in terms if term in text)
                title_matches = sum(1 for term in terms if term in title_text)
                return round(min(1.0, (matches / len(terms)) * 0.7 + (title_matches / len(terms)) * 0.3), 3)
        medical_keywords = [
            'diagnosis', 'treatment', 'symptoms', 'clinical', 'patient',
            'therapy', 'medication', 'disease', 'condition', 'medical'
        ]
        keyword_count = sum(1 for keyword in medical_keywords if keyword in text)
        total_words = len(text.split())
        return min(keyword_count / (total_words / 100), 1.0) if total_words > 0 else 0.0

    def _extract_keywords(self, title: str, abstract: str) -> List[str]:
        """Extract relevant medical keywords from title and abstract"""
        text = f"{title} {abstract}".lower()
        medical_terms = [
            'pain', 'fever', 'cough', 'headache', 'nausea', 'fatigue',
            'inflammation', 'infection', 'chronic', 'acute', 'severe',
            'mild', 'moderate', 'treatment', 'therapy', 'medication'
        ]
        return [term for term in medical_terms if term in text]

    async def _validate_diagnoses_with_literature(self, diagnoses: List[Dict[str, Any]], literature_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate diagnoses against literature evidence"""
        validated_diagnoses = []
        for diagnosis in diagnoses:
            condition_name = diagnosis['condition']
            relevant_evidence = [
                evidence for evidence in literature_evidence
                if condition_name.lower() in evidence['title'].lower() or condition_name.lower() in evidence['abstract'].lower()
            ]
            validation_score = self._calculate_validation_score(diagnosis, relevant_evidence)
            original_confidence = diagnosis.get('confidence', 0.5)
            validated_confidence = (original_confidence + validation_score) / 2
            validated_diagnosis = diagnosis.copy()
            validated_diagnosis['confidence'] = validated_confidence
            validated_diagnosis['literature_validation_score'] = validation_score
            validated_diagnosis['supporting_evidence_count'] = len(relevant_evidence)
            validated_diagnoses.append(validated_diagnosis)
        validated_diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
        return validated_diagnoses

    def _calculate_validation_score(self, diagnosis: Dict[str, Any], evidence: List[Dict[str, Any]]) -> float:
        """Calculate validation score based on literature evidence"""
        if not evidence:
            return 0.5  # Neutral score
        relevance_scores = [e['relevance_score'] for e in evidence]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        evidence_weight = min(len(evidence) / 5.0, 1.0)  # capped at 5 articles
        validation_score = (avg_relevance * 0.7) + (evidence_weight * 0.3)
        return min(validation_score, 1.0)

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.session:
            await self.session.close()