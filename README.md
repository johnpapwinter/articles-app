# Articles API

A FastAPI-based REST API for managing articles, authors, comments, and tags with Elasticsearch integration for advanced search capabilities.

## Features

- User authentication with JWT tokens
- Article management with full CRUD operations
- Comment system for articles
- Tag-based article categorization
- Author management
- Elasticsearch integration for powerful article search
- PostgreSQL database with SQLAlchemy ORM
- Containerized deployment with Docker

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- Elasticsearch 8.16.2
- SQLAlchemy
- Poetry for dependency management
- Docker & Docker Compose
- JWT for authentication

## Prerequisites

- Docker and Docker Compose
- Poetry (for local development)

## Getting Started

### Running with Docker

1. Clone the repository
2. Start the services:
   ```bash
   docker-compose up -d
   ```

The application will be available at `http://localhost:8000`

### Local Development Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Activate the virtual environment:
   ```bash
   poetry shell
   ```

3. Run the application:
   ```bash
   uvicorn src.articles.main:app --reload
   ```

## API Endpoints

### Authentication

#### Login
* **Path**: `/auth/login`
* **Method**: `POST`
* **Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```
* **Response**:
```json
{
    "access_token": "string (JWT token)"
}
```
* **Description**: Returns a JWT token that must be used as a Bearer token to access protected endpoints.

### Users

#### Create User
* **Path**: `/users`
* **Method**: `POST`
* **Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```
* **Response**:
```json
{
    "id": "integer",
    "username": "string"
}
```

### Articles

#### Create Article
* **Path**: `/articles/create`
* **Method**: `POST`
* **Authorization**: Bearer Token required
* **Request Body**:
```json
{
    "title": "string",
    "abstract": "string",
    "publication_date": "date",
    "author_ids": ["integer"],
    "tag_ids": ["integer"]
}
```

#### Get Article
* **Path**: `/articles/get/{article_id}`
* **Method**: `GET`
* **Authorization**: Bearer Token required
* **Response**:
```json
{
    "id": "integer",
    "title": "string",
    "abstract": "string",
    "publication_date": "date",
    "authors": ["Author"],
    "tags": ["Tag"],
    "owner_id": "integer"
}
```

#### Update Article
* **Path**: `/articles/{article_id}`
* **Method**: `PUT`
* **Authorization**: Bearer Token required
* **Description**: Only the owner can update the article

#### Delete Article
* **Path**: `/articles/{article_id}`
* **Method**: `DELETE`
* **Authorization**: Bearer Token required
* **Description**: Only the owner can delete the article

#### Search Articles
* **Path**: `/articles/search`
* **Method**: `POST`
* **Query Parameters**:
  * `page`: integer (default: 1)
  * `page_size`: integer (default: 10, max: 100)
* **Request Body**: ArticleSearchFilters object
* **Response**: Paginated list of articles

### Comments

#### Create Comment
* **Path**: `/comments`
* **Method**: `POST`
* **Authorization**: Bearer Token required
* **Request Body**:
```json
{
    "content": "string",
    "article_id": "integer"
}
```

#### Get Comment
* **Path**: `/comments/{comment_id}`
* **Method**: `GET`

#### Update Comment
* **Path**: `/comments/{comment_id}`
* **Method**: `PUT`
* **Authorization**: Bearer Token required
* **Description**: Only the comment author can update it

#### Delete Comment
* **Path**: `/comments/{comment_id}`
* **Method**: `DELETE`
* **Authorization**: Bearer Token required
* **Description**: Only the comment author can delete it

### Authors

#### Create Author
* **Path**: `/authors`
* **Method**: `POST`
* **Request Body**:
```json
{
    "name": "string",
    "bio": "string"
}
```

### Tags

#### Create Tag
* **Path**: `/tags`
* **Method**: `POST`
* **Request Body**:
```json
{
    "name": "string"
}
```

## Environment Configuration

The application uses the following services:

### PostgreSQL
- Port: 5433
- Default database: articles_db
- Default user: postgres

### Elasticsearch
- Port: 9200
- Single node configuration
- Security disabled for development

## Testing

Run the tests using pytest:
```bash
poetry run pytest
```

