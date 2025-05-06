import { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [status, setStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [medicalNotes, setMedicalNotes] = useState({
    subjective: '',
    objective: '',
    assessment: '',
    plan: ''
  });
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [healthData, setHealthData] = useState({
    bloodSugar: [],
    medications: [],
    appointments: []
  });
  const socketRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    socketRef.current = io('http://localhost:5000');
    socketRef.current.on('connect', () => console.log('Connected to server'));
    socketRef.current.on('message', (data) => setMessages(prev => [...prev, data]));
    
    if ('webkitSpeechRecognition' in window) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      
      recognitionRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setTranscription(transcript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };
    }
    
    fetchStatus();
    fetchMessages();
    fetchHealthData();

    return () => {
      if (socketRef.current) socketRef.current.disconnect();
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, []);

  const startRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleTranscriptionSubmit = async () => {
    if (!transcription.trim()) return;
    
    setIsProcessing(true);
    try {
      const response = await fetch('http://localhost:5000/api/transcribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: transcription }),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setAiAnalysis(data.analysis);
        
        // Update SOAP notes with AI analysis
        if (data.analysis.soap) {
          setMedicalNotes(prev => ({
            ...prev,
            ...data.analysis.soap
          }));
        }
      }
    } catch (error) {
      console.error('Error processing transcription:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const updateMedicalNote = (section, value) => {
    setMedicalNotes(prev => ({
      ...prev,
      [section]: value
    }));
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Error fetching status:', error);
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/messages');
      const data = await response.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const fetchHealthData = async () => {
    // Simulated health data - in a real app, this would come from your backend
    setHealthData({
      bloodSugar: [
        { value: 120, timestamp: '2025-05-04 08:00' },
        { value: 115, timestamp: '2025-05-04 12:00' },
        { value: 125, timestamp: '2025-05-04 18:00' }
      ],
      medications: [
        { name: 'Metformin', dosage: '500mg', frequency: 'Twice daily' },
        { name: 'Insulin', dosage: '10 units', frequency: 'Before meals' }
      ],
      appointments: [
        { date: '2025-05-15', time: '10:00 AM', doctor: 'Dr. Smith', type: 'Check-up' },
        { date: '2025-06-01', time: '2:30 PM', doctor: 'Dr. Johnson', type: 'Follow-up' }
      ]
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await fetch('http://localhost:5000/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newMessage }),
      });
      
      socketRef.current.emit('message', {
        message: newMessage,
        timestamp: new Date().toISOString()
      });
      
      setNewMessage('');
      fetchMessages();
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const renderHealthMetrics = () => (
    <div className="health-metrics">
      <div className="metric-card">
        <h3>Blood Sugar</h3>
        <div className="metric-chart">
          {healthData.bloodSugar.map((reading, index) => (
            <div key={index} className="reading">
              <span className="value">{reading.value}</span>
              <span className="time">{reading.timestamp}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="metric-card">
        <h3>Medications</h3>
        <ul className="medication-list">
          {healthData.medications.map((med, index) => (
            <li key={index}>
              <strong>{med.name}</strong>
              <span>{med.dosage}</span>
              <span>{med.frequency}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="metric-card">
        <h3>Upcoming Appointments</h3>
        <ul className="appointment-list">
          {healthData.appointments.map((apt, index) => (
            <li key={index}>
              <div className="appointment-date">{apt.date} at {apt.time}</div>
              <div className="appointment-details">
                <span>{apt.doctor}</span>
                <span>{apt.type}</span>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );

  const renderTranscriptionTool = () => (
    <div className="transcription-tool">
      <div className="transcription-controls">
        <button 
          className={`record-button ${isRecording ? 'recording' : ''}`}
          onClick={isRecording ? stopRecording : startRecording}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button>
        <div className="transcription-status">
          {isRecording ? 'Recording...' : 'Ready to record'}
        </div>
      </div>

      <div className="transcription-content">
        <textarea
          value={transcription}
          onChange={(e) => setTranscription(e.target.value)}
          placeholder="Transcription will appear here..."
          className="transcription-text"
        />
        <button 
          onClick={handleTranscriptionSubmit}
          className="submit-button"
          disabled={isProcessing}
        >
          {isProcessing ? 'Processing...' : 'Process with AI'}
        </button>
      </div>

      {aiAnalysis && (
        <div className="ai-analysis">
          <h3>AI Analysis</h3>
          {aiAnalysis.classification && (
            <div className="analysis-section">
              <h4>Medical Classification</h4>
              <pre>{JSON.stringify(aiAnalysis.classification, null, 2)}</pre>
            </div>
          )}
          {aiAnalysis.entities && (
            <div className="analysis-section">
              <h4>Medical Entities</h4>
              {Object.entries(aiAnalysis.entities).map(([type, entities]) => (
                <div key={type} className="entity-group">
                  <h5>{type}</h5>
                  <ul>
                    {entities.map((entity, index) => (
                      <li key={index}>{entity}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
          {aiAnalysis.understanding && (
            <div className="analysis-section">
              <h4>Medical Text Understanding</h4>
              <pre>{JSON.stringify(aiAnalysis.understanding, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      <div className="medical-notes">
        <h3>Medical Notes (SOAP Format)</h3>
        <div className="soap-sections">
          <div className="soap-section">
            <h4>Subjective</h4>
            <textarea
              value={medicalNotes.subjective}
              onChange={(e) => updateMedicalNote('subjective', e.target.value)}
              placeholder="Patient's reported symptoms and concerns..."
            />
          </div>
          <div className="soap-section">
            <h4>Objective</h4>
            <textarea
              value={medicalNotes.objective}
              onChange={(e) => updateMedicalNote('objective', e.target.value)}
              placeholder="Observable findings and measurements..."
            />
          </div>
          <div className="soap-section">
            <h4>Assessment</h4>
            <textarea
              value={medicalNotes.assessment}
              onChange={(e) => updateMedicalNote('assessment', e.target.value)}
              placeholder="Diagnosis and clinical impressions..."
            />
          </div>
          <div className="soap-section">
            <h4>Plan</h4>
            <textarea
              value={medicalNotes.plan}
              onChange={(e) => updateMedicalNote('plan', e.target.value)}
              placeholder="Treatment plan and follow-up..."
            />
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="App">
      <nav className="main-nav">
        <div className="logo">Diabuddy</div>
        <div className="nav-tabs">
          <button 
            className={activeTab === 'chat' ? 'active' : ''} 
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
          <button 
            className={activeTab === 'health' ? 'active' : ''} 
            onClick={() => setActiveTab('health')}
          >
            Health Metrics
          </button>
          <button 
            className={activeTab === 'transcribe' ? 'active' : ''} 
            onClick={() => setActiveTab('transcribe')}
          >
            Transcribe
          </button>
        </div>
      </nav>

      <main className="main-content">
        {activeTab === 'chat' ? (
          <div className="chat-section">
            <div className="status-bar">
              {status && (
                <div className="status-info">
                  <span>Status: {status.status}</span>
                  <span>Messages: {status.messages_count}</span>
                </div>
              )}
            </div>
            
            <div className="messages-container">
              {messages.map((msg, index) => (
                <div key={index} className="message">
                  <div className="message-content">{msg.message}</div>
                  <div className="message-timestamp">{msg.timestamp}</div>
                </div>
              ))}
            </div>

            <form onSubmit={handleSubmit} className="message-form">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
              />
              <button type="submit">Send</button>
            </form>
          </div>
        ) : activeTab === 'health' ? (
          renderHealthMetrics()
        ) : (
          renderTranscriptionTool()
        )}
      </main>
    </div>
  );
}

export default App;
