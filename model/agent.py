# import asyncio
# import logging
# from typing import Dict, List, Any
# from datetime import datetime
# import speech_recognition as sr
# import pyttsx3
# import threading
# import time
# import queue

# # Import all the agents
# from symptoms import EnhancedSymptomParser
# from diagnosis import DiagnosisAgent
# from literature_agent import LiteratureAgent
# from case_study_agent import CaseStudyAgent
# from explainability import ExplainabilityAgent

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class OrchestratorAgent:
#     """
#     Main orchestrator that connects all agents in the specified flow:
#     1. Takes natural language input (voice or text)
#     2. Sends to symptom agent for extraction
#     3. Sends extracted data to diagnosis agent
#     4. Sends diagnosis results to literature and case study agents
#     5. Sends all outputs to explainability agent
#     6. Returns final processed output (voice and text)
#     """
    
#     def __init__(self):
#         self.name = "OrchestratorAgent"
#         self.version = "1.0.0"
        
#         # Initialize all agents
#         self.symptom_parser = EnhancedSymptomParser()
#         self.diagnosis_agent = DiagnosisAgent()
#         self.literature_agent = LiteratureAgent()
#         self.case_study_agent = CaseStudyAgent()
#         self.explainability_agent = ExplainabilityAgent()
        
#         # Initialize voice components
#         self.recognizer = sr.Recognizer()
#         self.microphone = sr.Microphone()
#         self.tts_engine = pyttsx3.init()
#         self.voice_queue = queue.Queue()
#         self.is_speaking = False
        
#         # Configure TTS engine
#         self._configure_tts()
        
#         logger.info("OrchestratorAgent initialized with all sub-agents and voice capabilities")
    
#     def _configure_tts(self):
#         """Configure the text-to-speech engine"""
#         try:
#             voices = self.tts_engine.getProperty('voices')
#             if voices:
#                 # Try to find a female voice (usually index 1)
#                 if len(voices) > 1:
#                     self.tts_engine.setProperty('voice', voices[1].id)
#                 else:
#                     self.tts_engine.setProperty('voice', voices[0].id)
            
#             # Set speech rate and volume
#             self.tts_engine.setProperty('rate', 150)  # Speed of speech
#             self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
#             logger.info("TTS engine configured successfully")
#         except Exception as e:
#             logger.warning(f"Could not configure TTS engine: {e}")
    
#     def listen_for_voice_input(self, timeout=5, phrase_time_limit=10):
#         """
#         Listen for voice input and convert to text
        
#         Args:
#             timeout: Time to wait for speech to start
#             phrase_time_limit: Maximum time to listen for a phrase
            
#         Returns:
#             str: Transcribed text or None if failed
#         """
#         try:
#             print("\n🎤 Listening for voice input... (Speak now)")
#             print("=" * 60)
            
#             with self.microphone as source:
#                 # Adjust for ambient noise
#                 self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
#                 # Listen for audio
#                 audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
#             print("🔄 Processing speech...")
            
#             # Recognize speech using Google Speech Recognition
#             text = self.recognizer.recognize_google(audio)
            
#             print(f"📝 You said: {text}")
#             print("=" * 60)
            
#             return text
            
#         except sr.WaitTimeoutError:
#             print("⏰ No speech detected within timeout period")
#             return None
#         except sr.UnknownValueError:
#             print("❌ Could not understand the audio")
#             return None
#         except sr.RequestError as e:
#             print(f"❌ Speech recognition service error: {e}")
#             return None
#         except Exception as e:
#             print(f"❌ Error during voice recognition: {e}")
#             return None
    
#     def speak_text(self, text: str, display_text: bool = True):
#         """
#         Convert text to speech and speak it
        
#         Args:
#             text: Text to speak
#             display_text: Whether to display the text as subtitles
#         """
#         if not text:
#             return
        
#         try:
#             if display_text:
#                 print(f"\n🔊 Speaking: {text}")
#                 print("=" * 60)
            
#             # Speak the text
#             self.tts_engine.say(text)
#             self.tts_engine.runAndWait()
            
#             if display_text:
#                 print("✅ Finished speaking")
#                 print("=" * 60)
                
#         except Exception as e:
#             print(f"❌ Error during speech synthesis: {e}")
    
#     def format_voice_output(self, result: Dict[str, Any]) -> str:
#         """
#         Format the diagnosis result for voice output
        
#         Args:
#             result: Complete diagnosis result from orchestrator
            
#         Returns:
#             str: Formatted text for voice output
#         """
#         if result["status"] != "success":
#             return "Sorry, I encountered an error while processing your symptoms. Please try again."
        
#         # Get top diagnosis
#         top_diagnosis = result.get('top_diagnosis', {})
#         condition = top_diagnosis.get('condition', 'Unknown')
#         confidence = top_diagnosis.get('confidence', '0%')
        
#         # Get recommendations
#         recommendations = top_diagnosis.get('recommendations', {})
#         medications = recommendations.get('medications', [])
#         precautions = recommendations.get('precautions', [])
#         exercises = recommendations.get('exercises', [])
#         diet = recommendations.get('diet', [])
        
#         # Get all diagnoses
#         all_diagnoses = result.get('top_5_diagnoses_with_confidence', [])
        
#         # Format voice output
#         voice_text = f"Based on your symptoms, the most likely diagnosis is {condition} with {confidence} confidence. "
        
#         # Add medications if available
#         if medications and medications[0] != "No medications data found.":
#             meds_text = ", ".join(medications[:3])  # Limit to first 3
#             voice_text += f"Recommended medications include: {meds_text}. "
        
#         # Add precautions if available
#         if precautions and precautions[0] != "No precautions data found.":
#             prec_text = ", ".join(precautions[:3])  # Limit to first 3
#             voice_text += f"Important precautions: {prec_text}. "
        
#         # Add exercises if available
#         if exercises and exercises[0] != "No exercises data found.":
#             ex_text = ", ".join(exercises[:3])  # Limit to first 3
#             voice_text += f"Recommended exercises: {ex_text}. "
        
#         # Add diet if available
#         if diet and diet[0] != "No diet data found.":
#             diet_text = ", ".join(diet[:3])  # Limit to first 3
#             voice_text += f"Dietary recommendations: {diet_text}. "
        
#         # Add other possible diagnoses
#         if len(all_diagnoses) > 1:
#             other_diagnoses = [d['condition'] for d in all_diagnoses[1:3]]  # Next 2 diagnoses
#             voice_text += f"Other possible conditions include: {', '.join(other_diagnoses)}. "
        
#         # Add validation summaries if available
#         lit_validation = result.get('literature_validation_summary', '')
#         case_validation = result.get('case_study_validation_summary', '')
        
#         if lit_validation and lit_validation != "No literature data.":
#             # Truncate long validation text
#             lit_short = lit_validation[:200] + "..." if len(lit_validation) > 200 else lit_validation
#             voice_text += f"Medical literature supports this diagnosis: {lit_short}. "
        
#         if case_validation and case_validation != "No detailed case studies validation available.":
#             # Truncate long validation text
#             case_short = case_validation[:200] + "..." if len(case_validation) > 200 else case_validation
#             voice_text += f"Similar cases have been reported: {case_short}. "
        
#         voice_text += "Please consult with a healthcare professional for proper medical advice. Thank you."
        
#         return voice_text
    
#     def display_detailed_results(self, result: Dict[str, Any]):
#         """
#         Display detailed results on screen with subtitles
        
#         Args:
#             result: Complete diagnosis result from orchestrator
#         """
#         if result["status"] != "success":
#             print(f"\n❌ Error: {result.get('error_message', 'Unknown error')}")
#             return
        
#         print("\n" + "=" * 80)
#         print("📋 DETAILED DIAGNOSIS RESULTS")
#         print("=" * 80)
        
#         # Display symptoms
#         symptoms = result.get('symptom_extraction', {}).get('extracted_symptoms', [])
#         print(f"\n🔍 EXTRACTED SYMPTOMS ({len(symptoms)} found):")
#         for i, symptom in enumerate(symptoms, 1):
#             severity = f" (severity: {symptom['severity']})" if symptom.get('severity') else ""
#             print(f"  {i}. {symptom['symptom']}{severity} (confidence: {symptom['confidence_score']:.2f})")
        
#         # Display top diagnosis
#         top_diagnosis = result.get('top_diagnosis', {})
#         print(f"\n🏥 TOP DIAGNOSIS:")
#         print(f"  Condition: {top_diagnosis.get('condition', 'N/A')}")
#         print(f"  Confidence: {top_diagnosis.get('confidence', 'N/A')}")
        
#         # Display recommendations
#         recommendations = top_diagnosis.get('recommendations', {})
#         if recommendations:
#             print(f"\n💊 RECOMMENDATIONS:")
#             for category, items in recommendations.items():
#                 if items and items[0] != f"No {category} data found.":
#                     print(f"  {category.upper()}:")
#                     for item in items:
#                         print(f"    • {item}")
        
#         # Display all diagnoses
#         all_diagnoses = result.get('top_5_diagnoses_with_confidence', [])
#         if all_diagnoses:
#             print(f"\n📊 ALL DIAGNOSES WITH CONFIDENCE SCORES:")
#             for i, diag in enumerate(all_diagnoses, 1):
#                 print(f"  {i}. {diag.get('condition', 'N/A')} - {diag.get('confidence', 'N/A')}")
        
#         # Display validation summaries
#         lit_validation = result.get('literature_validation_summary', '')
#         if lit_validation and lit_validation != "No literature data.":
#             print(f"\n📚 LITERATURE VALIDATION:")
#             print(f"  {lit_validation}")
        
#         case_validation = result.get('case_study_validation_summary', '')
#         if case_validation and case_validation != "No detailed case studies validation available.":
#             print(f"\n📋 CASE STUDY VALIDATION:")
#             print(f"  {case_validation}")
        
#         print("\n" + "=" * 80)
    
#     async def process_voice_input(self, timeout=5, phrase_time_limit=10) -> Dict[str, Any]:
#         """
#         Process voice input through the complete diagnosis pipeline
        
#         Args:
#             timeout: Time to wait for speech to start
#             phrase_time_limit: Maximum time to listen for a phrase
            
#         Returns:
#             Dict: Complete diagnosis result
#         """
#         # Step 1: Listen for voice input
#         voice_input = self.listen_for_voice_input(timeout, phrase_time_limit)
        
#         if not voice_input:
#             return {
#                 "status": "error",
#                 "error_message": "No voice input detected or recognition failed"
#             }
        
#         # Step 2: Process through orchestrator
#         print("\n🔄 Processing your symptoms through AI diagnosis system...")
#         result = await self.process_natural_language_input(voice_input)
        
#         # Step 3: Display detailed results
#         self.display_detailed_results(result)
        
#         # Step 4: Generate and speak voice output
#         if result["status"] == "success":
#             voice_output = self.format_voice_output(result)
#             self.speak_text(voice_output, display_text=True)
        
#         return result
    
#     async def process_natural_language_input(self, natural_language_input: str) -> Dict[str, Any]:
#         """
#         Main processing function that orchestrates all agents
        
#         Args:
#             natural_language_input: Natural language description of symptoms/condition
            
#         Returns:
#             Final processed output with all agent results
#         """
#         try:
#             logger.info(f"Processing natural language input: {natural_language_input[:100]}...")
            
#             # Step 1: Extract symptoms from natural language
#             logger.info("Step 1: Extracting symptoms from natural language input")
#             symptom_result = self.symptom_parser.extract_symptoms_from_text(natural_language_input)
            
#             if symptom_result["status"] != "success":
#                 logger.error(f"Symptom extraction failed: {symptom_result.get('error_message', 'Unknown error')}")
#                 return {
#                     "status": "error",
#                     "error_message": "Failed to extract symptoms from input",
#                     "symptom_extraction_result": symptom_result
#                 }
            
#             # Prepare data for diagnosis agent
#             diagnosis_input = {
#                 'symptoms': symptom_result["symptoms"],
#                 'demographics': {},  # Will be filled with default values
#                 'allergies': ['no'],
#                 'past_diseases': ['no'],
#                 'medications': ['no']
#             }
            
#             # Step 2: Get diagnosis from diagnosis agent
#             logger.info("Step 2: Getting diagnosis from diagnosis agent")
#             diagnoses = await self.diagnosis_agent.diagnose(diagnosis_input)
            
#             if not diagnoses:
#                 logger.warning("No diagnoses returned from diagnosis agent")
#                 diagnoses = []
            
#             # Step 3: Get literature validation
#             logger.info("Step 3: Getting literature validation")
#             await self.literature_agent._load_models()
#             literature_input = {
#                 'initial_diagnoses': diagnoses,
#                 'extracted_symptoms': symptom_result["symptoms"]
#             }
#             literature_result = await self.literature_agent.process(literature_input)
            
#             # Step 4: Get case study validation
#             logger.info("Step 4: Getting case study validation")
#             await self.case_study_agent._load_models()
#             case_study_input = {
#                 'initial_diagnoses': diagnoses,
#                 'extracted_symptoms': symptom_result["symptoms"]
#             }
#             # Load case study data for the diagnosed conditions
#             condition_names = [diag['condition'] for diag in diagnoses]
#             await self.case_study_agent._load_data(condition_names)
#             case_study_result = await self.case_study_agent.process(case_study_input)
            
#             # Step 5: Generate explainability output
#             logger.info("Step 5: Generating explainability output")
#             await self.explainability_agent.start_session()
            
#             explainability_input = {
#                 'diagnoses': diagnoses,
#                 'literature': literature_result.get('literature_evidence', []),
#                 'cases': case_study_result.get('case_studies', [])
#             }
#             explainability_result = await self.explainability_agent.run(explainability_input)
            
#             # Step 6: Compile final output
#             logger.info("Step 6: Compiling final output")
#             final_output = {
#                 "status": "success",
#                 "input_text": natural_language_input,
#                 "timestamp": datetime.now().isoformat(),
#                 "orchestrator_metadata": {
#                     "agent_name": self.name,
#                     "version": self.version,
#                     "processing_steps": [
#                         "symptom_extraction",
#                         "diagnosis",
#                         "literature_validation", 
#                         "case_study_validation",
#                         "explainability_generation"
#                     ]
#                 },
#                 "symptom_extraction": {
#                     "extracted_symptoms": symptom_result["symptoms"],
#                     "total_symptoms_found": symptom_result["total_symptoms_found"]
#                 },
#                 "diagnosis_results": {
#                     "top_5_diagnoses": diagnoses[:5],
#                     "total_diagnoses": len(diagnoses)
#                 },
#                 "literature_validation": {
#                     "literature_evidence": literature_result.get('literature_evidence', []),
#                     "validation_metadata": literature_result.get('validation_metadata', {})
#                 },
#                 "case_study_validation": {
#                     "case_studies": case_study_result.get('case_studies', []),
#                     "metadata": case_study_result.get('metadata', {})
#                 },
#                 "explainability_output": explainability_result,
#                 # Return individual components as requested
#                 "top_diagnosis": explainability_result.get("top_diagnosis", {}),
#                 "top_5_diagnoses_with_confidence": explainability_result.get("top_5_diagnoses", []),
#                 "literature_validation_summary": explainability_result.get("literature_validation", ""),
#                 "case_study_validation_summary": explainability_result.get("case_study_validation", "")
#             }
            
#             # Cleanup
#             await self.literature_agent.cleanup()
#             await self.case_study_agent.cleanup()
#             await self.explainability_agent.close_session()
            
#             logger.info("Processing completed successfully")
#             return final_output
            
#         except Exception as e:
#             logger.error(f"Error in orchestrator processing: {str(e)}")
#             return {
#                 "status": "error",
#                 "error_message": f"Processing failed: {str(e)}",
#                 "timestamp": datetime.now().isoformat()
#             }
    
#     async def cleanup(self):
#         """Cleanup all agent resources"""
#         try:
#             await self.literature_agent.cleanup()
#             await self.case_study_agent.cleanup()
#             await self.explainability_agent.close_session()
#             logger.info("All agents cleaned up successfully")
#         except Exception as e:
#             logger.error(f"Error during cleanup: {str(e)}")

# async def main():
#     """Main function with voice bot interface"""
#     orchestrator = OrchestratorAgent()
    
#     print("=" * 80)
#     print("🎤 DIAGNOSURE VOICE - AI MEDICAL DIAGNOSIS BOT")
#     print("=" * 80)
#     print("Welcome! I'm your AI medical diagnosis assistant.")
#     print("I can help you get a preliminary diagnosis based on your symptoms.")
#     print("\nChoose your input method:")
#     print("1. Voice Input (Speak your symptoms)")
#     print("2. Text Input (Type your symptoms)")
#     print("3. Test Mode (Use predefined symptoms)")
#     print("4. Continuous Voice Bot (Keep listening for symptoms)")
    
#     try:
#         choice = input("\nEnter your choice (1, 2, 3, or 4): ").strip()
        
#         if choice == "1":
#             # Voice input mode
#             print("\n🎤 VOICE INPUT MODE")
#             print("I'll listen for your symptoms and provide a voice response.")
#             print("Make sure your microphone is working and speak clearly.")
            
#             result = await orchestrator.process_voice_input(timeout=10, phrase_time_limit=15)
            
#         elif choice == "2":
#             # Text input mode
#             print("\n📝 TEXT INPUT MODE")
#             symptoms_text = input("Please describe your symptoms: ").strip()
            
#             if not symptoms_text:
#                 print("❌ No symptoms provided. Exiting.")
#                 return
            
#             print(f"\n🔄 Processing: {symptoms_text}")
#             result = await orchestrator.process_natural_language_input(symptoms_text)
            
#             # Display results
#             orchestrator.display_detailed_results(result)
            
#             # Speak the results
#             if result["status"] == "success":
#                 voice_output = orchestrator.format_voice_output(result)
#                 orchestrator.speak_text(voice_output, display_text=True)
        
#         elif choice == "3":
#             # Test mode
#             print("\n🧪 TEST MODE")
#             test_input = "I have been experiencing severe headache, high fever, and occasional dizziness for the past 3 days. I also feel very tired and have muscle pain."
            
#             print(f"Using test input: {test_input}")
#             print("\n🔄 Processing...")
            
#             result = await orchestrator.process_natural_language_input(test_input)
            
#             # Display results
#             orchestrator.display_detailed_results(result)
            
#             # Speak the results
#             if result["status"] == "success":
#                 voice_output = orchestrator.format_voice_output(result)
#                 orchestrator.speak_text(voice_output, display_text=True)
        
#         elif choice == "4":
#             # Continuous voice bot mode
#             await voice_bot_mode()
#             return
        
#         else:
#             print("❌ Invalid choice. Exiting.")
#             return
        
#         # Final status
#         if result["status"] == "success":
#             print(f"\n✅ Diagnosis completed successfully!")
#             print("📋 All results have been displayed and spoken.")
#         else:
#             print(f"\n❌ Diagnosis failed: {result.get('error_message', 'Unknown error')}")
            
#     except KeyboardInterrupt:
#         print("\n\n👋 Goodbye! Thanks for using Diagnosure Voice.")
#     except Exception as e:
#         print(f"\n❌ Error during processing: {str(e)}")
#     finally:
#         await orchestrator.cleanup()
    
#     print("\n" + "=" * 80)
#     print("🎤 DIAGNOSURE VOICE SESSION COMPLETE")
#     print("=" * 80)

# async def voice_bot_mode():
#     """Continuous voice bot mode"""
#     orchestrator = OrchestratorAgent()
    
#     print("=" * 80)
#     print("🎤 DIAGNOSURE VOICE - CONTINUOUS VOICE BOT MODE")
#     print("=" * 80)
#     print("I'm ready to listen for your symptoms continuously.")
#     print("Say 'quit' or 'exit' to stop the bot.")
#     print("Press Ctrl+C to force exit.")
    
#     try:
#         while True:
#             print(f"\n{'='*60}")
#             print("🎤 Listening for your symptoms...")
            
#             result = await orchestrator.process_voice_input(timeout=5, phrase_time_limit=10)
            
#             if result["status"] == "error":
#                 if "No voice input detected" in result.get("error_message", ""):
#                     print("⏰ No speech detected. I'll keep listening...")
#                     continue
#                 else:
#                     print(f"❌ Error: {result.get('error_message')}")
#                     continue
            
#             # Check for exit commands
#             voice_input = result.get('input_text', '').lower()
#             if any(word in voice_input for word in ['quit', 'exit', 'stop', 'bye', 'goodbye']):
#                 print("\n👋 Goodbye! Thanks for using Diagnosure Voice.")
#                 break
            
#             print("\n🔄 Ready for next symptoms...")
            
#     except KeyboardInterrupt:
#         print("\n\n👋 Goodbye! Thanks for using Diagnosure Voice.")
#     except Exception as e:
#         print(f"\n❌ Error in voice bot mode: {str(e)}")
#     finally:
#         await orchestrator.cleanup()

# if __name__ == "__main__":
#     asyncio.run(main())











import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import threading
import queue

try:
    from .symptoms import EnhancedSymptomParser
    from .diagnosis import DiagnosisAgent
    from .literature_agent import LiteratureAgent
    from .case_study_agent import CaseStudyAgent
    from .explainability import ExplainabilityAgent
except ImportError:
    from symptoms import EnhancedSymptomParser
    from diagnosis import DiagnosisAgent
    from literature_agent import LiteratureAgent
    from case_study_agent import CaseStudyAgent
    from explainability import ExplainabilityAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self, enable_voice=True):
        self.name = "OrchestratorAgent"
        self.version = "1.0.0"

        # Initialize all agents
        self.symptom_parser = EnhancedSymptomParser()
        self.diagnosis_agent = DiagnosisAgent()
        self.literature_agent = LiteratureAgent()
        self.case_study_agent = CaseStudyAgent()
        self.explainability_agent = ExplainabilityAgent()

        # Voice components are optional so the text pipeline can run on a server.
        self.voice_enabled = enable_voice
        self.recognizer = sr.Recognizer() if enable_voice else None
        self.microphone = sr.Microphone() if enable_voice else None
        self.tts_engine = pyttsx3.init() if enable_voice else None
        self.voice_queue = queue.Queue()
        self.stop_listening_flag = threading.Event()

        if self.voice_enabled:
            self._configure_tts()
        logger.info("OrchestratorAgent initialized with all sub-agents and voice capabilities")

    def _configure_tts(self):
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            logger.info("TTS engine configured successfully")
        except Exception as e:
            logger.warning(f"Could not configure TTS engine: {e}")

    def listen_for_voice_input(self) -> str:
        """Listen for voice input with manual stop control"""
        print("\n🎤 Listening for voice input... (Press Enter to stop recording)")
        print("=" * 60)
        self.stop_listening_flag.clear()
        
        # Clear any old items in queue
        while not self.voice_queue.empty():
            try:
                self.voice_queue.get_nowait()
            except:
                break

        def listen_thread():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_chunks = []
                    print("🔴 Recording started. Speak now...")
                    
                    while not self.stop_listening_flag.is_set():
                        try:
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                            audio_chunks.append(audio)
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            print(f"Audio capture error: {e}")
                            break
                    
                    print("🛑 Recording stopped.")
                    
                    if not audio_chunks:
                        self.voice_queue.put(None)
                        return
                        
                    # Process audio chunks
                    texts = []
                    for chunk in audio_chunks:
                        try:
                            text = self.recognizer.recognize_google(chunk)
                            if text.strip():
                                texts.append(text)
                        except sr.UnknownValueError:
                            continue
                        except sr.RequestError as e:
                            print(f"Speech recognition error: {e}")
                            continue
                        except Exception as e:
                            print(f"Recognition error: {e}")
                            continue
                            
                    full_text = " ".join(texts).strip()
                    self.voice_queue.put(full_text if full_text else None)
                    
            except Exception as e:
                print(f"Thread error: {e}")
                self.voice_queue.put(None)

        listener = threading.Thread(target=listen_thread, daemon=True)
        listener.start()

        input("Press Enter to stop recording...")
        self.stop_listening_flag.set()
        listener.join(timeout=2)  # Don't wait forever

        try:
            text = self.voice_queue.get(timeout=3)
        except:
            text = None
            
        if not text:
            print("⚠ No speech detected or recognition failed.")
            return None

        print(f"📝 You said: {text}")
        print("=" * 60)
        return text

    def speak_text(self, text: str, display_text: bool = True):
        """Convert text to speech and speak it"""
        if not text:
            return
        try:
            if display_text:
                print(f"\n🔊 Speaking: {text}")
                print("=" * 60)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            if display_text:
                print("✅ Finished speaking")
                print("=" * 60)
        except Exception as e:
            print(f"⚠ Error during speech synthesis: {e}")

    def format_voice_output(self, explainability_output: Dict[str, Any]) -> str:
        """Format the explainability output for voice"""
        try:
            top_diag = explainability_output.get("top_diagnosis", {})
            condition = top_diag.get("condition", "Unknown")
            confidence = top_diag.get("confidence", "0%")
            
            medications = top_diag.get("medications", [])
            precautions = top_diag.get("precautions", [])
            exercises = top_diag.get("exercises", [])
            diet = top_diag.get("diet", [])

            voice_text = f"Based on your symptoms, the most likely diagnosis is {condition} with {confidence} confidence. "

            if medications and len(medications) > 0:
                meds_text = ", ".join(medications[:3])
                voice_text += f"Recommended medications include: {meds_text}. "
                
            if precautions and len(precautions) > 0:
                prec_text = ", ".join(precautions[:3])
                voice_text += f"Important precautions: {prec_text}. "
                
            if exercises and len(exercises) > 0:
                ex_text = ", ".join(exercises[:3])
                voice_text += f"Recommended exercises: {ex_text}. "
                
            if diet and len(diet) > 0:
                diet_text = ", ".join(diet[:3])
                voice_text += f"Dietary recommendations: {diet_text}. "

            voice_text += "Please consult with a healthcare professional for proper medical advice. Thank you."
            return voice_text
        except Exception as e:
            logger.error(f"Error formatting voice output: {e}")
            return "I encountered an error while formatting the diagnosis results. Please consult with a healthcare professional."

    def display_detailed_results(self, explainability_output: Dict[str, Any]):
        """Display the explainability agent's report"""
        try:
            print("\n" + "=" * 80)
            print("📋 DETAILED DIAGNOSIS RESULTS")
            print("=" * 80)
            
            # Display the explainability report
            report = explainability_output.get("report", "No report available")
            print(report)
            
            print("\n" + "=" * 80)
        except Exception as e:
            print(f"\n⚠ Error displaying results: {e}")

    async def process_natural_language_input(self, natural_language_input: str) -> Dict[str, Any]:
        """Main processing function that orchestrates all agents"""
        try:
            logger.info(f"Processing natural language input: {natural_language_input[:100]}...")

            # Step 1: Extract symptoms from natural language
            logger.info("Step 1: Extracting symptoms from natural language input")
            symptom_result = self.symptom_parser.extract_symptoms_from_text(natural_language_input)
            
            if symptom_result["status"] != "success":
                logger.error(f"Symptom extraction failed: {symptom_result.get('error_message', 'Unknown error')}")
                return {
                    "status": "error",
                    "error_message": "Failed to extract symptoms from input"
                }

            safety_warnings = self._get_safety_warnings(
                natural_language_input, symptom_result["symptoms"]
            )

            # Step 2: Get diagnosis from diagnosis agent  
            logger.info("Step 2: Getting diagnosis from diagnosis agent")
            diagnosis_input = {
                'symptoms': symptom_result["symptoms"],
                'demographics': {},
                'allergies': ['no'],
                'past_diseases': ['no'],
                'medications': ['no']
            }
            
            diagnosis_result = await self.diagnosis_agent.diagnose(diagnosis_input)
            
            # Convert diagnosis result to format expected by other agents
            if isinstance(diagnosis_result, dict):
                top_diagnosis = diagnosis_result.get('top_diagnosis', {})
                all_diagnoses = diagnosis_result.get('all_diagnoses', [])
                
                # Ensure confidence values are properly formatted
                if top_diagnosis:
                    top_diagnosis['confidence'] = self._parse_confidence(top_diagnosis.get('confidence', 0))
                
                diagnoses_list = []
                if top_diagnosis and top_diagnosis.get('condition'):
                    diagnoses_list.append({
                        'condition': top_diagnosis.get('condition'),
                        'confidence': top_diagnosis['confidence'],
                        'description': top_diagnosis.get('description', '')
                    })
                
                for diag in all_diagnoses:
                    if diag.get('condition') and diag.get('condition') != top_diagnosis.get('condition'):
                        diagnoses_list.append({
                            'condition': diag.get('condition'),
                            'confidence': self._parse_confidence(diag.get('confidence', 0)),
                            'description': diag.get('description', '')
                        })
            else:
                diagnoses_list = diagnosis_result if isinstance(diagnosis_result, list) else []
                top_diagnosis = diagnoses_list[0] if diagnoses_list else {}
                
                # Ensure confidence values are properly formatted for list format
                for diag in diagnoses_list:
                    diag['confidence'] = self._parse_confidence(diag.get('confidence', 0))

            # Step 3: Get literature validation
            logger.info("Step 3: Getting literature validation")
            literature_input = {
                'initial_diagnoses': diagnoses_list,
                'extracted_symptoms': [{'name': s.get('symptom', '')} for s in symptom_result["symptoms"]]
            }
            try:
                await self.literature_agent._load_models()
                literature_result = await self.literature_agent.process(literature_input)
            except Exception as e:
                logger.warning(f"Literature validation unavailable: {e}")
                literature_result = {'literature_evidence': []}

            # Step 4: Get case study validation
            logger.info("Step 4: Getting case study validation")
            case_study_input = {
                'initial_diagnoses': diagnoses_list,
                'extracted_symptoms': [{'name': s.get('symptom', '')} for s in symptom_result["symptoms"]]
            }
            
            condition_names = [diag['condition'] for diag in diagnoses_list]
            try:
                await self.case_study_agent._load_models()
                if condition_names:
                    await self.case_study_agent._load_data(condition_names)
                case_study_result = await self.case_study_agent.process(case_study_input)
            except Exception as e:
                logger.warning(f"Case study validation unavailable: {e}")
                case_study_result = {'case_studies': []}

            # Step 5: Generate explainability output
            logger.info("Step 5: Generating explainability output")
            
            # Prepare data for explainability agent
            literature_evidence = literature_result.get('literature_evidence', [])
            case_studies = case_study_result.get('case_studies', [])
            
            # Get literature and case study summaries
            literature_summary = self._create_summary(literature_evidence, "literature")
            case_study_summary = self._create_summary(case_studies, "case studies")
            
            # Prepare top diagnosis with safe confidence formatting
            safe_top_diagnosis = {}
            if top_diagnosis:
                safe_top_diagnosis = {
                    'condition': top_diagnosis.get('condition', 'Unknown'),
                    'confidence': top_diagnosis.get('confidence', 0.0),
                    'medications': top_diagnosis.get('medications', []),
                    'precautions': top_diagnosis.get('precautions', []),
                    'exercises': top_diagnosis.get('exercises', []),
                    'diet': top_diagnosis.get('diet', []),
                    'description': top_diagnosis.get('description', '')
                }
            
            # Prepare safe diagnoses list
            safe_diagnoses_list = []
            for diag in diagnoses_list[:5]:
                safe_diagnoses_list.append({
                    'condition': diag.get('condition', 'Unknown'),
                    'confidence': diag.get('confidence', 0.0),
                    'description': diag.get('description', '')
                })
            
            # Generate explainability report using safe data
            try:
                explainability_report = self.explainability_agent.generate_explainability_report(
                    top_diagnosis=safe_top_diagnosis,
                    all_diagnoses=safe_diagnoses_list,
                    literature_validation=literature_summary,
                    case_study_validation=case_study_summary
                )
            except Exception as e:
                logger.error(f"Explainability report generation failed: {e}")
                explainability_report = f"Explainability Report:\n\nTop Diagnosis: {safe_top_diagnosis.get('condition', 'Unknown')}\nConfidence: {safe_top_diagnosis.get('confidence', 0.0):.2f}\n\nRecommendations available but report generation encountered an error.\n\nLiterature validation: {literature_summary}\n\nCase study validation: {case_study_summary}"
            if safety_warnings:
                explainability_report += "\n\n=== Urgent Safety Warnings ===\n" + "\n".join(
                    f"- {warning}" for warning in safety_warnings
                )
            
            explainability_output = {
                "status": "success",
                "report": explainability_report,
                "top_diagnosis": safe_top_diagnosis,
                "top_5_diagnoses": safe_diagnoses_list,
                "literature_validation": literature_summary,
                "case_study_validation": case_study_summary,
                "safety_warnings": safety_warnings,
                "timestamp": datetime.now().isoformat()
            }

            # Cleanup
            await self.literature_agent.cleanup()
            await self.case_study_agent.cleanup()

            logger.info("Processing completed successfully")
            return explainability_output

        except Exception as e:
            logger.error(f"Error in orchestrator processing: {str(e)}")
            for service in (self.literature_agent, self.case_study_agent):
                try:
                    await service.cleanup()
                except Exception:
                    logger.exception("Failed to clean up an agent resource")
            return {
                "status": "error",
                "error_message": f"Processing failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _get_safety_warnings(self, text: str, symptoms: list) -> list:
        """Apply auditable warning rules before diagnosis ranking."""
        normalized = text.lower()
        present = {
            str(item.get("symptom", "")).lower()
            for item in symptoms
            if isinstance(item, dict)
            and item.get("assertion") != "negated"
            and not item.get("negated")
        }
        warnings = []
        if any(term in normalized or term in present for term in (
            "difficulty breathing", "shortness of breath", "trouble breathing"
        )):
            warnings.append("Difficulty breathing can be an emergency; seek urgent medical evaluation.")
        if any(term in normalized or term in present for term in ("chest pain", "pressure in chest")):
            warnings.append("Chest pain can be an emergency; seek urgent medical evaluation.")
        if (
            any(term in normalized or term in present for term in ("severe headache", "sudden headache"))
            and any(term in normalized or term in present for term in ("fever", "neck stiffness"))
        ):
            warnings.append("Severe or sudden headache with fever or neck stiffness requires urgent evaluation.")
        if any(term in normalized for term in ("confusion", "loss of consciousness", "face drooping", "slurred speech")):
            warnings.append("Altered consciousness or stroke-like symptoms require emergency care.")
        return warnings

    def _parse_confidence(self, confidence):
        """Parse confidence value to float"""
        if isinstance(confidence, str):
            try:
                # Handle percentage strings
                if '%' in confidence:
                    return float(confidence.replace('%', '')) / 100.0
                else:
                    return float(confidence)
            except:
                return 0.0
        elif isinstance(confidence, (int, float)):
            return float(confidence)
        else:
            return 0.0

    def _create_summary(self, evidence_list: list, evidence_type: str) -> str:
        """Create summary from evidence list"""
        if not evidence_list:
            return f"No {evidence_type} evidence available."
        
        summary_parts = [f"{evidence_type.title()} Evidence Summary:"]
        
        for i, evidence in enumerate(evidence_list[:3], 1):
            if evidence_type == "literature":
                title = evidence.get('title', 'Unknown study')
                source = evidence.get('source', 'Unknown')
                url = evidence.get('url', '')
                summary_parts.append(f"{i}. {title} (Source: {source})")
                if url:
                    summary_parts.append(f"   URL: {url}")
            else:  # case studies
                title = evidence.get('case_title', 'Unknown case')
                source = evidence.get('source', 'Unknown')
                url = evidence.get('case_url', '')
                summary_parts.append(f"{i}. {title} (Source: {source})")
                if url:
                    summary_parts.append(f"   URL: {url}")
        
        if len(evidence_list) > 3:
            summary_parts.append(f"... and {len(evidence_list) - 3} more {evidence_type} sources")
            
        return "\n".join(summary_parts)

    async def process_voice_input_manual_stop(self) -> Dict[str, Any]:
        """Process voice input through the complete diagnosis pipeline"""
        voice_input = self.listen_for_voice_input()
        if not voice_input:
            return {
                "status": "error",
                "error_message": "No voice input detected or recognition failed"
            }

        print("\n🔄 Processing your symptoms through AI diagnosis system...")
        result = await self.process_natural_language_input(voice_input)
        
        if result.get("status") == "success":
            self.display_detailed_results(result)
            voice_output = self.format_voice_output(result)
            self.speak_text(voice_output, display_text=True)
        else:
            print(f"\n⚠ Error: {result.get('error_message', 'Unknown error')}")
            
        return result

    async def cleanup(self):
        """Cleanup all agent resources"""
        try:
            await self.literature_agent.cleanup()
            await self.case_study_agent.cleanup()
            logger.info("All agents cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

async def continuous_voice_bot_mode(orchestrator: OrchestratorAgent):
    """Continuous voice bot mode"""
    print("=" * 80)
    print("🎤 DIAGNOSURE VOICE - CONTINUOUS VOICE BOT MODE")
    print("=" * 80)
    print("I'm ready to listen for your symptoms continuously.")
    print("Say 'quit', 'exit' or press Ctrl+C to stop.")

    try:
        while True:
            print(f"\n{'='*60}")
            print("🎤 Listening for your symptoms...")
            result = await orchestrator.process_voice_input_manual_stop()
            
            if result["status"] == "error":
                if "No voice input detected" in result.get("error_message", ""):
                    print("⏰ No speech detected. I'll keep listening...")
                    continue
                else:
                    print(f"⚠ Error: {result.get('error_message')}")
                    continue
                    
            voice_input = result.get('input_text', '').lower()
            if any(word in voice_input for word in ['quit', 'exit', 'stop', 'bye', 'goodbye']):
                print("\n👋 Goodbye! Thanks for using Diagnosure Voice.")
                break
                
            print("\n🔄 Ready for next symptoms...")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Diagnosure Voice.")
    except Exception as e:
        print(f"\n⚠ Error in continuous voice bot mode: {str(e)}")
    finally:
        await orchestrator.cleanup()

async def main():
    """Main function with voice bot interface"""
    orchestrator = OrchestratorAgent()
    
    print("=" * 80)
    print("🎤 DIAGNOSURE VOICE - AI MEDICAL DIAGNOSIS BOT")
    print("=" * 80)
    print("Welcome! I'm your AI medical diagnosis assistant.")
    print("I can help you get a preliminary diagnosis based on your symptoms.")
    print("\nChoose your input method:")
    print("1. Voice Input (Speak your symptoms, press Enter to stop)")
    print("2. Text Input (Type your symptoms)")
    print("3. Test Mode (Predefined symptoms)")
    print("4. Continuous Voice Bot (Keep listening for symptoms)")
    
    try:
        choice = input("\nEnter your choice (1, 2, 3, or 4): ").strip()
        
        if choice == "1":
            print("\n🎤 VOICE INPUT MODE")
            result = await orchestrator.process_voice_input_manual_stop()
            
        elif choice == "2":
            print("\n📝 TEXT INPUT MODE")
            symptoms_text = input("Please describe your symptoms: ").strip()
            if not symptoms_text:
                print("⚠ No symptoms provided. Exiting.")
                return
            print(f"\n🔄 Processing: {symptoms_text}")
            result = await orchestrator.process_natural_language_input(symptoms_text)
            
            if result.get("status") == "success":
                orchestrator.display_detailed_results(result)
                # No voice output for text input
            else:
                print(f"\n⚠ Error: {result.get('error_message', 'Unknown error')}")
                
        elif choice == "3":
            print("\n🧪 TEST MODE")
            test_input = "I have been experiencing severe headache, high fever, and occasional dizziness for the past 3 days. I also feel very tired and have muscle pain."
            print(f"Using test input: {test_input}")
            print("🔄 Processing...")
            result = await orchestrator.process_natural_language_input(test_input)
            
            if result.get("status") == "success":
                orchestrator.display_detailed_results(result)
                # No voice output for test mode
            else:
                print(f"\n⚠ Error: {result.get('error_message', 'Unknown error')}")
                
        elif choice == "4":
            await continuous_voice_bot_mode(orchestrator)
            return
            
        else:
            print("⚠ Invalid choice. Exiting.")
            return
        
        # Final status
        if result.get("status") == "success":
            print(f"\n✅ Diagnosis completed successfully!")
            print("📋 Results have been displayed and spoken.")
        else:
            print(f"\n⚠ Diagnosis failed: {result.get('error_message', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Diagnosure Voice.")
    except Exception as e:
        print(f"\n⚠ Error during processing: {str(e)}")
    finally:
        await orchestrator.cleanup()
    
    print("\n" + "=" * 80)
    print("🎤 DIAGNOSURE VOICE SESSION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())