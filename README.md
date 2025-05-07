# Diabuddy

A healthcare application for diabetes management with real-time transcription and AI-powered medical note organization.

## Features

- Real-time speech-to-text transcription
- AI-powered medical text analysis
- SOAP note organization
- Health metrics tracking
- Real-time chat functionality

## Tech Stack

- Frontend: React.js
- Backend: Flask
- AI: Hugging Face Transformers
- Real-time Communication: Socket.IO

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python app.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Version History

### v1.0.0
- Initial release
- Basic transcription functionality
- SOAP note organization
- Health metrics tracking

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 