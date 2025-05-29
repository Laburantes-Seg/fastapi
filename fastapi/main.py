uvicorn main:app --host 0.0.0.0 --port 10000
from fastapi import FastAPI

app = FastAPI()

@app.get("/main/")
def leer_main():
    return {"mensaje": "¡Hola desde FastAPI en 62 # 819!"}
