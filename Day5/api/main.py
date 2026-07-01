"""DevOps Monitoring API — FastAPI application entrypoint."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from api.auth import verify_api_key
from api.metrics import get_system_metrics
from api.models import Server, ServerIn, ServerOut
from api.poller import run_poll_loop

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# --- In-memory store -------------------------------------------------------
_store: dict[int, Server] = {}
_counter = 0
_stop_event = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the background poller on startup, stop it cleanly on shutdown."""
    _stop_event.clear()
    poll_task = asyncio.create_task(run_poll_loop(_store, _stop_event))
    logger.info("Poller started")
    yield
    _stop_event.set()
    await poll_task
    logger.info("Poller stopped")


app = FastAPI(title="DevOps Monitoring API", version="1.0", lifespan=lifespan)


# --- Health & metrics --------------------------------------------------------

@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    """Current CPU / memory / disk usage snapshot."""
    return get_system_metrics()


# --- Servers CRUD ------------------------------------------------------------

@app.post("/servers", response_model=ServerOut, status_code=201)
async def register_server(server: ServerIn, api_key: str = Depends(verify_api_key)):
    global _counter
    _counter += 1
    record = Server(
        id=_counter,
        name=server.name,
        host=server.host,
        port=server.port,
        tags=server.tags,
    )
    _store[_counter] = record
    return record


@app.get("/servers", response_model=list[ServerOut])
async def list_servers():
    return list(_store.values())


@app.delete("/servers/{server_id}", status_code=204)
async def delete_server(server_id: int, api_key: str = Depends(verify_api_key)):
    if server_id not in _store:
        raise HTTPException(404, "Server not found")
    del _store[server_id]


@app.post("/servers/{server_id}/check", response_model=ServerOut)
async def trigger_check(server_id: int):
    import httpx

    from api.poller import poll_server

    if server_id not in _store:
        raise HTTPException(404, "Server not found")
    server = _store[server_id]
    async with httpx.AsyncClient() as client:
        server = await poll_server(server, client)
    return server


# --- WebSocket: live metrics stream ------------------------------------------

@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    """Stream a metrics snapshot as JSON once per second until disconnect."""
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(get_system_metrics())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
