from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers import auth

app = FastAPI()
app.include_router(auth.router)

@app.get("/")
async def root():
    return JSONResponse(
        status_code=201,
        content={"message": "Hello World"}
    )
