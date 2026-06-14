# AI Role-Based Candidate Screening System

An intelligent, AI-powered recruitment platform that automates candidate screening using role-based criteria. The system combines React for an intuitive frontend interface with FastAPI for high-performance backend processing, RAG (Retrieval-Augmented Generation) for intelligent candidate evaluation, and SQLite for lightweight data persistence.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Role-Based Screening**: Automatically filter candidates based on job-specific requirements
- **RAG-Powered Analysis**: Intelligent candidate evaluation using Retrieval-Augmented Generation
- **User-Friendly Interface**: Modern React-based dashboard for easy candidate management
- **Fast Processing**: High-performance FastAPI backend for quick screening results
- **Lightweight Database**: SQLite for easy deployment and data persistence
- **Scalable Design**: Modular architecture ready for enterprise integration

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | React | Latest |
| Backend | FastAPI | Latest |
| Database | SQLite | 3.x |
| ML/AI | RAG (LangChain/Llama Index) | Latest |
| Package Manager | npm (Frontend), pip (Backend) | - |

**Language Composition:**
- Python: 80.5%
- JavaScript: 15%
- CSS: 4.2%
- HTML: 0.3%

## Project Structure

```
ai-role-based-candidate-screening-system/
├── frontend/                    # React application
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API integration
│   │   └── App.js
│   ├── public/
│   └── package.json
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── models/             # Data models
│   │   ├── routes/             # API endpoints
│   │   ├── services/           # Business logic
│   │   └── database.py         # Database configuration
│   ├── requirements.txt
│   └── config.py
├── data/                        # SQLite database and data files
└── README.md
```

## Prerequisites

Before you begin, ensure you have installed:

- **Python** 3.9 or higher ([Download](https://www.python.org/downloads/))
- **Node.js** 16.x or higher and npm ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **pip** (comes with Python)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lavishka22/ai-role-based-candidate-screening-system.git
cd ai-role-based-candidate-screening-system
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

## Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=sqlite:///./data/candidates.db

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# RAG Configuration
OPENAI_API_KEY=your_openai_api_key_here
# Or if using other LLM providers
HUGGINGFACE_API_KEY=your_huggingface_key_here

# Application Settings
DEBUG=False
CORS_ORIGINS=http://localhost:3000
```

### Frontend Configuration

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
```

## Running the Application

### Start the Backend Server

```bash
# From the backend directory (with venv activated)
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Start the Frontend Development Server

```bash
# From the frontend directory (in a new terminal)
cd frontend
npm start
```

The application will open at `http://localhost:3000`

## Usage

### Basic Workflow

1. **Access the Application**: Open `http://localhost:3000` in your browser
2. **Create a Job Role**: Define the job title, requirements, and desired qualifications
3. **Upload Candidates**: Submit candidate resumes or profiles
4. **Run Screening**: Initiate the AI-powered screening process
5. **Review Results**: View ranked candidates with screening scores and recommendations

### Example API Call

```bash
# Screen a candidate
curl -X POST http://localhost:8000/api/v1/screen \
  -H "Content-Type: application/json" \
  -d {
    "candidate_id": "123",
    "role_id": "senior_developer",
    "resume_text": "..."
  }
```

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide interactive documentation for all available endpoints.

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                   React Frontend                         │
│              (UI, State Management)                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │         API Routes & Controllers                 │   │
│  └──────────────┬───────────────────────────────────┘   │
│                 │                                         │
│  ┌──────────────▼───────────────────────────────────┐   │
│  │    RAG Engine (LLM + Vector Search)             │   │
│  │   - Candidate Profile Analysis                  │   │
│  │   - Requirements Matching                       │   │
│  │   - Scoring & Ranking                           │   │
│  └──────────────┬───────────────────────────────────┘   │
│                 │                                         │
│  ┌──────────────▼───────────────────────────────────┐   │
│  │      SQLite Database                             │   │
│  │   - Candidates                                   │   │
│  │   - Job Roles                                    │   │
│  │   - Screening Results                           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** and test thoroughly
4. **Commit with clear messages**: `git commit -m 'Add some feature'`
5. **Push to your fork**: `git push origin feature/your-feature-name`
6. **Open a Pull Request** with a detailed description

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation as needed

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change the port in the run command
python -m uvicorn app.main:app --port 8001
```

**Database errors:**
```bash
# Reset the database
rm data/candidates.db
# Restart the application to recreate tables
```

**CORS errors:**
Update the `CORS_ORIGINS` in your `.env` file to match your frontend URL.

### Frontend Issues

**Node modules not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
Check that the backend is running and `REACT_APP_API_URL` in `.env` is correct.

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Contact & Support

For questions, issues, or suggestions:
- Open an [issue](https://github.com/lavishka22/ai-role-based-candidate-screening-system/issues)
- Check existing discussions

---

**Happy Screening! 🚀**
