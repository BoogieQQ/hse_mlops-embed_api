from fastapi import APIRouter
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForFeatureExtraction
from models.text_request import TextRequest
import numpy as np


MODEL_NAME = "sergeyzh/rubert-mini-frida"
ONNX_PATH = "amekhrishvili/rubert-mini-frida-onnx"

router = APIRouter()

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = ORTModelForFeatureExtraction.from_pretrained(ONNX_PATH, provider="CPUExecutionProvider", file_name='model.onnx')

@router.post("/onnx_embed")
def get_embedding_onnx(request: TextRequest):
    inputs = tokenizer(
        request.text, 
        return_tensors="np",
        padding=True, 
        truncation=True
    )
    
    embeddings = model.model.run(None, dict(inputs))
    return {"embedding": embeddings[0][0].tolist()}