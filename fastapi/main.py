from fastapi import FastAPI

app = FastAPI()

@app.get("/main/")
def leer_main():
    return {"mensaje": "¡Hola desde FastAPI en PythonAnywhere!"}
