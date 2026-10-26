# import os
# import requests
# import re
# import json
# from typing import List, Dict, Tuple, Optional
# from dotenv import load_dotenv

# load_dotenv()

# API_URL = "https://router.huggingface.co/hf-inference/models/d4data/biomedical-ner-all"
# API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "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")

# headers = {
#     "Authorization": f"Bearer {API_TOKEN}"
# }

# class EnhancedSymptomParser:
#     def __init__(self):
#         # Severity indicators with their normalized forms
#         self.severity_patterns = {
#             'severe': ['severe', 'extreme', 'intense', 'sharp', 'excruciating', 'unbearable'],
#             'acute': ['acute'],
#             'chronic': ['chronic', 'persistent', 'constant', 'continuous', 'ongoing'],
#             'moderate': ['moderate', 'noticeable', 'significant', 'considerable'],
#             'mild': ['mild', 'slight', 'minor', 'low', 'weak', 'light'],
#             'high': ['high', 'elevated', 'increased'],
#             'occasional': ['occasional', 'intermittent', 'sporadic', 'periodic', 'sometimes'],
#             'sudden': ['sudden', 'abrupt', 'rapid', 'quick'],
#             'gradual': ['gradual', 'slow', 'progressive']
#         }
        
#         # Common anatomical and descriptive modifiers
#         self.modifiers = [
#             'chest', 'head', 'stomach', 'back', 'neck', 'throat', 'eye', 'ear',
#             'muscle', 'joint', 'abdominal', 'cardiac', 'respiratory', 'nasal',
#             'facial', 'limb', 'leg', 'arm', 'shoulder', 'knee', 'ankle'
#         ]
        
#         # Common symptom patterns that need expansion
#         self.compound_patterns = [
#             (r'\b(chest)\s+(pain|ache|discomfort)', r'\1 \2'),
#             (r'\b(muscle)\s+(pain|ache|cramp|spasm)', r'\1 \2'),
#             (r'\b(back)\s+(pain|ache)', r'\1 \2'),
#             (r'\b(head)\s+(ache|pain)', r'head\2'),
#             (r'\b(stomach)\s+(pain|ache)', r'\1 \2'),
#             (r'\b(shortness)\s+of\s+(breath)', r'\1 of \2'),
#             (r'\b(rapid)\s+(heart\s*beat|pulse)', r'\1 \2'),
#             (r'\b(difficulty)\s+(breathing|swallowing)', r'\1 \2'),
#             (r'\b(loss)\s+of\s+(appetite|consciousness)', r'\1 of \2'),
#             (r'\b(occasional)\s+(dizziness|nausea|headache|pain)', r'\2'),  # Extract the symptom, not the modifier
#             (r'\b(mild|severe|acute|chronic)\s+(pain|ache|nausea|headache|dizziness|fatigue)', r'\2'),  # Extract symptom
#         ]

#     def preprocess_text(self, text: str) -> str:
#         """Preprocess text to better handle compound symptoms"""
#         processed = text
#         for pattern, replacement in self.compound_patterns:
#             processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)
#         return processed

#     def extract_severity_for_entity(self, text: str, entity_start: int, entity_end: int, entity_text: str) -> Optional[str]:
#         """Extract severity specifically for a given entity with more precise context"""
#         # Clean entity text for matching
#         clean_entity = re.sub(r'[^\w\s]', '', entity_text.lower()).strip()
        
#         # Create sentence-level context (more accurate than fixed window)
#         sentences = re.split(r'[.!?;]', text)
#         target_sentence = ""
        
#         for sentence in sentences:
#             if entity_start >= text.find(sentence) and entity_end <= text.find(sentence) + len(sentence):
#                 target_sentence = sentence.lower()
#                 break
        
#         if not target_sentence:
#             # Fallback to window approach
#             window_start = max(0, entity_start - 30)
#             window_end = min(len(text), entity_end + 30)
#             target_sentence = text[window_start:window_end].lower()
        
#         # Look for severity modifiers that are close to this specific entity
#         # Split into clauses by common separators
#         clauses = re.split(r'\s+and\s+|\s*,\s*', target_sentence)
        
#         target_clause = ""
#         for clause in clauses:
#             if clean_entity in clause.lower():
#                 target_clause = clause
#                 break
        
#         if not target_clause:
#             target_clause = target_sentence
            
#         # Extract severity from the specific clause containing this entity
#         words = re.findall(r'\b\w+\b', target_clause)
        
#         # Check for severity patterns, prioritizing closer matches
#         for severity, patterns in self.severity_patterns.items():
#             for pattern in patterns:
#                 if pattern in words:
#                     # Check if the severity word is reasonably close to entity words
#                     entity_word_positions = []
#                     severity_positions = []
                    
#                     for i, word in enumerate(words):
#                         if word in clean_entity.split():
#                             entity_word_positions.append(i)
#                         if word == pattern:
#                             severity_positions.append(i)
                    
#                     # If severity is within 4 words of entity, it's likely related
#                     for s_pos in severity_positions:
#                         for e_pos in entity_word_positions:
#                             if abs(s_pos - e_pos) <= 4:
#                                 return severity
        
#         return None

#     def find_compound_symptoms(self, text: str) -> List[Dict]:
#         """Find compound symptoms using regex patterns"""
#         compound_symptoms = []
        
#         # First, find "occasional dizziness" type patterns where we want the symptom, not the modifier
#         modifier_symptom_pattern = r'\b(occasional|mild|severe|acute|chronic|high|sudden)\s+(dizziness|nausea|headache|pain|fatigue|cough|fever)\b'
#         for match in re.finditer(modifier_symptom_pattern, text, re.IGNORECASE):
#             modifier = match.group(1)
#             symptom = match.group(2)
#             compound_symptoms.append({
#                 'symptom': symptom,  # Just the symptom, not the modifier
#                 'start': match.start(2),  # Position of symptom only
#                 'end': match.end(2),
#                 'confidence_score': 0.98,
#                 'entity_type': 'Modified_symptom',
#                 'modifier': modifier  # Store modifier separately
#             })
        
#         # Then find anatomical + symptom patterns
#         for pattern, _ in self.compound_patterns[:-2]:  # Exclude the modifier patterns we handled above
#             matches = re.finditer(pattern, text, re.IGNORECASE)
#             for match in matches:
#                 compound_symptoms.append({
#                     'symptom': match.group(0),
#                     'start': match.start(),
#                     'end': match.end(),
#                     'confidence_score': 0.95,
#                     'entity_type': 'Compound_symptom'
#                 })
        
#         return compound_symptoms

#     def expand_symptom_with_modifiers(self, text: str, entity_start: int, entity_end: int) -> Tuple[str, int, int]:
#         """Expand symptom to include anatomical or descriptive modifiers"""
#         entity_text = text[entity_start:entity_end].strip()
        
#         # Handle truncated words by looking for complete word boundaries
#         if len(entity_text) >= 3:
#             # Check if entity seems to be a fragment of a larger word
#             # Look backwards to see if this is part of a larger word
#             extended_start = entity_start
#             while extended_start > 0 and not text[extended_start - 1].isspace():
#                 extended_start -= 1
            
#             full_word = text[extended_start:entity_end].strip()
            
#             # If the full word is significantly longer and looks like a medical term, use it
#             if len(full_word) > len(entity_text) and len(full_word) <= 20:
#                 # Check if it's a reasonable medical term (contains the original entity)
#                 if entity_text.lower() in full_word.lower():
#                     entity_text = full_word
#                     entity_start = extended_start
        
#         # Skip if entity starts with conjunctions or prepositions
#         if entity_text.lower().startswith(('and ', 'or ', 'of ', 'in ', 'on ', 'at ', 'with ')):
#             # Try to clean it up by removing the conjunction/preposition
#             clean_parts = entity_text.split()[1:] if len(entity_text.split()) > 1 else []
#             if clean_parts:
#                 clean_entity = ' '.join(clean_parts)
#                 # Find the actual start of the clean entity in the text
#                 clean_start_offset = entity_text.find(clean_parts[0])
#                 return clean_entity, entity_start + clean_start_offset, entity_end
#             else:
#                 return entity_text, entity_start, entity_end
        
#         # Look backwards for modifiers (anatomical terms)
#         new_start = entity_start
#         words_before = []
        
#         # Find start of previous word
#         pos = entity_start - 1
#         while pos >= 0 and text[pos].isspace():
#             pos -= 1
        
#         if pos >= 0:
#             word_end = pos + 1
#             while pos >= 0 and not text[pos].isspace():
#                 pos -= 1
            
#             prev_word = text[pos + 1:word_end].strip()
#             if prev_word.lower() in self.modifiers:
#                 words_before = [prev_word]
#                 new_start = pos + 1
        
#         # Look forward for completions
#         new_end = entity_end
#         words_after = []
        
#         remaining_text = text[entity_end:entity_end + 25].lower()
        
#         if entity_text.lower() == "shortness":
#             if remaining_text.strip().startswith("of breath"):
#                 words_after = ["of breath"]
#                 new_end = entity_end + 10  # len(" of breath")
#         elif entity_text.lower() == "rapid":
#             if "heartbeat" in remaining_text[:12]:
#                 words_after = ["heartbeat"]
#                 new_end = entity_end + len(" heartbeat")
#             elif "heart beat" in remaining_text[:15]:
#                 words_after = ["heart beat"]  
#                 new_end = entity_end + len(" heart beat")
#         elif entity_text.lower() == "loss":
#             match = re.match(r'\s+of\s+(\w+)', remaining_text)
#             if match:
#                 words_after = [f"of {match.group(1)}"]
#                 new_end = entity_end + len(match.group(0))
        
#         # Construct the expanded symptom
#         expanded_parts = words_before + [entity_text] + words_after
#         expanded_symptom = " ".join(expanded_parts).strip()
        
#         return expanded_symptom, new_start, new_end

#     def extract_symptoms_from_text(self, text: str) -> Dict:
#         """Extract symptoms with severity and return structured JSON"""
#         # Preprocess text for better compound detection
#         processed_text = self.preprocess_text(text)
        
#         # First, find compound symptoms using rules
#         compound_symptoms = self.find_compound_symptoms(text)
        
#         payload = {"inputs": text}
        
#         try:
#             response = requests.post(API_URL, headers=headers, json=payload)
            
#             if response.status_code != 200:
#                 return {
#                     "status": "error",
#                     "error_code": response.status_code,
#                     "error_message": response.text,
#                     "symptoms": []
#                 }
                
#             entities = response.json()
            
#             # Filter for relevant entity types
#             relevant_entities = []
#             if entities:
#                 for ent in entities:
#                     entity_group = ent.get('entity_group', '').upper()
#                     if entity_group in ['SIGN_SYMPTOM', 'SYMPTOM', 'DISEASE', 'DISORDER']:
#                         relevant_entities.append(ent)
            
#             # Combine NER entities with compound symptoms
#             all_symptoms = []
#             processed_spans = set()
            
#             # Process compound symptoms first (higher priority)
#             for comp_symp in compound_symptoms:
#                 span_key = f"{comp_symp['start']}-{comp_symp['end']}"
#                 processed_spans.add(span_key)
                
#                 # For modified symptoms, extract severity from the stored modifier
#                 if 'modifier' in comp_symp:
#                     severity = comp_symp['modifier'].lower()
#                     # Map modifier to our severity categories
#                     if severity in ['occasional', 'mild', 'severe', 'acute', 'chronic', 'high', 'sudden']:
#                         mapped_severity = severity
#                     else:
#                         mapped_severity = self.extract_severity_for_entity(
#                             text, comp_symp['start'], comp_symp['end'], comp_symp['symptom']
#                         )
#                 else:
#                     mapped_severity = self.extract_severity_for_entity(
#                         text, comp_symp['start'], comp_symp['end'], comp_symp['symptom']
#                     )
                
#                 symptom_data = {
#                     "symptom": comp_symp['symptom'],
#                     "severity": mapped_severity,
#                     "confidence_score": comp_symp['confidence_score'],
#                     "entity_type": comp_symp['entity_type'],
#                     "position": {
#                         "start": comp_symp['start'],
#                         "end": comp_symp['end']
#                     }
#                 }
#                 all_symptoms.append(symptom_data)
            
#             # Process NER entities
#             for ent in relevant_entities:
#                 start = ent['start']
#                 end = ent['end']
                
#                 # Check for overlaps with compound symptoms
#                 overlaps = False
#                 for comp_start, comp_end in [
#                     (int(span.split('-')[0]), int(span.split('-')[1])) 
#                     for span in processed_spans
#                 ]:
#                     if not (end <= comp_start or start >= comp_end):
#                         overlaps = True
#                         break
                
#                 if overlaps:
#                     continue
                
#                 # Expand symptom with context
#                 expanded_symptom, new_start, new_end = self.expand_symptom_with_modifiers(text, start, end)
                
#                 # Extract severity for this specific entity
#                 severity = self.extract_severity_for_entity(text, start, end, expanded_symptom)
                
#                 # Clean up the symptom text
#                 cleaned_symptom = re.sub(r'\s+', ' ', expanded_symptom).strip()
                
#                 if cleaned_symptom and len(cleaned_symptom) > 1:
#                     symptom_data = {
#                         "symptom": cleaned_symptom,
#                         "severity": severity,
#                         "confidence_score": round(ent.get('score', 0), 3),
#                         "entity_type": ent.get('entity_group'),
#                         "position": {
#                             "start": new_start,
#                             "end": new_end
#                         }
#                     }
#                     all_symptoms.append(symptom_data)
            
#             # Remove duplicates and filter out poor quality extractions
#             seen_symptoms = {}
#             unique_symptoms = []
            
#             for symptom in all_symptoms:
#                 symptom_key = symptom['symptom'].lower().strip()
                
#                 # Skip very short or invalid symptoms
#                 if len(symptom_key) <= 2 or not symptom_key:
#                     continue
                    
#                 # Skip symptoms that are just conjunctions or fragments
#                 if symptom_key in ['and', 'or', 'of', 'in', 'on', 'at', 'with', 'di', 'the']:
#                     continue
                
#                 # Handle duplicates by keeping the one with higher confidence
#                 if symptom_key in seen_symptoms:
#                     existing = seen_symptoms[symptom_key]
#                     if symptom['confidence_score'] > existing['confidence_score']:
#                         # Remove the old one and add the new one
#                         unique_symptoms = [s for s in unique_symptoms if s['symptom'].lower().strip() != symptom_key]
#                         unique_symptoms.append(symptom)
#                         seen_symptoms[symptom_key] = symptom
#                 else:
#                     seen_symptoms[symptom_key] = symptom
#                     unique_symptoms.append(symptom)
            
#             # Sort by confidence score (descending)
#             unique_symptoms.sort(key=lambda x: x['confidence_score'], reverse=True)
            
#             return {
#                 "status": "success",
#                 "input_text": text,
#                 "total_symptoms_found": len(unique_symptoms),
#                 "symptoms": unique_symptoms
#             }
            
#         except requests.exceptions.RequestException as e:
#             return {
#                 "status": "error",
#                 "error_message": f"Request failed: {str(e)}",
#                 "symptoms": []
#             }
#         except Exception as e:
#             return {
#                 "status": "error", 
#                 "error_message": f"Processing failed: {str(e)}",
#                 "symptoms": []
#             }



#     def collect_demographics_and_history_interactive(self):
#         # Interactive prompts for age/gender/height/weight/allergies/past_diseases/medications
#         data = {
#             "age": None,
#             "gender": None,
#             "height": None,
#             "weight": None,
#             "allergies": [],
#             "past_diseases": [],
#             "medications": []
#         }
#         data["age"] = input("Please enter your age (years): ").strip()
#         data["gender"] = input("Please enter your gender (male/female/other): ").strip()
#         data["height"] = input("Please enter your height with units (e.g. 170cm or 5'8\"): ").strip()
#         data["weight"] = input("Please enter your weight with units (e.g. 70kg or 150lbs): ").strip()
#         allergies = input("List any allergies (comma-separated): ").strip()
#         data["allergies"] = [a.strip() for a in allergies.split(",") if a.strip()]
#         past_diseases = input("List any past diseases or medical conditions (comma-separated): ").strip()
#         data["past_diseases"] = [d.strip() for d in past_diseases.split(",") if d.strip()]
#         medications = input("List any ongoing medications (comma-separated): ").strip()
#         data["medications"] = [m.strip() for m in medications.split(",") if m.strip()]
#         return data

#     def extract_and_collect(self, text: str):
#         # Runs your symptom extraction, then interactively gathers extra info
#         symptom_result = self.extract_symptoms_from_text(text)
#         if symptom_result["status"] != "success":
#             print("Error extracting symptoms:", symptom_result.get("errormessage"))
#             return None
#         collected = {
#             "symptoms": symptom_result["symptoms"],
#             "demographics": {},
#             "allergies": [],
#             "past_diseases": [],
#             "medications": [],
#         }
#         interactive_data = self.collect_demographics_and_history_interactive()
#         collected["demographics"]["age"] = interactive_data["age"]
#         collected["demographics"]["gender"] = interactive_data["gender"]
#         collected["demographics"]["height"] = interactive_data["height"]
#         collected["demographics"]["weight"] = interactive_data["weight"]
#         collected["allergies"] = interactive_data["allergies"]
#         collected["past_diseases"] = interactive_data["past_diseases"]
#         collected["medications"] = interactive_data["medications"]

#         return collected

# # def main():
# #     parser = EnhancedSymptomParser()
    
# #     # Original test cases
# #     original_tests = [
# #         "Patient has high fever and cough",
# #         "The subject reports severe headache and mild nausea", 
# #         "Symptoms include fatigue, muscle pain, and occasional dizziness",
# #         "She complained of chest pain and shortness of breath",
# #         "The patient experiences rash and swelling around the eyes",
# #         "He has chronic back pain and acute abdominal discomfort",
# #         "Patient presents with sudden onset of severe chest pain and rapid heartbeat"
# #     ]
    
# #     # Additional complex test cases
# #     complex_tests = [
# #         "The 45-year-old male presents with severe crushing chest pain radiating to left arm, profuse sweating, and mild nausea",
# #         "Patient reports chronic lower back pain, intermittent leg cramps, and occasional numbness in fingers",
# #         "She has been experiencing persistent headaches, blurred vision, and episodes of sudden dizziness for the past week",
# #         "Symptoms include high-grade fever (102°F), chills, body aches, dry cough, and loss of appetite",
# #         "The child has developed a widespread rash, swollen lymph nodes, sore throat, and difficulty swallowing",
# #         "Patient complains of sharp abdominal pain in right lower quadrant, vomiting, and low-grade fever",
# #         "He reports progressive muscle weakness, joint stiffness in the morning, and chronic fatigue",
# #         "The elderly woman presents with confusion, memory loss, tremors, and difficulty with balance",
# #         "Acute onset of severe headache, neck stiffness, photophobia, and high fever",
# #         "Patient has been having palpitations, excessive sweating, anxiety attacks, and insomnia for 3 months"
# #     ]
    
# #     # Edge cases and tricky scenarios
# #     edge_cases = [
# #         "No pain, no fever, no cough - patient feels completely normal",
# #         "Mild to moderate pain that comes and goes",
# #         "Severe pain 8/10, worse with movement, better with rest",
# #         "The pain is described as burning, stabbing, and throbbing",
# #         "Patient denies chest pain but admits to pressure and tightness",
# #         "Intermittent sharp pain versus constant dull ache",
# #         "History of chronic pain, now with acute exacerbation"
# #     ]
    
# #     test_texts = original_tests + complex_tests + edge_cases
    
# #     print("Enhanced Symptom Parser - Comprehensive Testing")
# #     print("=" * 60)
    
# #     total_tests = len(test_texts)
    
# #     print(f"\n🔬 ORIGINAL TEST CASES (1-7)")
# #     print("-" * 40)
# #     for i in range(7):
# #         print(f"\nTest Case {i+1}:")
# #         result = parser.extract_symptoms_from_text(test_texts[i])
# #         print(json.dumps(result, indent=2))
# #         print("-" * 40)
    
# #     print(f"\n🏥 COMPLEX MEDICAL SCENARIOS (8-17)")
# #     print("-" * 40)
# #     for i in range(7, 17):
# #         print(f"\nTest Case {i+1}:")
# #         result = parser.extract_symptoms_from_text(test_texts[i])
# #         print(json.dumps(result, indent=2))
# #         print("-" * 40)
    
# #     print(f"\n⚠️  EDGE CASES & TRICKY SCENARIOS (18-{total_tests})")
# #     print("-" * 40)
# #     for i in range(17, total_tests):
# #         print(f"\nTest Case {i+1}:")
# #         result = parser.extract_symptoms_from_text(test_texts[i])
# #         print(json.dumps(result, indent=2))
# #         print("-" * 40)
    
# #     # Summary statistics
# #     print(f"\n📊 TESTING SUMMARY")
# #     print("=" * 40)
    
# #     total_symptoms = 0
# #     symptoms_with_severity = 0
    
# #     for i, text in enumerate(test_texts, 1):
# #         result = parser.extract_symptoms_from_text(text)
# #         if result['status'] == 'success':
# #             total_symptoms += result['total_symptoms_found']
# #             symptoms_with_severity += sum(1 for s in result['symptoms'] if s['severity'] is not None)
    
# #     print(f"Total test cases: {total_tests}")
# #     print(f"Total symptoms extracted: {total_symptoms}")
# #     print(f"Symptoms with severity detected: {symptoms_with_severity}")
# #     if total_symptoms > 0:
# #         print(f"Severity detection rate: {symptoms_with_severity/total_symptoms*100:.1f}%")

# # if __name__ == "__main__":
# #     main()













# def main():
#     parser = EnhancedSymptomParser()

#     # Combine all your test cases here
#     test_texts = [
#         "Patient has high fever and cough",
#         "The subject reports severe headache and mild nausea", 
#         "Symptoms include fatigue, muscle pain, and occasional dizziness"
#     ]

#     print("Enhanced Symptom Parser - Interactive Testing")
#     print("=" * 60)

#     for i, text in enumerate(test_texts, 1):
#         print(f"\n--- Test Case {i} ---")
#         print(f"Symptom text:\n{text}\n")

#         combined_result = parser.extract_and_collect(text)

#         if combined_result is None:
#             print("Extraction failed for this case.")
#         else:
#             print("Complete structured data collected:")
#             print(combined_result)

#         print("=" * 60)

# if __name__ == "__main__":
#     main()

































































import os
import re
import json
import logging
from typing import Any, List, Dict, Tuple, Optional
from transformers import pipeline

logger = logging.getLogger(__name__)

# Free local inference: downloads the model once, then runs it on this computer.
MODEL_NAME = "d4data/biomedical-ner-all"
_ner_pipeline = None


def get_ner_pipeline():
    """Load the biomedical NER model once and reuse it for later requests."""
    global _ner_pipeline
    if _ner_pipeline is None:
        _ner_pipeline = pipeline(
            "token-classification",
            model=MODEL_NAME,
            aggregation_strategy="simple"
        )
    return _ner_pipeline

class EnhancedSymptomParser:
    def __init__(self):
        # Severity indicators with their normalized forms
        self.severity_patterns = {
            'severe': ['severe', 'extreme', 'intense', 'sharp', 'excruciating', 'unbearable'],
            'acute': ['acute'],
            'chronic': ['chronic', 'persistent', 'constant', 'continuous', 'ongoing'],
            'moderate': ['moderate', 'noticeable', 'significant', 'considerable'],
            'mild': ['mild', 'slight', 'minor', 'low', 'weak', 'light'],
            'high': ['high', 'elevated', 'increased'],
            'occasional': ['occasional', 'intermittent', 'sporadic', 'periodic', 'sometimes'],
            'sudden': ['sudden', 'abrupt', 'rapid', 'quick'],
            'gradual': ['gradual', 'slow', 'progressive']
        }
        
        # Common anatomical and descriptive modifiers
        self.modifiers = [
            'chest', 'head', 'stomach', 'back', 'neck', 'throat', 'eye', 'ear',
            'muscle', 'joint', 'abdominal', 'cardiac', 'respiratory', 'nasal',
            'facial', 'limb', 'leg', 'arm', 'shoulder', 'knee', 'ankle'
        ]
        
        # Common symptom patterns that need expansion
        self.compound_patterns = [
            (r'\b(chest)\s+(pain|ache|discomfort)', r'\1 \2'),
            (r'\b(muscle)\s+(pain|ache|cramp|spasm)', r'\1 \2'),
            (r'\b(back)\s+(pain|ache)', r'\1 \2'),
            (r'\b(head)\s+(ache|pain)', r'head\2'),
            (r'\b(stomach)\s+(pain|ache)', r'\1 \2'),
            (r'\b(shortness)\s+of\s+(breath)', r'\1 of \2'),
            (r'\b(rapid)\s+(heart\s*beat|pulse)', r'\1 \2'),
            (r'\b(difficulty)\s+(breathing|swallowing)', r'\1 \2'),
            (r'\b(loss)\s+of\s+(appetite|consciousness)', r'\1 of \2'),
            (r'\b(occasional)\s+(dizziness|nausea|headache|pain)', r'\2'),  # Extract the symptom, not the modifier
            (r'\b(mild|severe|acute|chronic)\s+(pain|ache|nausea|headache|dizziness|fatigue)', r'\2'),  # Extract symptom
        ]

    def preprocess_text(self, text: str) -> str:
        """Preprocess text to better handle compound symptoms"""
        processed = text
        for pattern, replacement in self.compound_patterns:
            processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)
        return processed

    def extract_severity_for_entity(self, text: str, entity_start: int, entity_end: int, entity_text: str) -> Optional[str]:
        """Extract severity specifically for a given entity with more precise context"""
        # Clean entity text for matching
        clean_entity = re.sub(r'[^\w\s]', '', entity_text.lower()).strip()
        
        # Create sentence-level context (more accurate than fixed window)
        sentences = re.split(r'[.!?;]', text)
        target_sentence = ""
        
        for sentence in sentences:
            if entity_start >= text.find(sentence) and entity_end <= text.find(sentence) + len(sentence):
                target_sentence = sentence.lower()
                break
        
        if not target_sentence:
            # Fallback to window approach
            window_start = max(0, entity_start - 30)
            window_end = min(len(text), entity_end + 30)
            target_sentence = text[window_start:window_end].lower()
        
        # Look for severity modifiers that are close to this specific entity
        # Split into clauses by common separators
        clauses = re.split(r'\s+and\s+|\s*,\s*', target_sentence)
        
        target_clause = ""
        for clause in clauses:
            if clean_entity in clause.lower():
                target_clause = clause
                break
        
        if not target_clause:
            target_clause = target_sentence
            
        # Extract severity from the specific clause containing this entity
        words = re.findall(r'\b\w+\b', target_clause)
        
        # Check for severity patterns, prioritizing closer matches
        for severity, patterns in self.severity_patterns.items():
            for pattern in patterns:
                if pattern in words:
                    # Check if the severity word is reasonably close to entity words
                    entity_word_positions = []
                    severity_positions = []
                    
                    for i, word in enumerate(words):
                        if word in clean_entity.split():
                            entity_word_positions.append(i)
                        if word == pattern:
                            severity_positions.append(i)
                    
                    # If severity is within 4 words of entity, it's likely related
                    for s_pos in severity_positions:
                        for e_pos in entity_word_positions:
                            if abs(s_pos - e_pos) <= 4:
                                return severity
        
        return None

    def find_compound_symptoms(self, text: str) -> List[Dict]:
        """Find compound symptoms using regex patterns"""
        compound_symptoms = []
        
        # First, find "occasional dizziness" type patterns where we want the symptom, not the modifier
        modifier_symptom_pattern = r'\b(occasional|mild|severe|acute|chronic|high|sudden)\s+(dizziness|nausea|headache|pain|fatigue|cough|fever)\b'
        for match in re.finditer(modifier_symptom_pattern, text, re.IGNORECASE):
            modifier = match.group(1)
            symptom = match.group(2)
            compound_symptoms.append({
                'symptom': symptom,  # Just the symptom, not the modifier
                'start': match.start(2),  # Position of symptom only
                'end': match.end(2),
                'confidence_score': 0.98,
                'entity_type': 'Modified_symptom',
                'modifier': modifier  # Store modifier separately
            })
        
        # Then find anatomical + symptom patterns
        for pattern, _ in self.compound_patterns[:-2]:  # Exclude the modifier patterns we handled above
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                compound_symptoms.append({
                    'symptom': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence_score': 0.95,
                    'entity_type': 'Compound_symptom'
                })
        
        return compound_symptoms

    def expand_symptom_with_modifiers(self, text: str, entity_start: int, entity_end: int) -> Tuple[str, int, int]:
        """Expand symptom to include anatomical or descriptive modifiers"""
        entity_text = text[entity_start:entity_end].strip()
        
        # Handle truncated words by looking for complete word boundaries
        if len(entity_text) >= 3:
            # Check if entity seems to be a fragment of a larger word
            # Look backwards to see if this is part of a larger word
            extended_start = entity_start
            while extended_start > 0 and not text[extended_start - 1].isspace():
                extended_start -= 1
            
            full_word = text[extended_start:entity_end].strip()
            
            # If the full word is significantly longer and looks like a medical term, use it
            if len(full_word) > len(entity_text) and len(full_word) <= 20:
                # Check if it's a reasonable medical term (contains the original entity)
                if entity_text.lower() in full_word.lower():
                    entity_text = full_word
                    entity_start = extended_start
        
        # Skip if entity starts with conjunctions or prepositions
        if entity_text.lower().startswith(('and ', 'or ', 'of ', 'in ', 'on ', 'at ', 'with ')):
            # Try to clean it up by removing the conjunction/preposition
            clean_parts = entity_text.split()[1:] if len(entity_text.split()) > 1 else []
            if clean_parts:
                clean_entity = ' '.join(clean_parts)
                # Find the actual start of the clean entity in the text
                clean_start_offset = entity_text.find(clean_parts[0])
                return clean_entity, entity_start + clean_start_offset, entity_end
            else:
                return entity_text, entity_start, entity_end
        
        # Look backwards for modifiers (anatomical terms)
        new_start = entity_start
        words_before = []
        
        # Find start of previous word
        pos = entity_start - 1
        while pos >= 0 and text[pos].isspace():
            pos -= 1
        
        if pos >= 0:
            word_end = pos + 1
            while pos >= 0 and not text[pos].isspace():
                pos -= 1
            
            prev_word = text[pos + 1:word_end].strip()
            if prev_word.lower() in self.modifiers:
                words_before = [prev_word]
                new_start = pos + 1
        
        # Look forward for completions
        new_end = entity_end
        words_after = []
        
        remaining_text = text[entity_end:entity_end + 25].lower()
        
        if entity_text.lower() == "shortness":
            if remaining_text.strip().startswith("of breath"):
                words_after = ["of breath"]
                new_end = entity_end + 10  # len(" of breath")
        elif entity_text.lower() == "rapid":
            if "heartbeat" in remaining_text[:12]:
                words_after = ["heartbeat"]
                new_end = entity_end + len(" heartbeat")
            elif "heart beat" in remaining_text[:15]:
                words_after = ["heart beat"]  
                new_end = entity_end + len(" heart beat")
        elif entity_text.lower() == "loss":
            match = re.match(r'\s+of\s+(\w+)', remaining_text)
            if match:
                words_after = [f"of {match.group(1)}"]
                new_end = entity_end + len(match.group(0))
        
        # Construct the expanded symptom
        expanded_parts = words_before + [entity_text] + words_after
        expanded_symptom = " ".join(expanded_parts).strip()
        
        return expanded_symptom, new_start, new_end

    def extract_symptoms_from_text(self, text: str) -> Dict:
        """Extract symptoms with severity and return structured JSON"""
        if not isinstance(text, str):
            return {
                "status": "error",
                "error_message": "Input text must be a string.",
                "symptoms": [],
            }
        if not text.strip():
            return {
                "status": "success",
                "input_text": text,
                "total_symptoms_found": 0,
                "symptoms": [],
            }
        if len(text) > 10000:
            return {
                "status": "error",
                "error_message": "Input text exceeds the 10,000 character limit.",
                "symptoms": [],
            }

        # Preprocess text for better compound detection
        processed_text = self.preprocess_text(text)
        
        # First, find compound symptoms using rules
        compound_symptoms = self.find_compound_symptoms(text)
        
        try:
            # Run inference locally; no hosted API credits or token are needed.
            entities = get_ner_pipeline()(text)

            # The model emits both symptoms and diseases. Diseases are not patient
            # symptoms and must not be passed into the diagnosis stage as such.
            relevant_entities = []
            if entities:
                for ent in entities:
                    if not isinstance(ent, dict):
                        continue
                    entity_group = str(ent.get('entity_group', ent.get('entity', ''))).upper()
                    normalized_group = entity_group.replace("-", "_").replace(" ", "_")
                    if normalized_group == 'SYMPTOM' or 'SYMPTOM' in normalized_group:
                        relevant_entities.append(ent)

            # Combine NER entities with compound symptoms
            all_symptoms = []
            processed_spans = set()
            
            # Process compound symptoms first (higher priority)
            for comp_symp in compound_symptoms:
                span_key = f"{comp_symp['start']}-{comp_symp['end']}"
                processed_spans.add(span_key)
                
                # For modified symptoms, extract severity from the stored modifier
                if 'modifier' in comp_symp:
                    severity = comp_symp['modifier'].lower()
                    # Map modifier to our severity categories
                    if severity in ['occasional', 'mild', 'severe', 'acute', 'chronic', 'high', 'sudden']:
                        mapped_severity = severity
                    else:
                        mapped_severity = self.extract_severity_for_entity(
                            text, comp_symp['start'], comp_symp['end'], comp_symp['symptom']
                        )
                else:
                    mapped_severity = self.extract_severity_for_entity(
                        text, comp_symp['start'], comp_symp['end'], comp_symp['symptom']
                    )
                
                symptom_data = {
                    "symptom": comp_symp['symptom'],
                    "severity": mapped_severity,
                    "confidence_score": comp_symp['confidence_score'],
                    "entity_type": comp_symp['entity_type'],
                    "position": {
                        "start": comp_symp['start'],
                        "end": comp_symp['end']
                    }
                }
                symptom_data.update(self._context_status(
                    text, comp_symp['start'], comp_symp['end']
                ))
                all_symptoms.append(symptom_data)
            
            # Process NER entities
            for ent in relevant_entities:
                start = ent['start']
                end = ent['end']
                
                # Check for overlaps with compound symptoms
                overlaps = False
                for comp_start, comp_end in [
                    (int(span.split('-')[0]), int(span.split('-')[1])) 
                    for span in processed_spans
                ]:
                    if not (end <= comp_start or start >= comp_end):
                        overlaps = True
                        break
                
                if overlaps:
                    continue
                
                # Expand symptom with context
                expanded_symptom, new_start, new_end = self.expand_symptom_with_modifiers(text, start, end)
                
                # Extract severity for this specific entity
                severity = self.extract_severity_for_entity(text, start, end, expanded_symptom)
                
                # Clean up the symptom text
                cleaned_symptom = re.sub(r'\s+', ' ', expanded_symptom).strip()
                
                if cleaned_symptom and len(cleaned_symptom) > 1:
                    symptom_data = {
                        "symptom": cleaned_symptom,
                        "severity": severity,
                        "confidence_score": round(ent.get('score', 0), 3),
                        "entity_type": ent.get('entity_group'),
                        "position": {
                            "start": new_start,
                            "end": new_end
                        },
                    }
                    symptom_data.update(self._context_status(text, new_start, new_end))
                    all_symptoms.append(symptom_data)
            
            # Remove duplicates and filter out poor quality extractions
            seen_symptoms = {}
            unique_symptoms = []
            
            for symptom in all_symptoms:
                symptom_key = symptom['symptom'].lower().strip()
                
                # Skip very short or invalid symptoms
                if len(symptom_key) <= 2 or not symptom_key:
                    continue
                    
                # Skip symptoms that are just conjunctions or fragments
                if symptom_key in ['and', 'or', 'of', 'in', 'on', 'at', 'with', 'di', 'the']:
                    continue
                
                # Handle duplicates by keeping the one with higher confidence
                if symptom_key in seen_symptoms:
                    existing = seen_symptoms[symptom_key]
                    if symptom['confidence_score'] > existing['confidence_score']:
                        # Remove the old one and add the new one
                        unique_symptoms = [s for s in unique_symptoms if s['symptom'].lower().strip() != symptom_key]
                        unique_symptoms.append(symptom)
                        seen_symptoms[symptom_key] = symptom
                else:
                    seen_symptoms[symptom_key] = symptom
                    unique_symptoms.append(symptom)

            # Remove nested NER spans while retaining the richer compound span.
            unique_symptoms = [
                symptom for symptom in unique_symptoms
                if not any(
                    symptom is not other
                    and symptom["position"]["start"] >= other["position"]["start"]
                    and symptom["position"]["end"] <= other["position"]["end"]
                    and (
                        symptom["position"]["start"] != other["position"]["start"]
                        or symptom["position"]["end"] != other["position"]["end"]
                    )
                    for other in unique_symptoms
                )
            ]
            
            # Sort by confidence score (descending)
            unique_symptoms.sort(key=lambda x: x['confidence_score'], reverse=True)
            
            return {
                "status": "success",
                "input_text": text,
                "total_symptoms_found": len(unique_symptoms),
                "symptoms": unique_symptoms
            }
            
        except Exception as e:
            logger.exception("Local symptom inference failed")
            return {
                "status": "error", 
                "error_message": f"Processing failed: {str(e)}",
                "symptoms": []
            }

    def _context_status(self, text: str, start: int, end: int) -> Dict[str, Any]:
        """Return conservative assertion metadata without treating absence as negation."""
        context = text[max(0, start - 60):min(len(text), end + 30)].lower()
        before = text[max(0, start - 45):start].lower()
        negated = bool(re.search(
            r"\b(?:no|not|never|without|denies|deny|doesn't|don't|didn't|hasn't|haven't)\b"
            r"(?:\W+\w+){0,3}\W*$",
            before,
        ))
        uncertain = bool(re.search(
            r"\b(?:might|may|maybe|possibly|possible|疑似|could|perhaps)\b",
            context,
        ))
        historical = bool(re.search(
            r"\b(?:history of|previously|had|was having|resolved|gone away|last week|yesterday)\b",
            context,
        ))
        status = "negated" if negated else "uncertain" if uncertain else "historical" if historical else "present"
        return {
            "assertion": status,
            "negated": negated,
            "uncertain": uncertain,
            "historical": historical,
        }



    def collect_demographics_and_history_interactive(self):
        # Interactive prompts for age/gender/height/weight/allergies/past_diseases/medications
        data = {
            "age": None,
            "gender": None,
            "height": None,
            "weight": None,
            "allergies": [],
            "past_diseases": [],
            "medications": []
        }
        data["age"] = input("Please enter your age (years): ").strip()
        data["gender"] = input("Please enter your gender (male/female/other): ").strip()
        data["height"] = input("Please enter your height with units (e.g. 170cm or 5'8\"): ").strip()
        data["weight"] = input("Please enter your weight with units (e.g. 70kg or 150lbs): ").strip()
        allergies = input("List any allergies (comma-separated): ").strip()
        data["allergies"] = [a.strip() for a in allergies.split(",") if a.strip()]
        past_diseases = input("List any past diseases or medical conditions (comma-separated): ").strip()
        data["past_diseases"] = [d.strip() for d in past_diseases.split(",") if d.strip()]
        medications = input("List any ongoing medications (comma-separated): ").strip()
        data["medications"] = [m.strip() for m in medications.split(",") if m.strip()]
        return data

    def extract_and_collect(self, text: str):
        # Runs your symptom extraction, then interactively gathers extra info
        symptom_result = self.extract_symptoms_from_text(text)
        if symptom_result["status"] != "success":
            print("Error extracting symptoms:", symptom_result.get("error_message"))
            return None
        collected = {
            "symptoms": symptom_result["symptoms"],
            "demographics": {},
            "allergies": [],
            "past_diseases": [],
            "medications": [],
        }
        interactive_data = self.collect_demographics_and_history_interactive()
        collected["demographics"]["age"] = interactive_data["age"]
        collected["demographics"]["gender"] = interactive_data["gender"]
        collected["demographics"]["height"] = interactive_data["height"]
        collected["demographics"]["weight"] = interactive_data["weight"]
        collected["allergies"] = interactive_data["allergies"]
        collected["past_diseases"] = interactive_data["past_diseases"]
        collected["medications"] = interactive_data["medications"]

        return collected

# def main():
#     parser = EnhancedSymptomParser()
    
#     # Original test cases
#     original_tests = [
#         "Patient has high fever and cough",
#         "The subject reports severe headache and mild nausea", 
#         "Symptoms include fatigue, muscle pain, and occasional dizziness",
#         "She complained of chest pain and shortness of breath",
#         "The patient experiences rash and swelling around the eyes",
#         "He has chronic back pain and acute abdominal discomfort",
#         "Patient presents with sudden onset of severe chest pain and rapid heartbeat"
#     ]
    
#     # Additional complex test cases
#     complex_tests = [
#         "The 45-year-old male presents with severe crushing chest pain radiating to left arm, profuse sweating, and mild nausea",
#         "Patient reports chronic lower back pain, intermittent leg cramps, and occasional numbness in fingers",
#         "She has been experiencing persistent headaches, blurred vision, and episodes of sudden dizziness for the past week",
#         "Symptoms include high-grade fever (102°F), chills, body aches, dry cough, and loss of appetite",
#         "The child has developed a widespread rash, swollen lymph nodes, sore throat, and difficulty swallowing",
#         "Patient complains of sharp abdominal pain in right lower quadrant, vomiting, and low-grade fever",
#         "He reports progressive muscle weakness, joint stiffness in the morning, and chronic fatigue",
#         "The elderly woman presents with confusion, memory loss, tremors, and difficulty with balance",
#         "Acute onset of severe headache, neck stiffness, photophobia, and high fever",
#         "Patient has been having palpitations, excessive sweating, anxiety attacks, and insomnia for 3 months"
#     ]
    
#     # Edge cases and tricky scenarios
#     edge_cases = [
#         "No pain, no fever, no cough - patient feels completely normal",
#         "Mild to moderate pain that comes and goes",
#         "Severe pain 8/10, worse with movement, better with rest",
#         "The pain is described as burning, stabbing, and throbbing",
#         "Patient denies chest pain but admits to pressure and tightness",
#         "Intermittent sharp pain versus constant dull ache",
#         "History of chronic pain, now with acute exacerbation"
#     ]
    
#     test_texts = original_tests + complex_tests + edge_cases
    
#     print("Enhanced Symptom Parser - Comprehensive Testing")
#     print("=" * 60)
    
#     total_tests = len(test_texts)
    
#     print(f"\n🔬 ORIGINAL TEST CASES (1-7)")
#     print("-" * 40)
#     for i in range(7):
#         print(f"\nTest Case {i+1}:")
#         result = parser.extract_symptoms_from_text(test_texts[i])
#         print(json.dumps(result, indent=2))
#         print("-" * 40)
    
#     print(f"\n🏥 COMPLEX MEDICAL SCENARIOS (8-17)")
#     print("-" * 40)
#     for i in range(7, 17):
#         print(f"\nTest Case {i+1}:")
#         result = parser.extract_symptoms_from_text(test_texts[i])
#         print(json.dumps(result, indent=2))
#         print("-" * 40)
    
#     print(f"\n⚠️  EDGE CASES & TRICKY SCENARIOS (18-{total_tests})")
#     print("-" * 40)
#     for i in range(17, total_tests):
#         print(f"\nTest Case {i+1}:")
#         result = parser.extract_symptoms_from_text(test_texts[i])
#         print(json.dumps(result, indent=2))
#         print("-" * 40)
    
#     # Summary statistics
#     print(f"\n📊 TESTING SUMMARY")
#     print("=" * 40)
    
#     total_symptoms = 0
#     symptoms_with_severity = 0
    
#     for i, text in enumerate(test_texts, 1):
#         result = parser.extract_symptoms_from_text(text)
#         if result['status'] == 'success':
#             total_symptoms += result['total_symptoms_found']
#             symptoms_with_severity += sum(1 for s in result['symptoms'] if s['severity'] is not None)
    
#     print(f"Total test cases: {total_tests}")
#     print(f"Total symptoms extracted: {total_symptoms}")
#     print(f"Symptoms with severity detected: {symptoms_with_severity}")
#     if total_symptoms > 0:
#         print(f"Severity detection rate: {symptoms_with_severity/total_symptoms*100:.1f}%")

# if __name__ == "__main__":
#     main()













def main():
    parser = EnhancedSymptomParser()

    # Combine all your test cases here
    test_texts = [
        "Patient has high fever and cough",
        "The subject reports severe headache and mild nausea", 
        "Symptoms include fatigue, muscle pain, and occasional dizziness"
    ]

    print("Enhanced Symptom Parser - Interactive Testing")
    print("=" * 60)

    for i, text in enumerate(test_texts, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Symptom text:\n{text}\n")

        combined_result = parser.extract_and_collect(text)

        if combined_result is None:
            print("Extraction failed for this case.")
        else:
            print("Complete structured data collected:")
            print(combined_result)

        print("=" * 60)

if __name__ == "__main__":
    main()







