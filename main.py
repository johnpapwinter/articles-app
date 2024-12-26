import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.articles.api import logging_middleware
from src.articles.api.router import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.middleware("http")(logging_middleware)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


