from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import socketio
from datetime import datetime
from transformers import pipeline
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask and Socket.IO
app = Flask(__name__)
CORS(app)
sio = socketio.Server(cors_allowed_origins='*', async_mode='threading')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Initialize AI models
logger.info("Loading AI models...")
try:
    # Medical text classification
    classifier = pipeline(
        "text-classification",
        model="emilyalsentzer/Bio_ClinicalBERT",
        tokenizer="emilyalsentzer/Bio_ClinicalBERT",
        device=0 if torch.cuda.is_available() else -1
    )
    
    # Medical NER (Named Entity Recognition)
    ner = pipeline(
        "ner",
        model="d4data/biomedical-ner-all",
        tokenizer="d4data/biomedical-ner-all",
        aggregation_strategy="simple",
        device=0 if torch.cuda.is_available() else -1
    )
    
    logger.info("AI models loaded successfully")
except Exception as e:
    logger.error(f"Error loading AI models: {e}")
    classifier = None
    ner = None

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
        'messages_count': len(messages),
        'ml_models_loaded': all(model is not None for model in [classifier, ner])
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
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

        # Organize into SOAP format
        soap_analysis = analyze_soap(text, results.get('entities', {}))
        results['soap'] = soap_analysis

        return jsonify({
            'status': 'success',
            'analysis': results
        })

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        return jsonify({'error': str(e)}), 500

def analyze_soap(text, entities):
    """Analyze text and organize into SOAP format using extracted entities"""
    soap = {
        'subjective': '',
        'objective': '',
        'assessment': '',
        'plan': ''
    }
    
    # Enhanced medical terminology keywords
    subjective_keywords = [
        'feel', 'pain', 'symptom', 'complaint', 'report', 'patient states', 
        'patient reports', 'experiencing', 'suffering from', 'noticed', 
        'concerned about', 'worried about', 'feeling'
    ]
    
    objective_keywords = [
        'observe', 'measure', 'test', 'exam', 'vital', 'blood pressure', 
        'temperature', 'heart rate', 'pulse', 'respiratory rate', 'oxygen', 
        'saturation', 'weight', 'height', 'bmi', 'lab results', 'imaging', 
        'x-ray', 'mri', 'ct scan', 'ultrasound', 'physical examination'
    ]
    
    assessment_keywords = [
        'diagnose', 'condition', 'finding', 'result', 'assessment', 
        'impression', 'conclusion', 'differential diagnosis', 'ruled out', 
        'confirmed', 'consistent with', 'indicative of', 'suggestive of'
    ]
    
    plan_keywords = [
        'treat', 'prescribe', 'follow-up', 'recommend', 'plan', 'medication', 
        'therapy', 'dose', 'schedule', 'frequency', 'duration', 'refer', 
        'referral', 'consult', 'consultation', 'monitor', 'monitoring', 
        'lifestyle', 'diet', 'exercise', 'activity', 'rest', 'avoid', 
        'precautions', 'instructions', 'education', 'counseling', 'return', 
        'revisit', 'appointment', 'surgery', 'procedure', 'test', 'imaging',
        'blood work', 'lab work', 'vaccination', 'immunization'
    ]

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
        if 'PROCEDURE' in entities:
            soap['plan'] += 'Procedures: ' + ', '.join(entities['PROCEDURE']) + '. '
        if 'TEST' in entities:
            soap['plan'] += 'Tests: ' + ', '.join(entities['TEST']) + '. '

    # Process text by sentences with improved context
    sentences = text.split('.')
    for sentence in sentences:
        sentence = sentence.lower().strip()
        if not sentence:
            continue

        # Check for plan-related content first
        if any(keyword in sentence for keyword in plan_keywords):
            # Additional context for plan classification
            if any(word in sentence for word in ['prescribe', 'medication', 'drug', 'pill', 'tablet', 'capsule']):
                soap['plan'] += 'Medication Plan: ' + sentence + '. '
            elif any(word in sentence for word in ['follow-up', 'return', 'revisit', 'appointment']):
                soap['plan'] += 'Follow-up Plan: ' + sentence + '. '
            elif any(word in sentence for word in ['test', 'lab', 'imaging', 'scan', 'x-ray']):
                soap['plan'] += 'Testing Plan: ' + sentence + '. '
            elif any(word in sentence for word in ['lifestyle', 'diet', 'exercise', 'activity']):
                soap['plan'] += 'Lifestyle Plan: ' + sentence + '. '
            else:
                soap['plan'] += sentence + '. '
        elif any(keyword in sentence for keyword in subjective_keywords):
            soap['subjective'] += sentence + '. '
        elif any(keyword in sentence for keyword in objective_keywords):
            soap['objective'] += sentence + '. '
        elif any(keyword in sentence for keyword in assessment_keywords):
            soap['assessment'] += sentence + '. '

    # Clean up and format the output
    for key in soap:
        soap[key] = soap[key].strip()
        if not soap[key]:
            soap[key] = 'No ' + key + ' information found'

    return soap

# Socket.IO event handlers
@sio.event
def connect(sid, environ):
    logger.info(f'Client connected: {sid}')
    sio.emit('connection_status', {'status': 'connected'}, room=sid)

@sio.event
def disconnect(sid):
    logger.info(f'Client disconnected: {sid}')

@sio.on('message')
def handle_message(sid, data):
    logger.info(f'Received message from {sid}: {data}')
    sio.emit('message', data, broadcast=True)

if __name__ == '__main__':
    logger.info("Server starting at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True) 