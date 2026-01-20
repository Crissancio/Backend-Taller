from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, id_usuario: int, websocket: WebSocket):
        await websocket.accept()
        if id_usuario not in self.active_connections:
            self.active_connections[id_usuario] = []
        self.active_connections[id_usuario].append(websocket)

    def disconnect(self, id_usuario: int, websocket: WebSocket):
        if id_usuario in self.active_connections:
            self.active_connections[id_usuario].remove(websocket)
            if not self.active_connections[id_usuario]:
                del self.active_connections[id_usuario]

    async def send_personal_message(self, message: str, id_usuario: int):
        if id_usuario in self.active_connections:
            for connection in self.active_connections[id_usuario]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/notificaciones/{id_usuario}")
async def websocket_endpoint(websocket: WebSocket, id_usuario: int):
    await manager.connect(id_usuario, websocket)
    try:
        while True:
            await websocket.receive_text()  # Mantener la conexión activa
    except WebSocketDisconnect:
        manager.disconnect(id_usuario, websocket)

# Esta función debe llamarse desde el service de notificaciones cuando se registre una nueva notificación
async def notificar_usuario(id_usuario: int, mensaje: str):
    await manager.send_personal_message(mensaje, id_usuario)
