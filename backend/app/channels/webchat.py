"""
Web Chat Channel Adapter
WebSocket-based real-time chat for web and mobile apps
"""
from typing import Dict, Any, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import uuid

from app.services.nlu_service import nlu_service
from app.services.dialogue_manager import dialogue_manager, DialogueState

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, DialogueState] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        session_id = str(uuid.uuid4())
        self.active_connections[session_id] = websocket
        self.sessions[session_id] = DialogueState()
        return session_id
    
    def disconnect(self, session_id: str):
        """Remove connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific session"""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))
    
    def get_session(self, session_id: str) -> DialogueState:
        """Get dialogue state for session"""
        return self.sessions.get(session_id, DialogueState())


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for web chat"""
    session_id = await manager.connect(websocket)
    
    # Send welcome message
    await manager.send_message(session_id, {
        "type": "system",
        "message": "Connected to Bangla AI",
        "session_id": session_id
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                text = message_data.get("text", "")
                
                # Echo user message
                await manager.send_message(session_id, {
                    "type": "user",
                    "text": text,
                    "timestamp": message_data.get("timestamp")
                })
                
                # Process through NLU
                nlu_result = nlu_service.resolve(text)
                
                # Get dialogue state
                state = manager.get_session(session_id)
                
                # Process through DM
                dm_result = dialogue_manager.decide(
                    intent=nlu_result["intent"],
                    entities=nlu_result["entities"],
                    context={"channel": "webchat", "session_id": session_id},
                    state=state
                )
                
                # Send bot response
                await manager.send_message(session_id, {
                    "type": "bot",
                    "text": dm_result["response_text_bn"],
                    "intent": nlu_result["intent"],
                    "confidence": nlu_result["confidence"],
                    "action": dm_result["action"],
                    "timestamp": message_data.get("timestamp")
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(session_id)

