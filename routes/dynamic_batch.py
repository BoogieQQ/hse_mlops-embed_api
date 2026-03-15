import asyncio
import time
from fastapi import APIRouter, HTTPException
from models.text_request import TextRequest
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

MAX_BATCH_SIZE = 16
MAX_WAIT_TIME = 0.05

MODEL_NAME = "sergeyzh/rubert-mini-frida"
ONNX_PATH = "amekhrishvili/rubert-mini-frida-onnx"

router = APIRouter()

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = ORTModelForFeatureExtraction.from_pretrained(ONNX_PATH, provider="CPUExecutionProvider", file_name='model.onnx')

queue = asyncio.Queue()

async def batch_worker():
    while True:
        items = []
        
        first_item = await queue.get()
        items.append(first_item)
        
        start_time = time.time()
        
        while len(items) < MAX_BATCH_SIZE:
            time_left = MAX_WAIT_TIME - (time.time() - start_time)
            if time_left <= 0:
                break
            
            try:
                item = await asyncio.wait_for(queue.get(), timeout=time_left)
                items.append(item)
            except asyncio.TimeoutError:
                break
        
        texts   = [item['text'] for item in items]
        futures = [item['future'] for item in items]

        inputs = tokenizer(texts, 
                            return_tensors="np", 
                            padding=True, 
                            truncation=True)
    
        embeddings = model.model.run(None, dict(inputs))[0]

        for i, future in enumerate(futures):
            if not future.done():
                future.set_result(embeddings[i].tolist())
        
        for _ in range(len(items)):
            queue.task_done()

@router.post("/onnx_dynamic_batch")
async def get_embedding_dynamic(request: TextRequest):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    
    await queue.put({'text': request.text, 'future': future})
    
    embedding = await future
    return {"embedding": embedding}
   