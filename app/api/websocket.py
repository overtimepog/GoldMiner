from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.goldmine_sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
    
    async def broadcast_json(self, data: dict):
        message = json.dumps(data)
        await self.broadcast(message)
    
    async def send_goldmine_update(self, session_id: str, update_type: str, data: dict):
        """Send goldmine progress updates"""
        message = {
            "type": "goldmine_update",
            "session_id": session_id,
            "update_type": update_type,
            "data": data
        }
        await self.broadcast_json(message)
    
    async def send_idea_update(self, idea_id: int, action: str, data: dict):
        """Send idea updates (create, update, delete)"""
        message = {
            "type": "idea_update",
            "action": action,
            "idea_id": idea_id,
            "data": data
        }
        await self.broadcast_json(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive and echo messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
            
            elif message.get("type") == "goldmine_start":
                session_id = message.get("session_id")
                manager.goldmine_sessions[session_id] = {
                    "status": "active",
                    "progress": {"generated": 0, "validated": 0}
                }
                await manager.send_goldmine_update(
                    session_id, 
                    "started", 
                    {"message": "Goldmining session started"}
                )
            
            elif message.get("type") == "goldmine_stop":
                session_id = message.get("session_id")
                if session_id in manager.goldmine_sessions:
                    manager.goldmine_sessions[session_id]["status"] = "stopped"
                    await manager.send_goldmine_update(
                        session_id,
                        "stopped",
                        {"message": "Goldmining session stopped"}
                    )
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)