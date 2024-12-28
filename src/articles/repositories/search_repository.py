from typing import List

from elasticsearch import AsyncElasticsearch

from src.articles.models import Article


class ArticleSearchRepository:
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client
        self.index_name = "articles"

    async def create_index(self) -> None:
        """Creates an Elasticsearch index with appropriate mappings for article search"""
        if await self.es_client.indices.exists(index=self.index_name):
            return

        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "custom_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "abstract": {
                        "type": "text",
                        "analyzer": "custom_analyzer"
                    }
                }
            }
        }

        await self.es_client.indices.create(index=self.index_name, body=mapping)

    async def index_article(self, article: Article) -> None:
        """Index an article"""
        document = {
            "id": article.id,
            "abstract": article.abstract
        }

        await self.es_client.index(index=self.index_name, id=str(article.id), document=document)

    async def delete_article(self, article_id: int) -> None:
        """Removes an article from the index"""
        await self.es_client.delete(index=self.index_name, id=str(article_id))

    async def search_articles(
            self,
            query: str,
            fuzzy: bool = True,
            min_score: float = 0.5,
            size: int = 20
    ) -> List[int]:
        """
        Searches for articles matching the query text.
        Returns a list of article IDs ordered by relevance.
        """
        search_query = {
            "bool": {
                "must": [
                    {
                        "match": {
                            "abstract": {
                                "query": query,
                                "fuzziness": "AUTO" if fuzzy else 0,
                                "minimum_should_match": "70%"
                            }
                        }
                    }
                ]
            }
        }

        response = await self.es_client.search(
            index=self.index_name,
            query=search_query,
            size=size,
            min_score=min_score,
            _source=["id"]
        )

        return [int(hit["_source"]["id"]) for hit in response["hits"]["hits"]]

    async def verify_article_indexed(self, article_id: int) -> dict | None:
        """
        Retrieves an indexed article directly from Elasticsearch.
        Returns the full indexed document if found, otherwise returns None.
        """
        try:
            result = await self.es_client.get(
                index=self.index_name,
                id=str(article_id)
            )
            return result['_source']
        except Exception as e:
            print(f"Error retrieving article {article_id}: {str(e)}")
            return None

