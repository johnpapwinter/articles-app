from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.articles.api.logging_middleware import logger_middleware
from src.articles.api.router import api_router
from src.articles.core.dependencies import get_elasticsearch_client
from src.articles.db.init_db import init_db


@asynccontextmanager
async def lifespan(application: FastAPI):
    await init_db()
    es_client: AsyncElasticsearch = get_elasticsearch_client()
    yield
    await es_client.close()


app = FastAPI(
    title="Articles API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(logger_middleware)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


