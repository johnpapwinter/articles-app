from datetime import timezone, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.auth.password_utils import get_password_hash
from src.articles.core.dependencies import get_elasticsearch_client
from src.articles.models import Author, Tag, User, Article
from src.articles.repositories import ArticleSearchRepository
from src.articles.utils.logging import setup_logging


logger = setup_logging(__name__)


async def init_authors(db: AsyncSession) -> list[Author]:
    """Initialize default authors"""
    default_authors = [
        {"name": "J.R.R. Tolkien"},
        {"name": "R.A. Salvatore"},
        {"name": "Brent Weeks"}
    ]

    created_authors = []
    for author_data in default_authors:
        # Check if author already exists
        query = select(Author).where(Author.name == author_data["name"])
        result = await db.execute(query)
        author = result.scalar_one_or_none()

        if author is None:
            author = Author(**author_data)
            db.add(author)
            # await db.flush()  # Flush to get the ID
            await db.commit()

        created_authors.append(author)

    # await db.commit()
    logger.info("Default authors initialized")
    return created_authors


async def init_tags(db: AsyncSession) -> list[Tag]:
    """Initialize default tags"""
    default_tags = [
        {"name": "Literature"},
        {"name": "Programming"},
        {"name": "Linguistics"},
        {"name": "Medicine"},
    ]

    created_tags = []
    for tag_data in default_tags:
        # Check if tag already exists
        query = select(Tag).where(Tag.name == tag_data["name"])
        result = await db.execute(query)
        tag = result.scalar_one_or_none()

        if tag is None:
            tag = Tag(**tag_data)
            db.add(tag)
            # await db.flush()  # Flush to get the ID
            await db.commit()

        created_tags.append(tag)

    # await db.commit()
    logger.info("Default tags initialized")
    return created_tags


async def init_articles(
        db: AsyncSession,
        authors: list[Author],
        tags: list[Tag],
        users: list[User],
        search_repository: ArticleSearchRepository,
) -> None:
    """Initialize default articles"""

    sample_articles = [
        {
            "title": "First Report",
            "abstract": "In this blog post, we will walk through the process of creating a text search application "
                        "using Elasticsearch and FastAPI. Elasticsearch is a powerful search engine that efficiently "
                        "indexes and searches text data. FastAPI is a modern web framework for building APIs "
                        "with Python that integrates well with Elasticsearch.",
            "publication_date": datetime.now(timezone.utc),
            "owner_id": users[0].id,
            "authors": authors[:2],
            "tags": tags[:3],
        },
        {
            "title": "Parker Probe",
            "abstract": "It used repeated gravity assists from Venus to develop an eccentric orbit, approaching "
                        "within 9.86 solar radii (6.9 million km or 4.3 million miles) from the center of the Sun. "
                        "At its closest approach in 2024, its speed was 690,000 km/h (430,000 mph) or 191 km/s, "
                        "which is 0.064% the speed of light. It is the fastest object ever built on Earth. "
                        "The project was announced in the fiscal 2009 budget year. Johns Hopkins University Applied "
                        "Physics Laboratory designed and built the spacecraft, which was launched on 12 August 2018. "
                        "It became the first NASA spacecraft named after a living person, honoring physicist Eugene "
                        "Newman Parker, professor emeritus at the University of Chicago.",
            "publication_date": datetime.now(timezone.utc),
            "owner_id": users[0].id,
            "authors": authors[2:],
            "tags": tags[:1],
        },
        {
            "title": "Movie",
            "abstract": "A sequel to Gladiator was discussed as early as June 2001, with David Franzoni and John Logan "
                        "set to return as screenwriters. Development was halted when DreamWorks Pictures was sold "
                        "to Paramount in 2006. The film was finally announced in 2018, and Mescal was cast "
                        "in the lead role in January 2023, with a script by Scarpa. Filming took place "
                        "between June 2023 and January 2024, with a five-month delay "
                        "due to the 2023 Hollywood labor disputes.",
            "publication_date": datetime.now(timezone.utc),
            "owner_id": users[0].id,
            "authors": authors[1:],
            "tags": tags[2:],
        },
    ]

    created_articles = []
    for article_data in sample_articles:
        # Check if article already exists
        query = select(Article).where(Article.title == article_data["title"])
        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if article is None:
            # Extract relationships
            article_authors = article_data.pop("authors")
            article_tags = article_data.pop("tags")

            # Create article
            article = Article(**article_data)
            article.authors = article_authors
            article.tags = article_tags
            db.add(article)
            created_articles.append(article)

    await db.commit()

    for article in created_articles:
        await search_repository.index_article(article)

    logger.info("Sample articles initialized")


async def init_users(db: AsyncSession) -> list[User]:
    """Initialize default users"""
    default_users = [
        {"username": "user1", "password": get_password_hash("123")},
        {"username": "user2", "password": get_password_hash("123")},
    ]

    created_users = []
    for user_data in default_users:
        # Check if user already exists
        query = select(User).where(User.username == user_data["username"])
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            user = User(**user_data)
            db.add(user)
            # await db.flush()  # Flush to get the ID
            await db.commit()

        created_users.append(user)

    # await db.commit()
    logger.info("Default users initialized")
    return created_users


async def init_data(db: AsyncSession) -> None:
    """Initialize default data"""
    try:
        # Initialize search repository
        search_repository = ArticleSearchRepository(get_elasticsearch_client())

        await search_repository.create_index()

        # Initialize in order and keep references
        users = await init_users(db)
        authors = await init_authors(db)
        tags = await init_tags(db)

        # Initialize articles with the created entities
        await init_articles(db, authors, tags, users, search_repository)

        logger.info(f"Default data created successfully")
    except Exception as e:
        logger.error(f"Error initializing data: {str(e)}")
        raise

