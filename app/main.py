import uvicorn
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.database import connect_to_mongo

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI()

templates = Jinja2Templates(directory="app/static/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router)

try:
    connect_to_mongo()
    logger.info("DB connection initialized")
except Exception as e:
    logger.error(f"Failed to initialize DB: {str(e)}")

@app.get("/")
async def base_route(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
