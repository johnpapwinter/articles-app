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
                    "title": {
                        "type": "text",
                        "analyzer": "custom_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "abstract": {
                        "type": "text",
                        "analyzer": "custom_analyzer"
                    },
                    "publication_date": {"type": "date"},
                    "owner_id": {"type": "integer"}
                }
            }
        }

        await self.es_client.indices.create(index=self.index_name, body=mapping)

    async def index_article(self, article: Article) -> None:
        """Index an article"""
        document = {
            "id": article.id,
            "title": article.title,
            "abstract": article.abstract,
            "publication_date": article.publication_date,
            "owner_id": article.owner_id
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
                "should": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^2", "abstract"],  # Title matches are twice as important
                            "fuzziness": "AUTO" if fuzzy else 0,
                            "minimum_should_match": "70%"
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

    async def verify_index_status(self) -> dict | None:
        """
        Checks the overall status of the articles index.
        Returns information about the index including document count and settings.
        """
        try:
            stats = await self.es_client.indices.stats(index=self.index_name)
            settings = await self.es_client.indices.get_settings(index=self.index_name)

            return {
                "doc_count": stats["_all"]["primaries"]["docs"]["count"],
                "settings": settings[self.index_name]["settings"],
                "health": await self.es_client.cluster.health(index=self.index_name)
            }
        except Exception as e:
            print(f"Error checking index status: {str(e)}")
            return None

    async def test_search_functionality(self, query: str) -> dict:
        """
        Performs a test search and returns detailed information about the results.
        This helps in understanding how Elasticsearch is matching documents.
        """
        try:
            # First, let's check if the index exists
            index_exists = await self.es_client.indices.exists(index=self.index_name)
            if not index_exists:
                return {
                    "status": "error",
                    "message": "Search index does not exist",
                    "details": "The articles index has not been created yet"
                }

            # Perform the search with explanation
            search_response = await self.es_client.search(
                index=self.index_name,
                body={
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["abstract^2", "title"],  # Giving more weight to abstract matches
                            "fuzziness": "AUTO",
                            "minimum_should_match": "70%"
                        }
                    },
                    "explain": True,  # This gives us detailed scoring information
                    "size": 5,  # Limit to top 5 results for clarity
                    "highlight": {  # Add highlighting to see what parts matched
                        "fields": {
                            "abstract": {},
                            "title": {}
                        },
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"]
                    }
                }
            )

            # Get index statistics
            stats = await self.es_client.indices.stats(index=self.index_name)
            total_indexed = stats["_all"]["primaries"]["docs"]["count"]

            # Process the results
            hits = search_response["hits"]["hits"]
            results = []

            for hit in hits:
                result = {
                    "article_id": int(hit["_id"]),
                    "score": hit["_score"],
                    "title": hit["_source"]["title"],
                    "abstract": hit["_source"]["abstract"],
                    "highlights": hit.get("highlight", {}),
                    "match_explanation": self._simplify_explanation(hit["_explanation"])
                }
                results.append(result)

            return {
                "status": "success",
                "query_performed": query,
                "total_documents_indexed": total_indexed,
                "total_matches": search_response["hits"]["total"]["value"],
                "max_score": search_response["hits"]["max_score"],
                "top_matches": results,
                "search_settings": {
                    "fields_searched": ["abstract (weight: 2)", "title (weight: 1)"],
                    "fuzziness": "AUTO",
                    "minimum_should_match": "70%"
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "details": "Error occurred while testing search functionality"
            }

    def _simplify_explanation(self, explanation: dict) -> dict:
        """
        Simplifies the Elasticsearch explanation into more readable format.
        """
        return {
            "description": explanation.get("description", ""),
            "value": explanation.get("value", 0),
            "details": [
                self._simplify_explanation(detail)
                for detail in explanation.get("details", [])
                if detail.get("value", 0) > 0  # Only include positive contributions
            ]
        }
