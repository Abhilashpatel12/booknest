from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.models import User, Book, Shelf, BookStatus, Lending, Activity, ShelfShare, ShareRole
from app.schemas import BookCreate, BookResponse, BookUpdate, ShelfCreate, ShelfResponse, ShelfUpdate, LendBookRequest, LendingResponse, ShareShelfRequest, UpdateRoleRequest, SharedUserResponse, SignupRequest, LoginRequest, RefreshTokenRequest
from app.core.jwt_handler import verify_access_token
from typing import Dict, List
import json
import asyncio

router = APIRouter(prefix="/ws", tags=["websockets"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.main_loop = None

    async def connect(self, websocket: WebSocket, user_id: int):
        if self.main_loop is None:
            self.main_loop = asyncio.get_running_loop()
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    dead_connections.append(connection)
            
            for dead in dead_connections:
                self.disconnect(dead, user_id)

    def send_personal_message_sync(self, message: dict, user_id: int):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.send_personal_message(message, user_id))
        except RuntimeError:
            if getattr(self, "main_loop", None):
                asyncio.run_coroutine_threadsafe(self.send_personal_message(message, user_id), self.main_loop)

manager = ConnectionManager()

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    payload = verify_access_token(token, expected_type="access")
    if not payload or not payload.get("sub"):
        await websocket.close(code=1008)
        return
        
    user_id = int(payload.get("sub"))
    
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
    except Exception:
        pass
    finally:
        manager.disconnect(websocket, user_id)
