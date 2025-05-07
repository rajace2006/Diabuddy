from flask import Flask, request, jsonify, render_template
from datetime import datetime
from flask_cors import CORS
import socketio
import json
import os
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification
import torch

# Initialize Flask and Socket.IO
app = Flask(__name__)
CORS(app)
sio = socketio.Server(cors_allowed_origins='*', async_mode='threading')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Initialize AI models
try:
    # Medical text classification
    classifier = pipeline(
        "text-classification",
        model="emilyalsentzer/Bio_ClinicalBERT",
        tokenizer="emilyalsentzer/Bio_ClinicalBERT"
    )
    
    # Medical NER (Named Entity Recognition)
    ner = pipeline(
        "ner",
        model="d4data/biomedical-ner-all",
        tokenizer="d4data/biomedical-ner-all",
        aggregation_strategy="simple"
    )
    
    # Medical text understanding
    medical_understanding = pipeline(
        "text-classification",
        model="johngiorgi/declutr-sci-base",
        tokenizer="johngiorgi/declutr-sci-base"
    )
    
    print("AI models loaded successfully")
except Exception as e:
    print(f"Error loading AI models: {e}")
    classifier = None
    ner = None
    medical_understanding = None

# Store messages and transcriptions in memory
messages = []
transcriptions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.get_json()
        message = {
            'message': data['message'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        messages.append(message)
        return jsonify({'status': 'success'})
    return jsonify({'messages': messages})

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'online',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'messages_count': len(messages)
    })

@app.route('/api/transcribe', methods=['POST'])
def process_transcription():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Store transcription
        transcription = {
            'text': text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        transcriptions.append(transcription)

        # AI Processing
        results = {}
        
        if classifier:
            # Classify medical conditions
            classification = classifier(text)
            results['classification'] = classification

        if ner:
            # Extract medical entities
            entities = ner(text)
            # Group entities by type
            grouped_entities = {}
            for entity in entities:
                entity_type = entity['entity_group']
                if entity_type not in grouped_entities:
                    grouped_entities[entity_type] = []
                grouped_entities[entity_type].append(entity['word'])
            results['entities'] = grouped_entities

        if medical_understanding:
            # Get medical text understanding
            understanding = medical_understanding(text)
            results['understanding'] = understanding

        # Organize into SOAP format
        soap_analysis = analyze_soap(text, results.get('entities', {}))
        results['soap'] = soap_analysis

        return jsonify({
            'status': 'success',
            'analysis': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_soap(text, entities):
    """Analyze text and organize into SOAP format using AI and extracted entities"""
    soap = {
        'subjective': '',
        'objective': '',
        'assessment': '',
        'plan': ''
    }
    
    # Enhanced keyword-based classification with medical terminology
    subjective_keywords = ['feel', 'pain', 'symptom', 'complaint', 'report', 'patient states', 'patient reports']
    objective_keywords = ['observe', 'measure', 'test', 'exam', 'vital', 'blood pressure', 'temperature', 'heart rate']
    assessment_keywords = ['diagnose', 'condition', 'finding', 'result', 'assessment', 'impression']
    plan_keywords = ['treat', 'prescribe', 'follow-up', 'recommend', 'plan', 'medication', 'therapy']

    # Add medical entities to appropriate sections
    if entities:
        if 'SYMPTOM' in entities:
            soap['subjective'] += 'Symptoms: ' + ', '.join(entities['SYMPTOM']) + '. '
        if 'DIAGNOSIS' in entities:
            soap['assessment'] += 'Diagnoses: ' + ', '.join(entities['DIAGNOSIS']) + '. '
        if 'TREATMENT' in entities:
            soap['plan'] += 'Treatments: ' + ', '.join(entities['TREATMENT']) + '. '
        if 'MEDICATION' in entities:
            soap['plan'] += 'Medications: ' + ', '.join(entities['MEDICATION']) + '. '

    # Process text by sentences
    sentences = text.split('.')
    for sentence in sentences:
        sentence = sentence.lower().strip()
        if any(keyword in sentence for keyword in subjective_keywords):
            soap['subjective'] += sentence + '. '
        elif any(keyword in sentence for keyword in objective_keywords):
            soap['objective'] += sentence + '. '
        elif any(keyword in sentence for keyword in assessment_keywords):
            soap['assessment'] += sentence + '. '
        elif any(keyword in sentence for keyword in plan_keywords):
            soap['plan'] += sentence + '. '

    return soap

# Socket.IO event handlers
@sio.event
def connect(sid, environ):
    print(f'Client connected: {sid}')
    sio.emit('connection_status', {'status': 'connected'}, room=sid)

@sio.event
def disconnect(sid):
    print(f'Client disconnected: {sid}')

@sio.on('message')
def handle_message(sid, data):
    print(f'Received message from {sid}: {data}')
    sio.emit('message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Server starting at http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True) 