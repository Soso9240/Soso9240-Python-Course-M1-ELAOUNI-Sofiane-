"""Data models for the DevOps Monitoring API.

Contains:
- Server: internal dataclass representing a monitored server.
- ServerIn / ServerOut: Pydantic schemas used at the API boundary.
"""

from dataclasses import dataclass, field

from pydantic import BaseModel, Field


@dataclass
class Server:
    """Internal representation of a monitored server."""

    id: int
    name: str
    host: str
    port: int
    status: str = "unknown"
    tags: list[str] = field(default_factory=list)

    def base_url(self) -> str:
        """Return the base HTTP URL used to reach this server."""
        return f"http://{self.host}:{self.port}"


class ServerIn(BaseModel):
    """Payload accepted when registering a new server."""

    name: str
    host: str
    port: int = Field(default=8080, ge=1, le=65535)
    tags: list[str] = []


class ServerOut(BaseModel):
    """Payload returned to API clients describing a server."""

    id: int
    name: str
    host: str
    port: int
    status: str
    tags: list[str] = []

    model_config = {"from_attributes": True}
