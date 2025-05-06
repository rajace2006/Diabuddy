"""
Configuration settings for the Diabuddy application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server settings
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '127.0.0.1')

# Speech recognition settings
SPEECH_RECOGNITION = {
    'energy_threshold': 300,
    'dynamic_energy_threshold': True,
    'pause_threshold': 0.8,
}

# SOAP note settings
SOAP_CATEGORIES = {
    'subjective': [
        'patient reports', 'complains of', 'states', 'describes', 'feels',
        'denies', 'admits', 'history', 'symptoms', 'pain scale'
    ],
    'objective': [
        'vital signs', 'examination reveals', 'observed', 'auscultation',
        'palpation', 'measured', 'test results', 'lab values', 'findings'
    ],
    'assessment': [
        'diagnosis', 'impression', 'likely', 'suspected', 'differential',
        'consistent with', 'suggests', 'indicates', 'assessment'
    ],
    'plan': [
        'recommend', 'prescribe', 'plan', 'treatment', 'follow up',
        'refer', 'order', 'schedule', 'instructions', 'education'
    ]
}

# Medical terms dictionary
MEDICAL_TERMS = {
    'vitals': [
        'BP', 'HR', 'RR', 'T', 'SpO2',
        'blood pressure', 'heart rate', 'respiratory rate',
        'temperature', 'oxygen saturation'
    ],
    'measurements': [
        'kg', 'cm', 'mm Hg', 'bpm', 'celsius', 'fahrenheit'
    ],
    'assessments': [
        'diagnosis', 'differential', 'impression',
        'assessment', 'suspected'
    ],
    'medications': [
        'mg', 'mcg', 'ml', 'tablet', 'capsule',
        'injection', 'oral', 'IV', 'IM'
    ],
    'timing': [
        'bid', 'tid', 'qid', 'prn', 'daily', 'weekly',
        'q4h', 'q6h', 'q8h', 'q12h'
    ]
} 