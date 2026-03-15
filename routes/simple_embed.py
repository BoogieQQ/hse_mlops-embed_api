from fastapi import APIRouter
from sentence_transformers import SentenceTransformer
from models.text_request import TextRequest

router = APIRouter()

MODEL_NAME = "sergeyzh/rubert-mini-frida"

model = SentenceTransformer(MODEL_NAME, device="cpu")

@router.post("/simple_embed")
def get_embedding(request: TextRequest):
    embedding = model.encode(request.text)[0]
    return {"embedding": embedding.tolist()}