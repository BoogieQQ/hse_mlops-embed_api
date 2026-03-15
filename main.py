import asyncio
from fastapi import FastAPI
from routes.simple_embed import router as basic_router
from routes.onnx_embed import router as onnx_router
from routes.dynamic_batch import router as dynamic_batch_router

from contextlib import asynccontextmanager
from routes.dynamic_batch import batch_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(batch_worker())
    yield
    worker_task.cancel()

app = FastAPI(lifespan=lifespan)

app.include_router(basic_router)
app.include_router(onnx_router)
app.include_router(dynamic_batch_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)