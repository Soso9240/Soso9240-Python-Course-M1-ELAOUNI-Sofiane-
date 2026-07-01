"""Background polling of registered servers' health status."""

import asyncio
import logging

import httpx

from api.models import Server

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 10
CHECK_TIMEOUT_SECONDS = 5.0
DEGRADED_THRESHOLD_MS = 500.0


async def poll_server(server: Server, client: httpx.AsyncClient) -> Server:
    """Check a single server's /health endpoint and update its status.

    Status rules:
      - UP: HTTP 200 and response time <= DEGRADED_THRESHOLD_MS
      - DEGRADED: HTTP 200 but slow, or a non-200 response
      - DOWN: connection error or timeout
    """
    import time

    start = time.monotonic()
    try:
        resp = await client.get(
            f"{server.base_url()}/health", timeout=CHECK_TIMEOUT_SECONDS
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        if resp.status_code == 200 and elapsed_ms <= DEGRADED_THRESHOLD_MS:
            server.status = "UP"
        else:
            server.status = "DEGRADED"
    except (httpx.ConnectError, httpx.TimeoutException):
        server.status = "DOWN"
    return server


async def run_poll_loop(servers: dict[int, Server], stop_event: asyncio.Event) -> None:
    """Continuously poll all registered servers every POLL_INTERVAL_SECONDS.

    `servers` is the shared in-memory store (mutated in place).
    `stop_event` lets the FastAPI lifespan cancel the loop cleanly on shutdown.
    """
    async with httpx.AsyncClient() as client:
        while not stop_event.is_set():
            if servers:
                await asyncio.gather(
                    *(poll_server(s, client) for s in servers.values())
                )
                logger.info("Polled %d server(s)", len(servers))
            try:
                await asyncio.wait_for(
                    stop_event.wait(), timeout=POLL_INTERVAL_SECONDS
                )
            except asyncio.TimeoutError:
                pass  # normal: just means it's time to poll again
