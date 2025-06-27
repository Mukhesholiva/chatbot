# VoiceBot API

A scalable FastAPI-based voice bot application with authentication and user management features.

## Prerequisites

- Python 3.8+
- SQL Server
- ODBC Driver 17 for SQL Server

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
DB_SERVER=183.82.126.21
DB_NAME=voicebot
DB_USER=sa
DB_PASSWORD=Oliva@9876
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

To run the application:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Available Endpoints

### Authentication
- `POST /token` - Login and get access token

### User Management
- `POST /users/` - Create new user
- `GET /users/me/` - Get current user information
- `POST /users/me/profile/` - Create user profile
- `PUT /users/me/profile/` - Update user profile
- `POST /users/me/change-password/` - Change password

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py          # Main FastAPI application
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic models
│   └── auth.py          # Authentication utilities
├── requirements.txt
└── README.md
```

## Security Notes

- JWT tokens are used for authentication
- Passwords are hashed using bcrypt
- CORS is enabled for all origins (modify in production)
- Environment variables are used for sensitive data

## Next Steps

1. Add more voice bot specific features
2. Implement rate limiting
3. Add logging
4. Add tests
5. Configure production deployment settings 