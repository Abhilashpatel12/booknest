#!/bin/bash
source venv/bin/activate
pip install -r requirements.txt 2>/dev/null || pip install 'uvicorn[standard]' websockets fastapi sqlalchemy pydantic python-jose passlib bcrypt python-multipart psycopg2-binary
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
