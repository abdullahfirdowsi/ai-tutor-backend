# AI Tutor Pro - Backend

This repository contains the backend API for the AI Tutor Pro application, which provides an interactive question-answering system powered by AI models.

## Project Overview

The AI Tutor Pro backend is built with FastAPI and provides REST APIs for:

- QA sessions management
- Question answering using AI models
- User authentication via Firebase
- Session history tracking

The backend is designed to support the AI Tutor Pro frontend application, providing all necessary APIs to manage conversations and educational content.

## Setup Instructions

### Prerequisites

- Python 3.9+ 
- [Firebase](https://firebase.google.com/) project with Authentication enabled
- [Optional] OpenAI API key for AI-powered responses

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-tutor-pro.git
   cd ai-tutor-pro/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Set up Firebase:
   - Create a Firebase project at [firebase.google.com](https://firebase.google.com/)
   - Enable Authentication (Email/Password and Google providers recommended)
   - Generate a service account key from Project Settings > Service Accounts
   - Save the JSON file and update the `FIREBASE_CREDENTIALS_PATH` in your `.env` file

### Running the Server

Start the development server:

```bash
# Development mode
python -m uvicorn main:app --reload

# Production mode
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000/api/v1/

## Development Guidelines

### Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── qa.py       # QA-related endpoints
│   ├── core/
│   │   ├── auth.py         # Firebase authentication
│   │   └── config.py       # App configuration
│   ├── db/                 # Database models and connections
│   ├── models/
│   │   └── base.py         # Pydantic models
│   └── services/           # Business logic services
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── .env                    # Environment variables (not in git)
```

### Adding New Endpoints

1. Create route handlers in the appropriate files in `app/api/routes/`
2. Define request/response models in `app/models/`
3. Implement business logic in `app/services/`
4. Register routes in `main.py`

### Code Style

- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for all function parameters and return values

## API Documentation

Once the server is running, API documentation is available at:

- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Key Endpoints

#### QA Sessions

- `POST /api/v1/qa/sessions` - Create a new QA session
- `GET /api/v1/qa/sessions` - List all sessions for authenticated user
- `GET /api/v1/qa/sessions/{session_id}` - Get details of a specific session
- `PATCH /api/v1/qa/sessions/{session_id}` - Update a session
- `DELETE /api/v1/qa/sessions/{session_id}` - Delete a session

#### Questions

- `POST /api/v1/qa/ask` - Ask a standalone question
- `POST /api/v1/qa/sessions/{session_id}/ask` - Ask a question in a session

#### History

- `GET /api/v1/qa/history` - Get history of questions and answers

## Authentication

The backend uses Firebase Authentication for user management:

1. Frontend obtains Firebase ID token
2. Token is sent in the Authorization header (`Bearer {token}`)
3. Backend verifies the token using Firebase Admin SDK

Most endpoints require authentication, except for the public ones like health check.

## Deployment Instructions

### Prerequisites

- Docker and Docker Compose (optional, for containerized deployment)
- A server with Python 3.9+ installed (for direct deployment)
- Firebase service account credentials

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t ai-tutor-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env ai-tutor-backend
   ```

### Production Configuration

For production deployments:

1. Set `DEBUG=false` in the `.env` file
2. Configure a proper database (PostgreSQL recommended)
3. Set up proper CORS settings with `CORS_ORIGINS`
4. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

5. Set up reverse proxy (Nginx or similar)

### Database Migration (for SQL databases)

If using SQLAlchemy with migrations:

```bash
# Generate migrations
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Connecting with Frontend

The frontend application expects the backend to be running at the URL specified in its configuration. Make sure the backend's CORS settings include the frontend's origin.

## License

[MIT License](LICENSE)
