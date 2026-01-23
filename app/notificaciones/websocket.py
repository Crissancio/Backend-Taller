from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import Dict, List

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, id_usuario: int, websocket: WebSocket):
        print(f"[WebSocket] Conexión entrante para usuario {id_usuario}")
        await websocket.accept()
        if id_usuario not in self.active_connections:
            self.active_connections[id_usuario] = []
        self.active_connections[id_usuario].append(websocket)
        print(f"[WebSocket] Usuario {id_usuario} conectado. Total conexiones: {len(self.active_connections[id_usuario])}")

    def disconnect(self, id_usuario: int, websocket: WebSocket):
        print(f"[WebSocket] Desconectando usuario {id_usuario}")
        if id_usuario in self.active_connections:
            self.active_connections[id_usuario].remove(websocket)
            if not self.active_connections[id_usuario]:
                del self.active_connections[id_usuario]
        print(f"[WebSocket] Usuario {id_usuario} desconectado. Conexiones restantes: {len(self.active_connections.get(id_usuario, []))}")

    async def send_personal_message(self, message: str, id_usuario: int):
        print(f"[WebSocket] Intentando enviar mensaje a usuario {id_usuario}. Conexiones activas: {list(self.active_connections.keys())}")
        if id_usuario in self.active_connections:
            for idx, connection in enumerate(self.active_connections[id_usuario]):
                print(f"[WebSocket] Enviando mensaje a conexión #{idx+1} de usuario {id_usuario}: {message}")
                try:
                    await connection.send_text(message)
                    print(f"[WebSocket] Mensaje enviado correctamente a conexión #{idx+1} de usuario {id_usuario}")
                except Exception as e:
                    print(f"[WebSocket] Error enviando mensaje a conexión #{idx+1} de usuario {id_usuario}: {e}")
        else:
            print(f"[WebSocket] No hay conexiones activas para usuario {id_usuario}")

    async def broadcast(self, message: str):
        for connections in self.active_connections.values():
            for connection in connections:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/notificaciones/{id_usuario}")
async def websocket_endpoint(websocket: WebSocket, id_usuario: int):
    print(f"[WebSocket] Endpoint iniciado para usuario {id_usuario}")
    await manager.connect(id_usuario, websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Mantener la conexión activa
            print(f"[WebSocket] Mensaje recibido desde el cliente usuario {id_usuario}: {data}")
    except WebSocketDisconnect:
        print(f"[WebSocket] Desconexión detectada para usuario {id_usuario}")
        manager.disconnect(id_usuario, websocket)

# Esta función debe llamarse desde el service de notificaciones cuando se registre una nueva notificación
async def notificar_usuario(id_usuario: int, mensaje: str):
    print(f"[WebSocket] notificar_usuario llamado para usuario {id_usuario} con mensaje: {mensaje}")
    await manager.send_personal_message(mensaje, id_usuario)
