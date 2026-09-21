from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers import auth, issues, user_role

app = FastAPI()
app.include_router(auth.router)
app.include_router(issues.router)
app.include_router(user_role.router)

@app.get("/")
async def root():
    return JSONResponse(
        status_code=201,
        content={"message": "Hello World"}
    )
