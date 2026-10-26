# # import logging
# # import aiohttp
# # import asyncio
# # import numpy as np
# # from sklearn.feature_extraction.text import TfidfVectorizer
# # from sklearn.ensemble import RandomForestClassifier
# # from typing import List, Dict, Any
# # from datetime import datetime

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger("DiagnosisAgentStandalone")

# # class DiagnosisAgent:
# #     # Paste your actual free DxGPT API key here (replace sample)
# #     DXGPT_API_KEY = os.getenv("DXGPT_API_KEY", "")

# #     def __init__(self):
# #         self.conditions_db = self._load_sample_conditions()
# #         self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1,2))
# #         self.classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
# #         self._train_dummy_classifier()

# #     def _load_sample_conditions(self) -> Dict[str, Any]:
# #         return {
# #             "Common Cold": {
# #                 "symptoms": ["cough", "sore throat", "runny nose", "fever"],
# #                 "icd10_code": "J00",
# #                 "description": "Viral infection in nose and throat",
# #                 "treatments": ["rest", "fluids"],
# #                 "medications": [],
# #             },
# #             "Influenza": {
# #                 "symptoms": ["fever", "cough", "body ache", "chills", "fatigue"],
# #                 "icd10_code": "J11",
# #                 "description": "Flu virus infection",
# #                 "treatments": ["rest", "hydration"],
# #                 "medications": ["antiviral drugs"],
# #             },
# #             "COVID-19": {
# #                 "symptoms": ["fever", "dry cough", "tiredness", "loss of taste", "loss of smell"],
# #                 "icd10_code": "U07.1",
# #                 "description": "Infectious respiratory disease caused by coronavirus",
# #                 "treatments": ["isolation", "supportive care"],
# #                 "medications": [],
# #             },
# #         }

# #     def _train_dummy_classifier(self):
# #         disease_names = list(self.conditions_db.keys())
# #         text_data = [" ".join(self.conditions_db[d]["symptoms"]) for d in disease_names]
# #         X = self.vectorizer.fit_transform(text_data)
# #         y = list(range(len(disease_names)))
# #         self.classifier.fit(X, y)
# #         self.num_to_disease = {i: d for i, d in enumerate(disease_names)}

# #     async def convert_input_to_clinical_text(self, input_data: Dict[str, Any]) -> str:
# #         symptoms = input_data.get('symptoms', [])
# #         demographics = input_data.get('demographics', {})
# #         allergies = input_data.get('allergies', [])
# #         past_diseases = input_data.get('past_diseases', [])
# #         medications = input_data.get('medications', [])

# #         desc_parts = []
# #         if demographics:
# #             age = demographics.get('age', '')
# #             gender = demographics.get('gender', '')
# #             height = demographics.get('height', '')
# #             weight = demographics.get('weight', '')
# #             desc_parts.append(f"Patient is a {age}-year-old {gender} with height {height} cm and weight {weight} kg.")

# #         if symptoms:
# #             symptom_descs = []
# #             for sym in symptoms:
# #                 s = sym.get('symptom', '')
# #                 severity = sym.get('severity')
# #                 if severity:
# #                     symptom_descs.append(f"{s} (severity: {severity})")
# #                 else:
# #                     symptom_descs.append(s)
# #             desc_parts.append("Symptoms reported: " + ", ".join(symptom_descs) + ".")

# #         if allergies and allergies != ['no']:
# #             desc_parts.append("Allergies: " + ", ".join(allergies) + ".")
# #         else:
# #             desc_parts.append("No known allergies.")

# #         if past_diseases and past_diseases != ['no']:
# #             desc_parts.append("Past diseases include: " + ", ".join(past_diseases) + ".")
# #         else:
# #             desc_parts.append("No significant past diseases.")

# #         if medications and medications != ['no']:
# #             desc_parts.append("Current medications: " + ", ".join(medications) + ".")
# #         else:
# #             desc_parts.append("No current medications.")

# #         return " ".join(desc_parts)

# #     async def call_dxgpt_api(self, clinical_text: str) -> List[Dict[str, Any]]:
# #         if not self.DXGPT_API_KEY or self.DXGPT_API_KEY == "your_free_dxgpt_api_key_here":
# #             logger.warning("DxGPT API key not provided or default. Skipping API call.")
# #             return []

# #         url = "https://api.dxgpt.app/api/diagnose"
# #         headers = {
# #             "Authorization": f"Bearer {self.DXGPT_API_KEY}",
# #             "Content-Type": "application/json"
# #         }
# #         payload = {
# #             "description": clinical_text,
# #             "model": "gpt4o",
# #             "request_id": f"req-{int(datetime.now().timestamp())}",
# #             "timezone": "UTC"
# #         }
# #         try:
# #             async with aiohttp.ClientSession() as session:
# #                 async with session.post(url, headers=headers, json=payload) as resp:
# #                     if resp.status != 200:
# #                         text = await resp.text()
# #                         logger.error(f"DxGPT API error: {resp.status} - {text}")
# #                         return []
# #                     data = await resp.json()
# #                     diagnoses = data.get("diagnoses", [])
# #                     top5 = diagnoses[:5]
# #                     results = []
# #                     for d in top5:
# #                         results.append({
# #                             "condition": d.get("condition", "Unknown"),
# #                             "confidence": d.get("confidence", 0.0),
# #                             "icd10code": d.get("icd10_code", ""),
# #                             "treatments": d.get("treatments", []),
# #                             "medications": d.get("medications", [])
# #                         })
# #                     return results
# #         except Exception as e:
# #             logger.error(f"DxGPT API call exception: {e}")
# #             return []

# #     def diagnose_with_local_db(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
# #         input_symptom_names = {s.get('symptom', '').lower() for s in input_data.get('symptoms', [])}

# #         diagnoses = []
# #         for disease, data in self.conditions_db.items():
# #             disease_symptoms = set([sym.lower() for sym in data.get('symptoms', [])])
# #             matched = input_symptom_names.intersection(disease_symptoms)
# #             if matched:
# #                 confidence = len(matched) / max(len(disease_symptoms), len(input_symptom_names))
# #                 diagnoses.append({
# #                     "condition": disease,
# #                     "confidence": round(confidence, 2),
# #                     "icd10code": data.get("icd10_code", ""),
# #                     "treatments": data.get("treatments", []),
# #                     "medications": data.get("medications", []),
# #                 })
# #         diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
# #         return diagnoses[:5]

# #     async def diagnose(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
# #         clinical_text = await self.convert_input_to_clinical_text(input_data)
# #         results = await self.call_dxgpt_api(clinical_text)
# #         if results:
# #             return results
# #         logger.info("Using local database fallback diagnosis")
# #         return self.diagnose_with_local_db(input_data)

# # if __name__ == "__main__":
# #     agent = DiagnosisAgent()
# #     sample_input = {
# #         'symptoms': [
# #             {'symptom': 'cough', 'severity': None, 'confidence_score': 1.0, 'entity_type': 'Sign_symptom', 'position': {'start': 27, 'end': 32}},
# #             {'symptom': 'fever', 'severity': 'high', 'confidence_score': 0.98, 'entity_type': 'Modified_symptom', 'position': {'start': 17, 'end': 22}},
# #         ],
# #         'demographics': {'age': '20', 'gender': 'male', 'height': '150', 'weight': '70'},
# #         'allergies': ['no'],
# #         'past_diseases': ['no'],
# #         'medications': ['no']
# #     }

# #     async def run():
# #         diagnoses = await agent.diagnose(sample_input)
# #         print("Top 5 Diagnoses:")
# #         for d in diagnoses:
# #             print(f"Condition: {d['condition']}, Confidence: {d['confidence']}, ICD10: {d['icd10code']}")

# #     asyncio.run(run())











# # import logging
# # import aiohttp
# # import asyncio
# # import uuid
# # import numpy as np
# # from sklearn.feature_extraction.text import TfidfVectorizer
# # from sklearn.ensemble import RandomForestClassifier
# # from typing import List, Dict, Any
# # from datetime import datetime

# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger("DiagnosisAgentStandalone")

# # class DiagnosisAgent:
# #     # Paste your DxGPT subscription key here (replace with your actual key)
# #     DXGPT_API_KEY = os.getenv("DXGPT_API_KEY", "")

# #     def __init__(self):
# #         self.conditions_db = self._load_sample_conditions()
# #         self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
# #         self.classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
# #         self._train_dummy_classifier()

# #     def _load_sample_conditions(self) -> Dict[str, Any]:
# #         return {
# #             "Common Cold": {
# #                 "symptoms": ["cough", "sore throat", "runny nose", "fever"],
# #                 "icd10_code": "J00",
# #                 "description": "Viral infection in nose and throat",
# #                 "treatments": ["rest", "fluids"],
# #                 "medications": [],
# #             },
# #             "Influenza": {
# #                 "symptoms": ["fever", "cough", "body ache", "chills", "fatigue"],
# #                 "icd10_code": "J11",
# #                 "description": "Flu virus infection",
# #                 "treatments": ["rest", "hydration"],
# #                 "medications": ["antiviral drugs"],
# #             },
# #             "COVID-19": {
# #                 "symptoms": ["fever", "dry cough", "tiredness", "loss of taste", "loss of smell"],
# #                 "icd10_code": "U07.1",
# #                 "description": "Infectious respiratory disease caused by coronavirus",
# #                 "treatments": ["isolation", "supportive care"],
# #                 "medications": [],
# #             },
# #         }

# #     def _train_dummy_classifier(self):
# #         disease_names = list(self.conditions_db.keys())
# #         text_data = [" ".join(self.conditions_db[d]["symptoms"]) for d in disease_names]
# #         X = self.vectorizer.fit_transform(text_data)
# #         y = list(range(len(disease_names)))
# #         self.classifier.fit(X, y)
# #         self.num_to_disease = {i: d for i, d in enumerate(disease_names)}

# #     async def convert_input_to_clinical_text(self, input_data: Dict[str, Any]) -> str:
# #         symptoms = input_data.get('symptoms', [])
# #         demographics = input_data.get('demographics', {})
# #         allergies = input_data.get('allergies', [])
# #         past_diseases = input_data.get('past_diseases', [])
# #         medications = input_data.get('medications', [])

# #         desc_parts = []
# #         if demographics:
# #             age = demographics.get('age', '')
# #             gender = demographics.get('gender', '')
# #             height = demographics.get('height', '')
# #             weight = demographics.get('weight', '')
# #             desc_parts.append(f"Patient is a {age}-year-old {gender} with height {height} cm and weight {weight} kg.")

# #         if symptoms:
# #             symptom_descs = []
# #             for sym in symptoms:
# #                 s = sym.get('symptom', '')
# #                 severity = sym.get('severity')
# #                 if severity:
# #                     symptom_descs.append(f"{s} (severity: {severity})")
# #                 else:
# #                     symptom_descs.append(s)
# #             desc_parts.append("Symptoms reported: " + ", ".join(symptom_descs) + ".")

# #         if allergies and allergies != ['no']:
# #             desc_parts.append("Allergies: " + ", ".join(allergies) + ".")
# #         else:
# #             desc_parts.append("No known allergies.")

# #         if past_diseases and past_diseases != ['no']:
# #             desc_parts.append("Past diseases include: " + ", ".join(past_diseases) + ".")
# #         else:
# #             desc_parts.append("No significant past diseases.")

# #         if medications and medications != ['no']:
# #             desc_parts.append("Current medications: " + ", ".join(medications) + ".")
# #         else:
# #             desc_parts.append("No current medications.")

# #         return " ".join(desc_parts)

# #     async def call_dxgpt_api(self, clinical_text: str) -> List[Dict[str, Any]]:
# #         if not self.DXGPT_API_KEY or self.DXGPT_API_KEY == "your_subscription_key_here":
# #             logger.warning("DxGPT API key not provided or default placeholder.")
# #             return []

# #         url = "https://dxgpt-apim.azure-api.net/api/diagnose"
# #         headers = {
# #             "Ocp-Apim-Subscription-Key": self.DXGPT_API_KEY,
# #             "Content-Type": "application/json"
# #         }
# #         payload = {
# #             "description": clinical_text,
# #             "myuuid": str(uuid.uuid4()),
# #             "timezone": "America/New_York",
# #             "model": "gpt4o",
# #             "response_mode": "direct",
# #             "lang": "en"
# #         }

# #         try:
# #             async with aiohttp.ClientSession() as session:
# #                 async with session.post(url, headers=headers, json=payload) as resp:
# #                     if resp.status != 200:
# #                         text = await resp.text()
# #                         logger.error(f"DxGPT API error: {resp.status} - {text}")
# #                         return []
# #                     data = await resp.json()
# #                     diagnoses_data = data.get("data", [])
# #                     results = []
# #                     for d in diagnoses_data[:5]:
# #                         results.append({
# #                             "condition": d.get("diagnosis", "Unknown"),
# #                             "confidence": 1.0,
# #                             "description": d.get("description", ""),
# #                             "symptoms_in_common": d.get("symptoms_in_common", []),
# #                             "symptoms_not_in_common": d.get("symptoms_not_in_common", []),
# #                         })
# #                     return results
# #         except Exception as e:
# #             logger.error(f"DxGPT API call exception: {e}")
# #             return []

# #     def diagnose_with_local_db(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
# #         input_symptom_names = {s.get('symptom', '').lower() for s in input_data.get('symptoms', [])}

# #         diagnoses = []
# #         for disease, data in self.conditions_db.items():
# #             disease_symptoms = set([sym.lower() for sym in data.get('symptoms', [])])
# #             matched = input_symptom_names.intersection(disease_symptoms)
# #             if matched:
# #                 confidence = len(matched) / max(len(disease_symptoms), len(input_symptom_names))
# #                 diagnoses.append({
# #                     "condition": disease,
# #                     "confidence": round(confidence, 2),
# #                     "icd10code": data.get("icd10_code", ""),
# #                     "treatments": data.get("treatments", []),
# #                     "medications": data.get("medications", []),
# #                 })
# #         diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
# #         return diagnoses[:5]

# #     async def diagnose(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
# #         clinical_text = await self.convert_input_to_clinical_text(input_data)
# #         results = await self.call_dxgpt_api(clinical_text)
# #         if results:
# #             return results
# #         logger.info("Using local database fallback diagnosis")
# #         return self.diagnose_with_local_db(input_data)


# # if __name__ == "__main__":
# #     agent = DiagnosisAgent()
# #     sample_input = {
# #         'symptoms': [
# #             {'symptom': 'cough', 'severity': None, 'confidence_score': 1.0, 'entity_type': 'Sign_symptom', 'position': {'start': 27, 'end': 32}},
# #             {'symptom': 'fever', 'severity': 'high', 'confidence_score': 0.98, 'entity_type': 'Modified_symptom', 'position': {'start': 17, 'end': 22}},
# #         ],
# #         'demographics': {'age': '20', 'gender': 'male', 'height': '150', 'weight': '70'},
# #         'allergies': ['no'],
# #         'past_diseases': ['no'],
# #         'medications': ['no']
# #     }

# #     async def run():
# #         diagnoses = await agent.diagnose(sample_input)
# #         print("Top 5 Diagnoses:")
# #         for d in diagnoses:
# #             print(f"Condition: {d['condition']}, Confidence: {d['confidence']}")
# #             print(f"Description: {d.get('description', '')}")
# #             print(f"Symptoms In Common: {d.get('symptoms_in_common', [])}")
# #             # print(f"Symptoms Not In Common: {d.get('symptoms_not_in_common', [])}")
# #             print("")

# #     asyncio.run(run())








###############################################################final########################



# import logging
# import aiohttp
# import asyncio
# import uuid
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.ensemble import RandomForestClassifier
# from typing import List, Dict, Any
# from datetime import datetime

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("DiagnosisAgentStandalone")

# class DiagnosisAgent:
#     DXGPT_API_KEY = os.getenv("DXGPT_API_KEY", "")

#     def __init__(self):
#         self.conditions_db = self._load_sample_conditions()
#         self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
#         self.classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
#         self._train_dummy_classifier()

#     def _load_sample_conditions(self) -> Dict[str, Any]:
#         return {
#             "Common Cold": {
#                 "symptoms": ["cough", "sore throat", "runny nose", "fever"],
#                 "icd10_code": "J00",
#                 "description": "Viral infection in nose and throat",
#                 "treatments": ["rest", "fluids"],
#                 "medications": [],
#             },
#             "Influenza": {
#                 "symptoms": ["fever", "cough", "body ache", "chills", "fatigue"],
#                 "icd10_code": "J11",
#                 "description": "Flu virus infection",
#                 "treatments": ["rest", "hydration"],
#                 "medications": ["antiviral drugs"],
#             },
#             "COVID-19": {
#                 "symptoms": ["fever", "dry cough", "tiredness", "loss of taste", "loss of smell"],
#                 "icd10_code": "U07.1",
#                 "description": "Infectious respiratory disease caused by coronavirus",
#                 "treatments": ["isolation", "supportive care"],
#                 "medications": [],
#             },
#         }

#     def _train_dummy_classifier(self):
#         disease_names = list(self.conditions_db.keys())
#         text_data = [" ".join(self.conditions_db[d]["symptoms"]) for d in disease_names]
#         X = self.vectorizer.fit_transform(text_data)
#         y = list(range(len(disease_names)))
#         self.classifier.fit(X, y)
#         self.num_to_disease = {i: d for i, d in enumerate(disease_names)}

#     async def convert_input_to_clinical_text(self, input_data: Dict[str, Any]) -> str:
#         prompt_intro = (
#             "Analyze patient symptoms considering demographic info, allergies, past diseases, and current medications. "
#             "Provide diagnosis based on comprehensive patient data.\n"
#         )

#         symptoms = input_data.get('symptoms', [])
#         demographics = input_data.get('demographics', {})
#         allergies = input_data.get('allergies', [])
#         past_diseases = input_data.get('past_diseases', [])
#         medications = input_data.get('medications', [])

#         desc_parts = []
#         if demographics:
#             age = demographics.get('age', '')
#             gender = demographics.get('gender', '')
#             height = demographics.get('height', '')
#             weight = demographics.get('weight', '')
#             desc_parts.append(f"Patient is a {age}-year-old {gender} with height {height} cm and weight {weight} kg.")

#         if symptoms:
#             symptom_descs = []
#             for sym in symptoms:
#                 s = sym.get('symptom', '')
#                 severity = sym.get('severity')
#                 if severity:
#                     symptom_descs.append(f"{s} (severity: {severity})")
#                 else:
#                     symptom_descs.append(s)
#             desc_parts.append("Symptoms reported: " + ", ".join(symptom_descs) + ".")

#         if allergies and allergies != ['no']:
#             desc_parts.append("Allergies: " + ", ".join(allergies) + ".")
#         else:
#             desc_parts.append("No known allergies.")

#         if past_diseases and past_diseases != ['no']:
#             desc_parts.append("Past diseases include: " + ", ".join(past_diseases) + ".")
#         else:
#             desc_parts.append("No significant past diseases.")

#         if medications and medications != ['no']:
#             desc_parts.append("Current medications: " + ", ".join(medications) + ".")
#         else:
#             desc_parts.append("No current medications.")

#         return prompt_intro + " ".join(desc_parts)

#     async def call_dxgpt_api(self, clinical_text: str) -> List[Dict[str, Any]]:
#         if not self.DXGPT_API_KEY or self.DXGPT_API_KEY == "your_subscription_key_here":
#             logger.warning("DxGPT API key not provided or default placeholder.")
#             return []

#         url = "https://dxgpt-apim.azure-api.net/api/diagnose"
#         headers = {
#             "Ocp-Apim-Subscription-Key": self.DXGPT_API_KEY,
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "description": clinical_text,
#             "myuuid": str(uuid.uuid4()),
#             "timezone": "America/New_York",
#             "model": "gpt4o",
#             "response_mode": "direct",
#             "lang": "en"
#         }

#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(url, headers=headers, json=payload) as resp:
#                     if resp.status != 200:
#                         text = await resp.text()
#                         logger.error(f"DxGPT API error: {resp.status} - {text}")
#                         return []
#                     data = await resp.json()
#                     diagnoses_data = data.get("data", [])
#                     results = []
#                     for d in diagnoses_data[:5]:
#                         results.append({
#                             "condition": d.get("diagnosis", "Unknown"),
#                             "confidence": 1.0,
#                             "description": d.get("description", ""),
#                             "symptoms_in_common": d.get("symptoms_in_common", []),
#                             "symptoms_not_in_common": d.get("symptoms_not_in_common", []),
#                         })
#                     return results
#         except Exception as e:
#             logger.error(f"DxGPT API call exception: {e}")
#             return []

#     def diagnose_with_local_db(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         input_symptom_names = {s.get('symptom', '').lower() for s in input_data.get('symptoms', [])}

#         diagnoses = []
#         for disease, data in self.conditions_db.items():
#             disease_symptoms = set([sym.lower() for sym in data.get('symptoms', [])])
#             matched = input_symptom_names.intersection(disease_symptoms)
#             if matched:
#                 confidence = len(matched) / max(len(disease_symptoms), len(input_symptom_names))
#                 diagnoses.append({
#                     "condition": disease,
#                     "confidence": round(confidence, 2),
#                     "icd10code": data.get("icd10_code", ""),
#                     "treatments": data.get("treatments", []),
#                     "medications": data.get("medications", []),
#                 })
#         diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
#         return diagnoses[:5]

#     async def diagnose(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         clinical_text = await self.convert_input_to_clinical_text(input_data)
#         results = await self.call_dxgpt_api(clinical_text)
#         if results:
#             return results
#         logger.info("Using local database fallback diagnosis")
#         return self.diagnose_with_local_db(input_data)


# if __name__ == "__main__":
#     agent = DiagnosisAgent()
#     sample_input = {
#         'symptoms': [
#             {'symptom': 'dizziness', 'severity': 'occasional', 'confidence_score': 0.98, 'entity_type': 'Modified_symptom', 'position': {'start': 54, 'end': 63}},
#             {'symptom': 'muscle pain', 'severity': None, 'confidence_score': 0.95, 'entity_type': 'Compound_symptom', 'position': {'start': 26, 'end': 37}},
#             {'symptom': 'fatigue', 'severity': None, 'confidence_score': 0.829, 'entity_type': 'Sign_symptom', 'position': {'start': 17, 'end': 24}}
#         ],
#         'demographics': {'age': '3', 'gender': 'female', 'height': '24', 'weight': '30'},
#         'allergies': ['no'],
#         'past_diseases': ['no'],
#         'medications': ['no']
#     }

#     async def run():
#         diagnoses = await agent.diagnose(sample_input)
#         print("Top 5 Diagnoses Based on Complete Patient Data (Symptoms, Demographics, History):")
#         for d in diagnoses:
#             print(f"Condition: {d['condition']}, Confidence: {d['confidence']}")
#             print(f"Description: {d.get('description', '')}")
#             print(f"Symptoms In Common: {d.get('symptoms_in_common', [])}")
#             print(f"Symptoms Not In Common: {d.get('symptoms_not_in_common', [])}")
#             print("")

#     asyncio.run(run())







# ###########################final####################################






# import logging
# import aiohttp
# import asyncio
# import uuid
# from typing import List, Dict, Any
# from datetime import datetime
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.ensemble import RandomForestClassifier

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("DiagnosisAgentStandalone")

# class DiagnosisAgent:
#     DXGPT_API_KEY = os.getenv("DXGPT_API_KEY", "")

#     def __init__(self):
#         self.conditions_db = self._load_sample_conditions()
#         self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
#         self.classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
#         self._train_dummy_classifier()

#     def _load_sample_conditions(self) -> Dict[str, Any]:
#         return {
#             "Common Cold": {
#                 "symptoms": ["cough", "sore throat", "runny nose", "fever"],
#                 "icd10_code": "J00",
#                 "description": "Viral infection in nose and throat",
#                 "treatments": ["rest", "fluids"],
#                 "medications": [],
#             },
#             "Influenza": {
#                 "symptoms": ["fever", "cough", "body ache", "chills", "fatigue"],
#                 "icd10_code": "J11",
#                 "description": "Flu virus infection",
#                 "treatments": ["rest", "hydration"],
#                 "medications": ["antiviral drugs"],
#             },
#             "COVID-19": {
#                 "symptoms": ["fever", "dry cough", "tiredness", "loss of taste", "loss of smell"],
#                 "icd10_code": "U07.1",
#                 "description": "Infectious respiratory disease caused by coronavirus",
#                 "treatments": ["isolation", "supportive care"],
#                 "medications": [],
#             },
#         }

#     def _train_dummy_classifier(self):
#         disease_names = list(self.conditions_db.keys())
#         text_data = [" ".join(self.conditions_db[d]["symptoms"]) for d in disease_names]
#         X = self.vectorizer.fit_transform(text_data)
#         y = list(range(len(disease_names)))
#         self.classifier.fit(X, y)
#         self.num_to_disease = {i: d for i, d in enumerate(disease_names)}

#     async def convert_input_to_clinical_text(self, input_data: Dict[str, Any]) -> str:
#         prompt_intro = (
#             "Analyze patient symptoms considering demographic info, allergies, past diseases, and current medications. "
#             "Provide diagnosis based on comprehensive patient data.\n"
#         )

#         symptoms = input_data.get('symptoms', [])
#         demographics = input_data.get('demographics', {})
#         allergies = input_data.get('allergies', [])
#         past_diseases = input_data.get('past_diseases', [])
#         medications = input_data.get('medications', [])

#         desc_parts = []
#         if demographics:
#             age = demographics.get('age', '')
#             gender = demographics.get('gender', '')
#             height = demographics.get('height', '')
#             weight = demographics.get('weight', '')
#             desc_parts.append(f"Patient is a {age}-year-old {gender} with height {height} cm and weight {weight} kg.")

#         if symptoms:
#             symptom_descs = []
#             for sym in symptoms:
#                 s = sym.get('symptom', '')
#                 severity = sym.get('severity')
#                 if severity:
#                     symptom_descs.append(f"{s} (severity: {severity})")
#                 else:
#                     symptom_descs.append(s)
#             desc_parts.append("Symptoms reported: " + ", ".join(symptom_descs) + ".")

#         if allergies and allergies != ['no']:
#             desc_parts.append("Allergies: " + ", ".join(allergies) + ".")
#         else:
#             desc_parts.append("No known allergies.")

#         if past_diseases and past_diseases != ['no']:
#             desc_parts.append("Past diseases include: " + ", ".join(past_diseases) + ".")
#         else:
#             desc_parts.append("No significant past diseases.")

#         if medications and medications != ['no']:
#             desc_parts.append("Current medications: " + ", ".join(medications) + ".")
#         else:
#             desc_parts.append("No current medications.")

#         return prompt_intro + " ".join(desc_parts)

#     def calculate_confidence(self,
#                              symptoms_in_common: List[str],
#                              symptoms_not_in_common: List[str],
#                              input_symptoms: List[Dict[str, Any]]) -> float:
#         # Jaccard similarity base confidence
#         num_common = len(symptoms_in_common)
#         num_not_in_common = len(symptoms_not_in_common)
#         union_count = num_common + num_not_in_common
#         if union_count == 0:
#             base_confidence = 0.0
#         else:
#             base_confidence = num_common / union_count

#         # Heuristic boost from severity & confidence score of matched symptoms
#         severity_boost = 0.0
#         severity_matched = 0
#         severity_total = 0

#         symptom_confidence_sum = 0.0
#         symptom_confidence_count = 0

#         input_symptom_map = {s['symptom'].lower(): s for s in input_symptoms}

#         for sym in symptoms_in_common:
#             s = input_symptom_map.get(sym.lower())
#             if s:
#                 severity_total += 1
#                 if s['severity'] and s['severity'].lower() in ['severe', 'high', 'moderate']:
#                     severity_matched += 1
#                 if 'confidence_score' in s:
#                     symptom_confidence_sum += s['confidence_score']
#                     symptom_confidence_count += 1

#         if severity_total > 0:
#             severity_ratio = severity_matched / severity_total
#             severity_boost += 0.2 * severity_ratio  # up to +0.2 boost

#         if symptom_confidence_count > 0:
#             avg_confidence_score = symptom_confidence_sum / symptom_confidence_count
#             severity_boost += 0.3 * avg_confidence_score  # up to +0.3 boost

#         final_confidence = base_confidence + severity_boost
#         return min(max(final_confidence, 0.0), 1.0)

#     async def call_dxgpt_api(self, clinical_text: str, input_symptoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         if not self.DXGPT_API_KEY or self.DXGPT_API_KEY == "your_subscription_key_here":
#             logger.warning("DxGPT API key not provided or default placeholder.")
#             return []

#         url = "https://dxgpt-apim.azure-api.net/api/diagnose"
#         headers = {
#             "Ocp-Apim-Subscription-Key": self.DXGPT_API_KEY,
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "description": clinical_text,
#             "myuuid": str(uuid.uuid4()),
#             "timezone": "America/New_York",
#             "model": "gpt4o",
#             "response_mode": "direct",
#             "lang": "en"
#         }

#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(url, headers=headers, json=payload) as resp:
#                     if resp.status != 200:
#                         text = await resp.text()
#                         logger.error(f"DxGPT API error: {resp.status} - {text}")
#                         return []
#                     data = await resp.json()
#                     diagnoses_data = data.get("data", [])
#                     results = []
#                     for d in diagnoses_data[:5]:
#                         sym_in_common = d.get("symptoms_in_common", [])
#                         sym_not_in_common = d.get("symptoms_not_in_common", [])
#                         confidence = self.calculate_confidence(sym_in_common, sym_not_in_common, input_symptoms)
#                         results.append({
#                             "condition": d.get("diagnosis", "Unknown"),
#                             "confidence": confidence,
#                             "description": d.get("description", ""),
#                             "symptoms_in_common": sym_in_common,
#                             "symptoms_not_in_common": sym_not_in_common,
#                         })
#                     return results
#         except Exception as e:
#             logger.error(f"DxGPT API call exception: {e}")
#             return []

#     def diagnose_with_local_db(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         input_symptom_names = {s.get('symptom', '').lower() for s in input_data.get('symptoms', [])}

#         diagnoses = []
#         for disease, data in self.conditions_db.items():
#             disease_symptoms = set([sym.lower() for sym in data.get('symptoms', [])])
#             matched = input_symptom_names.intersection(disease_symptoms)
#             if matched:
#                 confidence = len(matched) / max(len(disease_symptoms), len(input_symptom_names))
#                 diagnoses.append({
#                     "condition": disease,
#                     "confidence": round(confidence, 2),
#                     "icd10code": data.get("icd10_code", ""),
#                     "treatments": data.get("treatments", []),
#                     "medications": data.get("medications", []),
#                 })
#         diagnoses.sort(key=lambda x: x['confidence'], reverse=True)
#         return diagnoses[:5]

#     async def diagnose(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         clinical_text = await self.convert_input_to_clinical_text(input_data)
#         input_symptoms = input_data.get('symptoms', [])
#         results = await self.call_dxgpt_api(clinical_text, input_symptoms)
#         if results:
#             return results
#         logger.info("Using local database fallback diagnosis")
#         return self.diagnose_with_local_db(input_data)
    
    


# if __name__ == "__main__":
#     agent = DiagnosisAgent()
#     sample_input = {
#         'symptoms': [
#             {'symptom': 'dizziness', 'severity': 'occasional', 'confidence_score': 0.98, 'entity_type': 'Modified_symptom', 'position': {'start': 54, 'end': 63}},
#             {'symptom': 'muscle pain', 'severity': None, 'confidence_score': 0.95, 'entity_type': 'Compound_symptom', 'position': {'start': 26, 'end': 37}},
#             {'symptom': 'fatigue', 'severity': None, 'confidence_score': 0.829, 'entity_type': 'Sign_symptom', 'position': {'start': 17, 'end': 24}},
#         ],
#         'demographics': {'age': '3', 'gender': 'female', 'height': '24', 'weight': '30'},
#         'allergies': ['no'],
#         'past_diseases': ['no'],
#         'medications': ['no']
#     }

#     async def run():
#         diagnoses = await agent.diagnose(sample_input)
#         print("Top 5 Diagnoses Based on Complete Patient Data (Symptoms, Demographics, History):")
#         for d in diagnoses:
#             print(f"Condition: {d['condition']}, Confidence: {d['confidence']:.2f}")
#             print(f"Description: {d.get('description', '')}")
#             print(f"Symptoms In Common: {d.get('symptoms_in_common', [])}")
#             print(f"Symptoms Not In Common: {d.get('symptoms_not_in_common', [])}")
#             print("")

#     asyncio.run(run())






# import logging
# import aiohttp
# import asyncio
# import uuid
# import pandas as pd
# from typing import List, Dict, Any
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.ensemble import RandomForestClassifier

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("DiagnosisAgentStandalone")

# class DiagnosisAgent:
#     DXGPT_API_KEY = os.getenv("DXGPT_API_KEY", "")

#     def __init__(self):
#         # Load CSVs and prepare lookup dictionaries
#         self.medications_map = pd.read_csv('medications.csv').set_index('Disease')['Medication'].to_dict()
#         precautions_df = pd.read_csv('precautions_df.csv')
#         self.precautions_map = {}
#         for _, row in precautions_df.iterrows():
#             disease = row['Disease']
#             points = [row.get(col) for col in precautions_df.columns if col.startswith('Precaution') and pd.notna(row.get(col))]
#             self.precautions_map[disease] = points
#         self.diets_map = pd.read_csv('diets.csv').set_index('Disease')['Diet'].to_dict()
#         workout_df = pd.read_csv('workout_df.csv')
#         self.workout_map = workout_df.groupby('disease')['workout'].apply(list).to_dict()
#         self.description_map = pd.read_csv('description.csv').set_index('Disease')['Description'].to_dict()

#     async def convert_input_to_clinical_text(self, input_data: Dict[str, Any]) -> str:
#         prompt_intro = (
#             "Analyze patient symptoms considering demographic info, allergies, past diseases, and current medications. "
#             "Provide diagnosis based on comprehensive patient data.\n"
#         )
#         symptoms = input_data.get('symptoms', [])
#         demographics = input_data.get('demographics', {})
#         allergies = input_data.get('allergies', [])
#         past_diseases = input_data.get('past_diseases', [])
#         medications = input_data.get('medications', [])
#         desc_parts = []
#         if demographics:
#             age = demographics.get('age', '')
#             gender = demographics.get('gender', '')
#             height = demographics.get('height', '')
#             weight = demographics.get('weight', '')
#             desc_parts.append(f"Patient is a {age}-year-old {gender} with height {height} cm and weight {weight} kg.")
#         if symptoms:
#             symptom_descs = []
#             for sym in symptoms:
#                 s = sym.get('symptom', '')
#                 severity = sym.get('severity')
#                 if severity:
#                     symptom_descs.append(f"{s} (severity: {severity})")
#                 else:
#                     symptom_descs.append(s)
#             desc_parts.append("Symptoms reported: " + ", ".join(symptom_descs) + ".")
#         if allergies and allergies != ['no']:
#             desc_parts.append("Allergies: " + ", ".join(allergies) + ".")
#         else:
#             desc_parts.append("No known allergies.")
#         if past_diseases and past_diseases != ['no']:
#             desc_parts.append("Past diseases include: " + ", ".join(past_diseases) + ".")
#         else:
#             desc_parts.append("No significant past diseases.")
#         if medications and medications != ['no']:
#             desc_parts.append("Current medications: " + ", ".join(medications) + ".")
#         else:
#             desc_parts.append("No current medications.")
#         return prompt_intro + " ".join(desc_parts)

#     def calculate_confidence(self,
#                              symptoms_in_common: List[str],
#                              symptoms_not_in_common: List[str],
#                              input_symptoms: List[Dict[str, Any]]) -> float:
#         num_common = len(symptoms_in_common)
#         num_not_in_common = len(symptoms_not_in_common)
#         union_count = num_common + num_not_in_common
#         if union_count == 0:
#             base_confidence = 0.0
#         else:
#             base_confidence = num_common / union_count

#         severity_boost = 0.0
#         severity_matched = 0
#         severity_total = 0
#         symptom_confidence_sum = 0.0
#         symptom_confidence_count = 0
#         input_symptom_map = {s['symptom'].lower(): s for s in input_symptoms}
#         for sym in symptoms_in_common:
#             s = input_symptom_map.get(sym.lower())
#             if s:
#                 severity_total += 1
#                 if s.get('severity') and s['severity'].lower() in ['severe', 'high', 'moderate']:
#                     severity_matched += 1
#                 if 'confidence_score' in s:
#                     symptom_confidence_sum += s['confidence_score']
#                     symptom_confidence_count += 1
#         if severity_total > 0:
#             severity_ratio = severity_matched / severity_total
#             severity_boost += 0.2 * severity_ratio
#         if symptom_confidence_count > 0:
#             avg_confidence_score = symptom_confidence_sum / symptom_confidence_count
#             severity_boost += 0.3 * avg_confidence_score
#         final_confidence = base_confidence + severity_boost
#         return min(max(final_confidence, 0.0), 1.0)

#     async def call_dxgpt_api(self, clinical_text: str, input_symptoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         if not self.DXGPT_API_KEY or self.DXGPT_API_KEY == "your_subscription_key_here":
#             logger.warning("DxGPT API key not provided or default placeholder.")
#             return []
#         url = "https://dxgpt-apim.azure-api.net/api/diagnose"
#         headers = {
#             "Ocp-Apim-Subscription-Key": self.DXGPT_API_KEY,
#             "Content-Type": "application/json"
#         }
#         payload = {
#             "description": clinical_text,
#             "myuuid": str(uuid.uuid4()),
#             "timezone": "America/New_York",
#             "model": "gpt4o",
#             "response_mode": "direct",
#             "lang": "en"
#         }
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.post(url, headers=headers, json=payload) as resp:
#                     if resp.status != 200:
#                         text = await resp.text()
#                         logger.error(f"DxGPT API error: {resp.status} - {text}")
#                         return []
#                     data = await resp.json()
#                     diagnoses_data = data.get("data", [])
#                     results = []
#                     for d in diagnoses_data[:5]:
#                         sym_in_common = d.get("symptoms_in_common", [])
#                         sym_not_in_common = d.get("symptoms_not_in_common", [])
#                         confidence = self.calculate_confidence(sym_in_common, sym_not_in_common, input_symptoms)
#                         results.append({
#                             "condition": d.get("diagnosis", "Unknown"),
#                             "confidence": confidence,
#                             "description": d.get("description", ""),
#                             "symptoms_in_common": sym_in_common,
#                             "symptoms_not_in_common": sym_not_in_common,
#                         })
#                     return results
#         except Exception as e:
#             logger.error(f"DxGPT API call exception: {e}")
#             return []

#     async def diagnose(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
#         clinical_text = await self.convert_input_to_clinical_text(input_data)
#         input_symptoms = input_data.get('symptoms', [])
#         results = await self.call_dxgpt_api(clinical_text, input_symptoms)
#         if not results:
#             logger.info("No DxGPT diagnosis results; fallback to local DB")
#             return {
#                 "top_diagnosis": {},
#                 "top_5_diagnoses": []
#             }
#         results.sort(key=lambda x: x['confidence'], reverse=True)
#         top = results[0]
#         name = top.get("condition", "")
#         enriched_top = {
#             "condition": name,
#             "confidence": top.get("confidence", 0.0),
#             "description": top.get("description", ""),
#             "medications": eval(self.medications_map.get(name, "[]")),
#             "precautions": self.precautions_map.get(name, []),
#             "diets": eval(self.diets_map.get(name, "[]")),
#             "exercises": self.workout_map.get(name, []),
#         }
#         return {
#             "top_diagnosis": enriched_top,
#             "top_5_diagnoses": results
#         }


# if __name__ == "__main__":
#     agent = DiagnosisAgent()
#     sample_input = {
#     'symptoms': [
#         {'symptom': 'itching', 'severity': 'moderate', 'confidence_score': 0.9},
#         {'symptom': 'redness', 'severity': 'mild', 'confidence_score': 0.8},
#         {'symptom': 'skin rash', 'severity': 'moderate', 'confidence_score': 0.85},
#         {'symptom': 'scaling', 'severity': 'mild', 'confidence_score': 0.7},
#         {'symptom': 'peeling skin', 'severity': 'mild', 'confidence_score': 0.75}
#     ],
#     'demographics': {'age': '30', 'gender': 'female', 'height': '165', 'weight': '60'},
#     'allergies': ['no'],
#     'past_diseases': ['no'],
#     'medications': ['no']

#     }

#     async def run():
#         diagnoses = await agent.diagnose(sample_input)
#         print("Top Diagnosis with details:")
#         td = diagnoses.get("top_diagnosis", {})
#         print(f"Condition: {td.get('condition', '')}, Confidence: {td.get('confidence', 0.0):.2f}")
#         print(f"Description: {td.get('description', '')}")
#         print(f"Medications: {td.get('medications', [])}")
#         print(f"Precautions: {td.get('precautions', [])}")
#         print(f"Diets: {td.get('diets', [])}")
#         print(f"Exercises: {td.get('exercises', [])}")
#         print("\nTop 5 Diagnoses:")
#         for d in diagnoses.get("top_5_diagnoses", []):
#             print(f"Condition: {d['condition']}, Confidence: {d['confidence']:.2f}")
#             print(f"Description: {d.get('description', '')}")
#             print("")

#     asyncio.run(run())

















import logging
import aiohttp
import asyncio
import uuid
import os
from dotenv import load_dotenv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from typing import List, Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnosisAgentStandalone")
load_dotenv()

class DiagnosisAgent:
    DXGPT_API_KEY = os.getenv("DXGPT_API_KEY", "")

    def __init__(self):
        self.conditions_db = self._load_sample_conditions()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english', ngram_range=(1, 2))
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self._train_dummy_classifier()

    def _load_sample_conditions(self) -> Dict[str, Any]:
        return {
            "Common Cold": {
                "symptoms": ["cough", "sore throat", "runny nose", "fever"],
                "icd10_code": "J00",
                "description": "Viral infection in nose and throat",
                "treatments": ["rest", "fluids"],
                "medications": [],
            },
            "Influenza": {
                "symptoms": ["fever", "cough", "body ache", "chills", "fatigue"],
                "icd10_code": "J11",
                "description": "Flu virus infection",
                "treatments": ["rest", "hydration"],
                "medications": ["antiviral drugs"],
            },
            "COVID-19": {
                "symptoms": ["fever", "dry cough", "tiredness", "loss of taste", "loss of smell"],
                "icd10_code": "U07.1",
                "description": "Infectious respiratory disease caused by coronavirus",
                "treatments": ["isolation", "supportive care"],
                "medications": [],
            },
        }

    def _train_dummy_classifier(self):
        disease_names = list(self.conditions_db.keys())
        text_data = [" ".join(self.conditions_db[d]["symptoms"]) for d in disease_names]
        X = self.vectorizer.fit_transform(text_data)
        y = list(range(len(disease_names)))
        self.classifier.fit(X, y)
        self.num_to_disease = {i: d for i, d in enumerate(disease_names)}

    def _get_medical_recommendations(self, condition: str) -> Dict[str, List[str]]:
        """Get medical recommendations for a condition"""
        condition_lower = condition.lower()
        
        recommendations = {
            "medications": [],
            "precautions": [],
            "exercises": [],
            "diet": []
        }
        
        if "influenza" in condition_lower or "flu" in condition_lower:
            recommendations = {
                "medications": ["Antiviral medications (Oseltamivir/Tamiflu)", "Fever reducers (Acetaminophen, Ibuprofen)", "Cough suppressants", "Decongestants if needed"],
                "precautions": ["Stay home and rest", "Stay hydrated", "Avoid contact with others", "Cover coughs and sneezes"],
                "exercises": ["Rest during acute phase", "Light stretching when feeling better", "Gradual return to activity", "Deep breathing exercises"],
                "diet": ["Stay hydrated with fluids", "Warm broths and soups", "Soft, easy-to-digest foods", "Avoid dairy if congested"]
            }
        elif "cold" in condition_lower:
            recommendations = {
                "medications": ["Pain relievers (Acetaminophen, Ibuprofen)", "Decongestants", "Throat lozenges", "Saline nasal spray"],
                "precautions": ["Get plenty of rest", "Stay hydrated", "Wash hands frequently", "Use humidifier"],
                "exercises": ["Light walking if energy permits", "Gentle stretching", "Avoid intense exercise", "Listen to your body"],
                "diet": ["Warm fluids and teas", "Chicken soup", "Citrus fruits for vitamin C", "Honey for sore throat"]
            }
        elif "covid" in condition_lower:
            recommendations = {
                "medications": ["Acetaminophen for fever", "Cough suppressants if needed", "Follow healthcare provider guidance", "Antiviral medications if prescribed"],
                "precautions": ["Isolate from others", "Monitor symptoms closely", "Seek medical attention for breathing difficulties", "Follow public health guidelines"],
                "exercises": ["Avoid exercise during illness", "Breathing exercises", "Gradual activity increase after recovery", "Monitor for fatigue"],
                "diet": ["Nutritious, balanced meals", "Plenty of fluids", "Protein-rich foods", "Fruits and vegetables"]
            }
        elif "viral infection" in condition_lower:
            recommendations = {
                "medications": ["Symptomatic treatment", "Fever reducers (Acetaminophen)", "Rest and hydration", "Over-the-counter pain relief"],
                "precautions": ["Rest and recover", "Stay hydrated", "Monitor symptoms", "Avoid spreading to others"],
                "exercises": ["Rest during acute symptoms", "Light activity as tolerated", "Gradual increase in exercise", "Stay hydrated during activity"],
                "diet": ["Light, nutritious meals", "Adequate fluid intake", "Easy-to-digest foods", "Avoid heavy meals"]
            }
        elif "anemia" in condition_lower:
            recommendations = {
                "medications": ["Iron supplements (if iron deficiency)", "Vitamin B12 supplements", "Folic acid supplements", "Treat underlying cause"],
                "precautions": ["Monitor energy levels", "Avoid strenuous activities", "Eat iron-rich foods", "Regular medical follow-up"],
                "exercises": ["Light to moderate exercise", "Avoid high-intensity workouts", "Build stamina gradually", "Monitor for dizziness"],
                "diet": ["Iron-rich foods (spinach, red meat)", "Vitamin C foods for iron absorption", "B12-rich foods", "Avoid tea/coffee with meals"]
            }
        elif "fatigue" in condition_lower:
            recommendations = {
                "medications": ["Address underlying conditions", "Multivitamin supplements", "Iron supplements if deficient", "Consult doctor for persistent fatigue"],
                "precautions": ["Ensure adequate sleep", "Manage stress levels", "Gradual increase in activity", "Monitor for other symptoms"],
                "exercises": ["Gentle exercises like walking", "Yoga or stretching", "Gradually increase intensity", "Balance activity with rest"],
                "diet": ["Balanced, regular meals", "Complex carbohydrates", "Lean proteins", "Stay hydrated"]
            }
        else:
            # Default recommendations for unknown conditions
            recommendations = {
                "medications": ["Consult healthcare provider", "Follow prescribed medications", "Monitor symptoms", "Seek medical attention if worsening"],
                "precautions": ["Follow medical advice", "Monitor symptoms", "Rest as needed", "Seek help if symptoms worsen"],
                "exercises": ["Consult doctor before exercising", "Start with light activities", "Gradually increase intensity", "Stop if symptoms worsen"],
                "diet": ["Maintain balanced nutrition", "Stay hydrated", "Eat regular meals", "Consult nutritionist if needed"]
            }
        
        return recommendations

    async def convert_input_to_clinical_text(self, input_data: Dict[str, Any]) -> str:
        prompt_intro = (
            "Analyze patient symptoms considering demographic info, allergies, past diseases, and current medications. "
            "Provide diagnosis based on comprehensive patient data.\n"
        )

        symptoms = input_data.get('symptoms', [])
        demographics = input_data.get('demographics', {})
        allergies = input_data.get('allergies', [])
        past_diseases = input_data.get('past_diseases', [])
        medications = input_data.get('medications', [])

        desc_parts = []
        if demographics:
            age = demographics.get('age', '')
            gender = demographics.get('gender', '')
            height = demographics.get('height', '')
            weight = demographics.get('weight', '')
            desc_parts.append(f"Patient is a {age}-year-old {gender} with height {height} cm and weight {weight} kg.")

        if symptoms:
            symptom_descs = []
            for sym in symptoms:
                s = sym.get('symptom', '')
                severity = sym.get('severity')
                if severity:
                    symptom_descs.append(f"{s} (severity: {severity})")
                else:
                    symptom_descs.append(s)
            desc_parts.append("Symptoms reported: " + ", ".join(symptom_descs) + ".")

        if allergies and allergies != ['no']:
            desc_parts.append("Allergies: " + ", ".join(allergies) + ".")
        else:
            desc_parts.append("No known allergies.")

        if past_diseases and past_diseases != ['no']:
            desc_parts.append("Past diseases include: " + ", ".join(past_diseases) + ".")
        else:
            desc_parts.append("No significant past diseases.")

        if medications and medications != ['no']:
            desc_parts.append("Current medications: " + ", ".join(medications) + ".")
        else:
            desc_parts.append("No current medications.")

        return prompt_intro + " ".join(desc_parts)

    def calculate_confidence(self,
                             symptoms_in_common: List[str],
                             symptoms_not_in_common: List[str],
                             input_symptoms: List[Dict[str, Any]]) -> float:
        # Jaccard similarity base confidence
        num_common = len(symptoms_in_common)
        num_not_in_common = len(symptoms_not_in_common)
        union_count = num_common + num_not_in_common
        if union_count == 0:
            base_confidence = 0.0
        else:
            base_confidence = num_common / union_count

        # Heuristic boost from severity & confidence score of matched symptoms
        severity_boost = 0.0
        severity_matched = 0
        severity_total = 0

        symptom_confidence_sum = 0.0
        symptom_confidence_count = 0

        input_symptom_map = {s['symptom'].lower(): s for s in input_symptoms}

        for sym in symptoms_in_common:
            s = input_symptom_map.get(sym.lower())
            if s:
                severity_total += 1
                if s.get('severity', '') and s.get('severity', '').lower() in ['severe', 'high', 'moderate']:
                    severity_matched += 1
                if 'confidence_score' in s:
                    symptom_confidence_sum += s['confidence_score']
                    symptom_confidence_count += 1

        if severity_total > 0:
            severity_ratio = severity_matched / severity_total
            severity_boost += 0.2 * severity_ratio  # up to +0.2 boost

        if symptom_confidence_count > 0:
            avg_confidence_score = symptom_confidence_sum / symptom_confidence_count
            severity_boost += 0.3 * avg_confidence_score  # up to +0.3 boost

        final_confidence = base_confidence + severity_boost
        return min(max(final_confidence, 0.0), 1.0)

    async def call_dxgpt_api(self, clinical_text: str, input_symptoms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.DXGPT_API_KEY:
            logger.info("DxGPT API key not configured; using the local deterministic matcher.")
            return []

        url = "https://dxgpt-apim.azure-api.net/api/diagnose"
        headers = {
            "Ocp-Apim-Subscription-Key": self.DXGPT_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "description": clinical_text,
            "myuuid": str(uuid.uuid4()),
            "timezone": "America/New_York",
            "model": "gpt4o",
            "response_mode": "direct",
            "lang": "en"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error(f"DxGPT API error: {resp.status} - {text}")
                        return []
                    data = await resp.json()
                    diagnoses_data = data.get("data", [])
                    results = []
                    for rank, d in enumerate(diagnoses_data[:5], start=1):
                        sym_in_common = d.get("symptoms_in_common", [])
                        sym_not_in_common = d.get("symptoms_not_in_common", [])
                        ranking_score = (len(diagnoses_data[:5]) - rank + 1) / len(diagnoses_data[:5])
                        results.append({
                            "condition": d.get("diagnosis", "Unknown"),
                            "confidence": ranking_score,
                            "description": d.get("description", ""),
                            "symptoms_in_common": sym_in_common,
                            "symptoms_not_in_common": sym_not_in_common,
                        })
                    return results
        except Exception as e:
            logger.error(f"DxGPT API call exception: {e}")
            return []

    def diagnose_with_local_db(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        symptom_aliases = {
            "body ache": "muscle pain",
            "body aches": "muscle pain",
            "tiredness": "fatigue",
        }
        input_symptom_names = set()
        input_records = {}
        for symptom in input_data.get('symptoms', []):
            if not isinstance(symptom, dict) or symptom.get("negated") or symptom.get("assertion") == "negated":
                continue
            name = str(symptom.get('symptom', '')).strip().lower()
            if name:
                canonical = symptom_aliases.get(name, name)
                input_symptom_names.add(canonical)
                input_records[canonical] = symptom

        diagnoses = []
        for disease, data in self.conditions_db.items():
            disease_symptoms = {
                symptom_aliases.get(str(sym).lower(), str(sym).lower())
                for sym in data.get('symptoms', [])
            }
            matched = input_symptom_names.intersection(disease_symptoms)
            if matched:
                # This is a bounded symptom-overlap ranking score, not a
                # probability. Rare symptoms contribute slightly more.
                weights = {
                    "loss of taste": 1.5, "loss of smell": 1.5,
                    "sore throat": 1.2, "chills": 1.2,
                }
                matched_weight = sum(weights.get(symptom, 1.0) for symptom in matched)
                input_weight = sum(weights.get(symptom, 1.0) for symptom in input_symptom_names)
                disease_weight = sum(weights.get(symptom, 1.0) for symptom in disease_symptoms)
                overlap = matched_weight / max(disease_weight, input_weight, 1.0)
                confidence = round(min(max(overlap, 0.0), 1.0), 3)
                matched_symptoms = sorted(matched)
                diagnoses.append({
                    "condition": disease,
                    "confidence": confidence,
                    "ranking_score": confidence,
                    "score_type": "bounded weighted symptom overlap; not a probability",
                    "symptoms_in_common": matched_symptoms,
                    "symptoms_not_in_common": sorted(disease_symptoms - input_symptom_names),
                    "icd10code": data.get("icd10_code", ""),
                    "treatments": data.get("treatments", []),
                    "medications": data.get("medications", []),
                })
        diagnoses.sort(key=lambda x: (-x['confidence'], x['condition']))
        return diagnoses[:5]

    async def diagnose(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        clinical_text = await self.convert_input_to_clinical_text(input_data)
        input_symptoms = input_data.get('symptoms', [])
        results = await self.call_dxgpt_api(clinical_text, input_symptoms)
        if not results:
            logger.info("Using local database fallback diagnosis")
            results = self.diagnose_with_local_db(input_data)
        
        # Get top diagnosis and generate recommendations
        if results:
            top_diagnosis = max(results, key=lambda x: x.get('confidence', 0))
            recommendations = self._get_medical_recommendations(top_diagnosis['condition'])
            
            return {
                "top_diagnosis": {
                    "condition": top_diagnosis['condition'],
                    "confidence": f"{top_diagnosis.get('confidence', 0):.2f}",
                    "ranking_score": top_diagnosis.get("ranking_score", top_diagnosis.get("confidence", 0)),
                    "score_type": top_diagnosis.get(
                        "score_type", "bounded weighted symptom overlap; not a probability"
                    ),
                    "symptoms_in_common": top_diagnosis.get("symptoms_in_common", []),
                    "symptoms_not_in_common": top_diagnosis.get("symptoms_not_in_common", []),
                    "medications": recommendations['medications'],
                    "precautions": recommendations['precautions'],
                    "exercises": recommendations['exercises'],
                    "diet": recommendations['diet']
                },
                "all_diagnoses": [
                    {
                        "condition": d.get('condition', 'Unknown'),
                        "confidence": f"{d.get('confidence', 0):.2f}"
                        ,"ranking_score": d.get("ranking_score", d.get("confidence", 0)),
                        "score_type": d.get(
                            "score_type", "bounded weighted symptom overlap; not a probability"
                        ),
                        "symptoms_in_common": d.get("symptoms_in_common", []),
                        "symptoms_not_in_common": d.get("symptoms_not_in_common", []),
                    }
                    for d in sorted(results, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
                ]
            }
        else:
            return {
                "top_diagnosis": {
                    "condition": "No diagnosis found",
                    "confidence": "0.0",
                    "medications": ["Consult healthcare provider"],
                    "precautions": ["Seek medical attention"],
                    "exercises": ["Follow medical advice"],
                    "diet": ["Maintain balanced nutrition"]
                },
                "all_diagnoses": []
            }


if __name__ == "__main__":
    agent = DiagnosisAgent()
    sample_input = {
        'symptoms': [
            {'symptom': 'dizziness', 'severity': 'occasional', 'confidence_score': 0.98, 'entity_type': 'Modified_symptom', 'position': {'start': 54, 'end': 63}},
            {'symptom': 'muscle pain', 'severity': None, 'confidence_score': 0.95, 'entity_type': 'Compound_symptom', 'position': {'start': 26, 'end': 37}},
            {'symptom': 'fatigue', 'severity': None, 'confidence_score': 0.829, 'entity_type': 'Sign_symptom', 'position': {'start': 17, 'end': 24}}
        ],
        'demographics': {'age': '3', 'gender': 'female', 'height': '24', 'weight': '30'},
        'allergies': ['no'],
        'past_diseases': ['no'],
        'medications': ['no']
    }

    async def run():
        result = await agent.diagnose(sample_input)
        
        print("=== TOP DIAGNOSIS WITH RECOMMENDATIONS ===")
        top = result['top_diagnosis']
        print(f"Condition: {top['condition']}")
        print(f"Confidence: {top['confidence']}")
        print("\nMedications:")
        for med in top['medications']:
            print(f"  • {med}")
        print("\nPrecautions:")
        for prec in top['precautions']:
            print(f"  • {prec}")
        print("\nExercises:")
        for ex in top['exercises']:
            print(f"  • {ex}")
        print("\nDiet:")
        for diet in top['diet']:
            print(f"  • {diet}")
        
        print("\n=== ALL DIAGNOSES ===")
        for i, diag in enumerate(result['all_diagnoses'], 1):
            print(f"{i}. {diag['condition']} - {diag['confidence']}")

    asyncio.run(run())