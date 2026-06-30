# BookNest Backend

Welcome to the backend for **BookNest**! This is a robust RESTful API built with FastAPI that powers a personal library management and social book-sharing platform.

## Features

- **Authentication System**: Secure JWT-based signup, login, and token refreshing.
- **Library Management**: Add, update, delete, and track your personal books. Manage reading statuses (e.g., Reading, Finished, Want to Read).
- **Shelves**: Organize books into custom shelves.
- **Collaborative Sharing**: Share shelves with other users using Role-Based Access Control (RBAC). Assign 'viewer' or 'editor' roles to collaborators.
- **Lending System**: Lend books to friends, track who borrowed what, and mark them as returned.
- **Dashboard & Analytics**: Aggregate statistics for total books, pages read, average ratings, and recent activity.
- **Real-time WebSockets**: Live event broadcasting for instant updates across the app.
- **Activity Feed**: Detailed logging of user actions (books added, lent, returned, etc.).

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: PostgreSQL (managed via SQLAlchemy ORM)
- **Data Validation**: Pydantic
- **Authentication**: JWT (JSON Web Tokens) & bcrypt password hashing
- **Real-time**: FastAPI WebSockets

## Project Structure

The project follows a clean, modular architecture:

```
app/
├── api/          # FastAPI routers and endpoints
├── core/         # Core configuration, security, database setup, and dependencies
├── crud/         # Generic CRUD operations and specific database interactions
├── models/       # SQLAlchemy database models
├── schemas/      # Pydantic validation schemas
└── main.py       # FastAPI application entry point
```

## Setup & Installation

1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

2. **Set up a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt python-multipart psycopg2-binary
   ```

4. **Environment Variables**
   Create a `.env` file in the `backend` directory (if not already present) and configure your secrets:
   ```env
   SECRET_KEY=your_super_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

5. **Run the Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be running at `http://127.0.0.1:8000`.

## API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## WebSocket Architecture & Security

We use native WebSockets for real-time updates. Polling is not used. 

**Authentication & Security:**
Native `WebSocket` connections in browsers do not support custom HTTP headers (like `Authorization: Bearer`). To secure the socket, the client must pass the JWT access token as a query parameter: `ws://127.0.0.1:8000/ws?token=<access_token>`. The server decodes and verifies this token; if invalid, it drops the connection immediately with code `1008 Policy Violation`.

**Event Scoping:**
The server maintains an in-memory dictionary (`ConnectionManager`) of active connections mapped by `user_id`. Events are strictly scoped and never broadcast globally:
- **Lending:** When a book is lent or returned, a targeted event is dispatched explicitly to the lender and the borrower.
- **Shelves:** When a shared shelf is updated, the server queries the database for all collaborators (the owner + all users with shared roles on that shelf) and dispatches the update exclusively to them.

**Disconnect Handling:**
Clients must handle socket drops gracefully. The app should continue to function via standard REST calls (and manual refreshes). The frontend should attach an `onclose` listener to the socket and attempt to reconnect using exponential backoff. Upon successful reconnection, the client should fetch the latest state via REST to ensure no events were missed during the downtime.
