"""The async trap, isolated. Run:  uvicorn async_trap:app --port 8002"""
import time

from fastapi import FastAPI

app = FastAPI()


@app.post("/slow-async")
async def slow_async():
    time.sleep(0.2)        # noqa: ASYNC251  blocking inside async def: the bug is the point
    return {"ok": True}


@app.post("/slow-def")
def slow_def():
    time.sleep(0.2)        # the same call in a plain def runs in a worker thread
    return {"ok": True}
