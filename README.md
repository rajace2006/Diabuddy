# Medical SOAP Note Analysis System

A full-stack application that uses machine learning to analyze medical text and generate structured SOAP (Subjective, Objective, Assessment, Plan) notes.

## Features

- Real-time medical text analysis
- SOAP note generation
- Medical entity recognition
- Medical condition classification
- Speech-to-text transcription
- Modern React frontend
- Flask backend with ML integration

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

2. Backend Setup:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Frontend Setup:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

1. Start the Backend:
   ```bash
   cd backend
   python app.py
   ```
   The backend server will start at http://localhost:5000

2. Start the Frontend:
   ```bash
   cd frontend
   npm start
   ```
   The frontend will start at http://localhost:3000

## Usage

1. Open your browser and navigate to http://localhost:3000
2. You can:
   - Type medical text directly
   - Use the speech recording feature
   - View AI-generated SOAP notes
   - See medical entity recognition results
   - Get condition classifications

## Project Structure

```
├── backend/
│   ├── app.py              # Flask application with ML integration
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   └── App.css        # Styles
│   └── package.json       # Node.js dependencies
└── README.md
```

## Technologies Used

- Frontend:
  - React
  - Socket.IO
  - Modern CSS

- Backend:
  - Flask
  - Transformers (Hugging Face)
  - Bio_ClinicalBERT
  - Biomedical NER

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license] 