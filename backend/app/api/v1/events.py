import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.sse_service import sse_manager

router = APIRouter(tags=["Real-time Events (SSE)"])

@router.get("/devices/{device_id}/events")
async def stream_device_events(device_id: str, request: Request):
    """
    Server-Sent Events (SSE) stream dedicated to a specific device.
    Emits real-time telemetry, pump state transitions, and alert notifications.
    """
    queue = await sse_manager.subscribe(device_id)

    async def event_generator():
        try:
            # Send initial ping event
            yield f": ping connected to device {id}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Wait up to 15s for new event or send heartbeat keep-alive
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield data
                except asyncio.TimeoutError:
                    yield ": keepalive heartbeat\n\n"
        finally:
            await sse_manager.unsubscribe(queue, id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.get("/events")
async def stream_all_events(request: Request):
    """
    Global Server-Sent Events stream for multi-device dashboard monitoring.
    """
    queue = await sse_manager.subscribe("all")

    async def event_generator():
        try:
            yield ": ping connected to global event stream\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield data
                except asyncio.TimeoutError:
                    yield ": keepalive heartbeat\n\n"
        finally:
            await sse_manager.unsubscribe(queue, "all")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
