import speech_recognition as sr
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
import json
from datetime import datetime
import re

class SpeechProcessor:
    def __init__(self):
        # Initialize speech recognizer with custom settings
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Increased sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Shorter pause detection
        
        # Load SpaCy model for medical text processing
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize BERT-based text classification
        self.classifier = pipeline("zero-shot-classification")
        
        # Common medical terms and abbreviations
        self.medical_terms = {
            "vitals": ["BP", "HR", "RR", "T", "SpO2", "blood pressure", "heart rate", "respiratory rate", "temperature", "oxygen saturation"],
            "measurements": ["kg", "cm", "mm Hg", "bpm", "celsius", "fahrenheit"],
            "assessments": ["diagnosis", "differential", "impression", "assessment", "suspected"],
            "medications": ["mg", "mcg", "ml", "tablet", "capsule", "injection", "oral", "IV", "IM"],
            "timing": ["bid", "tid", "qid", "prn", "daily", "weekly", "q4h", "q6h", "q8h", "q12h"],
        }
        
        # SOAP section keywords
        self.soap_keywords = {
            "subjective": [
                "patient reports", "complains of", "states", "describes", "feels",
                "denies", "admits", "history", "symptoms", "pain scale"
            ],
            "objective": [
                "vital signs", "examination reveals", "observed", "auscultation",
                "palpation", "measured", "test results", "lab values", "findings"
            ],
            "assessment": [
                "diagnosis", "impression", "likely", "suspected", "differential",
                "consistent with", "suggests", "indicates", "assessment"
            ],
            "plan": [
                "recommend", "prescribe", "plan", "treatment", "follow up",
                "refer", "order", "schedule", "instructions", "education"
            ]
        }

    def preprocess_audio(self, audio_data):
        """Enhance audio quality for better recognition"""
        try:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(audio_data)
            return audio_data
        except Exception as e:
            print(f"Error preprocessing audio: {e}")
            return audio_data

    def transcribe_audio(self, audio_data):
        """Convert audio to text using Google Speech Recognition with medical context"""
        try:
            # Preprocess audio
            audio_data = self.preprocess_audio(audio_data)
            
            # Perform recognition
            text = self.recognizer.recognize_google(audio_data)
            
            # Post-process medical terms
            text = self.post_process_medical_terms(text)
            return text
        except sr.UnknownValueError:
            return "Speech recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from speech recognition service; {e}"

    def post_process_medical_terms(self, text):
        """Correct common medical terms and abbreviations"""
        # Convert text to lowercase for matching
        text_lower = text.lower()
        
        # Replace common misheard medical terms
        corrections = {
            "blood pressure": ["blood fresher", "blood presser"],
            "hypertension": ["high pertension", "high tension"],
            "diabetes": ["diabetics", "diabeties"],
            "medication": ["medications", "medicine"],
            "temperature": ["temp"],
            # Add more common corrections
        }
        
        for correct, variants in corrections.items():
            for variant in variants:
                text_lower = text_lower.replace(variant, correct)
        
        # Correct units and measurements
        measurement_patterns = {
            r'(\d+)\s*over\s*(\d+)': r'\1/\2',  # Blood pressure format
            r'(\d+)\s*bpm': r'\1 BPM',  # Heart rate
            r'(\d+)\s*degrees?': r'\1°',  # Temperature
        }
        
        for pattern, replacement in measurement_patterns.items():
            text_lower = re.sub(pattern, replacement, text_lower)
        
        return text_lower

    def classify_sentence(self, sentence):
        """Classify sentence into SOAP categories with improved accuracy"""
        # First check for strong keyword matches
        sentence_lower = sentence.lower()
        
        for category, keywords in self.soap_keywords.items():
            for keyword in keywords:
                if keyword in sentence_lower:
                    return category
        
        # If no strong keyword matches, use zero-shot classification
        candidate_labels = [
            "subjective patient complaints and history",
            "objective medical findings and measurements",
            "assessment and diagnosis",
            "treatment plan and recommendations"
        ]
        
        result = self.classifier(sentence, candidate_labels)
        scores = result['scores']
        labels = result['labels']
        
        # Get the highest scoring category
        max_score_index = scores.index(max(scores))
        category = labels[max_score_index].split()[0].lower()
        
        return category

    def organize_into_soap(self, text):
        """Organize transcribed text into SOAP format with enhanced structure"""
        # Split text into sentences
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        # Initialize SOAP sections with metadata
        soap = {
            "subjective": {
                "content": [],
                "key_findings": set()
            },
            "objective": {
                "content": [],
                "measurements": {},
                "vitals": {}
            },
            "assessment": {
                "content": [],
                "diagnoses": set()
            },
            "plan": {
                "content": [],
                "medications": [],
                "follow_up": None
            }
        }
        
        # Process each sentence
        for sentence in sentences:
            category = self.classify_sentence(sentence)
            
            # Extract and categorize information based on section
            if category == "subjective":
                soap["subjective"]["content"].append(sentence)
                # Extract key symptoms/complaints
                doc = self.nlp(sentence)
                for ent in doc.ents:
                    if ent.label_ in ["SYMPTOM", "CONDITION"]:
                        soap["subjective"]["key_findings"].add(ent.text)
                        
            elif category == "objective":
                soap["objective"]["content"].append(sentence)
                # Extract measurements and vitals
                self.extract_measurements(sentence, soap["objective"])
                
            elif category == "assessment":
                soap["assessment"]["content"].append(sentence)
                # Extract potential diagnoses
                doc = self.nlp(sentence)
                for ent in doc.ents:
                    if ent.label_ in ["CONDITION", "DISEASE"]:
                        soap["assessment"]["diagnoses"].add(ent.text)
                        
            elif category == "plan":
                soap["plan"]["content"].append(sentence)
                # Extract medications and follow-up
                self.extract_plan_details(sentence, soap["plan"])
        
        # Format the result
        formatted_soap = {
            "timestamp": datetime.now().isoformat(),
            "sections": {
                "Subjective": {
                    "text": " ".join(soap["subjective"]["content"]),
                    "key_findings": list(soap["subjective"]["key_findings"])
                },
                "Objective": {
                    "text": " ".join(soap["objective"]["content"]),
                    "vitals": soap["objective"]["vitals"],
                    "measurements": soap["objective"]["measurements"]
                },
                "Assessment": {
                    "text": " ".join(soap["assessment"]["content"]),
                    "diagnoses": list(soap["assessment"]["diagnoses"])
                },
                "Plan": {
                    "text": " ".join(soap["plan"]["content"]),
                    "medications": soap["plan"]["medications"],
                    "follow_up": soap["plan"]["follow_up"]
                }
            }
        }
        
        return formatted_soap

    def extract_measurements(self, text, objective_data):
        """Extract measurements and vital signs from text"""
        # Extract vital signs
        vitals_patterns = {
            'blood_pressure': r'BP[:\s]*(\d+/\d+)',
            'heart_rate': r'HR[:\s]*(\d+)',
            'temperature': r'T[:\s]*(\d+\.?\d*)',
            'respiratory_rate': r'RR[:\s]*(\d+)',
            'oxygen_saturation': r'SpO2[:\s]*(\d+%?)',
        }
        
        for vital, pattern in vitals_patterns.items():
            match = re.search(pattern, text)
            if match:
                objective_data["vitals"][vital] = match.group(1)
        
        # Extract other measurements
        measurement_patterns = {
            'weight': r'(\d+\.?\d*)\s*(kg|pounds|lbs)',
            'height': r'(\d+\.?\d*)\s*(cm|meters|m)',
            'bmi': r'BMI[:\s]*(\d+\.?\d*)',
        }
        
        for measure, pattern in measurement_patterns.items():
            match = re.search(pattern, text)
            if match:
                objective_data["measurements"][measure] = {
                    "value": match.group(1),
                    "unit": match.group(2) if len(match.groups()) > 1 else None
                }

    def extract_plan_details(self, text, plan_data):
        """Extract medication and follow-up details from plan section"""
        # Extract medications
        med_pattern = r'(\d+\s*(?:mg|mcg|ml|g|mg/ml|mcg/ml))\s*of\s*([A-Za-z]+)'
        meds = re.findall(med_pattern, text)
        for dose, med in meds:
            plan_data["medications"].append({
                "medication": med,
                "dosage": dose
            })
        
        # Extract follow-up timing
        follow_up_pattern = r'follow\s*(?:up|-up)\s*in\s*(\d+)\s*(days|weeks|months)'
        follow_up = re.search(follow_up_pattern, text.lower())
        if follow_up:
            plan_data["follow_up"] = {
                "duration": follow_up.group(1),
                "unit": follow_up.group(2)
            }

    def process_realtime(self, audio_chunk):
        """Process audio chunk in real-time with enhanced features"""
        text = self.transcribe_audio(audio_chunk)
        if text and text != "Speech recognition could not understand the audio":
            soap_notes = self.organize_into_soap(text)
            return soap_notes
        return None 