# LingoSpectrum: A Multilingual Question-Answering AI System

A full-stack application that provides real-time translation and AI-powered responses in multiple languages.

## Features

- Real-time translation between multiple languages
- AI-powered responses to questions in different languages
- Support for English (US), Arabic, Chinese, and Spanish
- Single language or multi-language mode
- Automatic language detection
- Clean and responsive user interface

## Tech Stack

### Frontend
- Next.js 14
- React
- TailwindCSS
- TypeScript

### Backend
- FastAPI
- Python 3.8+
- OpenAI API
- DeepL API

## Prerequisites

Before you begin, ensure you have:
- Node.js 18+ installed
- Python 3.8+ installed
- OpenAI API key
- DeepL API key

## Installation

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
DEEPL_API_KEY=your_deepl_api_key_here
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```
