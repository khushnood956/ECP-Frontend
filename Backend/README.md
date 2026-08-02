# EduConsultant Backend

EduConsultant is a production-grade educational guidance platform consisting of Student, Agency, and Admin portals. This repository contains the backend service.

## Tech Stack
- **Python:** 3.10+ (Targets up to 3.14)
- **Framework:** FastAPI
- **Database:** MySQL with SQLAlchemy 2.0 (async via aiomysql)
- **Migrations:** Alembic
- **Caching:** Redis
- **Containerization:** Docker
- **Testing:** Pytest

## Architecture
The project follows Domain-Driven Design principles with a feature-first approach, adhering to SOLID, DRY, KISS, and YAGNI. 
- **API Layer:** FastAPI routers (No business logic).
- **Service Layer:** Core business logic orchestration.
- **Repository Layer:** Data access abstraction using SQLAlchemy 2.0 Async.
- **Dependency Injection:** Centralized via FastAPI's `Depends`.

## Folder Structure
- `app/api/`: API Routers and endpoints.
- `app/core/`: Application-wide settings, logging, and security configuration.
- `app/common/`: Common utilities, responses, and schemas.
- `app/db/`: Database session management, engine config, and Declarative Base.
- `app/models/`: SQLAlchemy declarative models.
- `app/schemas/`: Pydantic validation schemas.
- `app/repositories/`: Data access layer.
- `app/services/`: Business logic.
- `tests/`: Pytest suites.
- `alembic/`: Database migrations.

## Getting Started

### 1. Set Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Modify `.env` with your local database credentials.

### 2. Install Dependencies
```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn main:app --reload
```
Access the API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Running Tests
```bash
pytest
```

## System Standards

### Logging
The application uses structured logging via Python's built-in `logging` module, attached with a `RequestIDFilter`.
- **Location**: `app/core/logging/logger.py`
- All logs explicitly mask sensitive secrets, include request context (Request ID), and dynamically shift log levels based on the `LOG_LEVEL` environment variable.

### Exception Hierarchy & Handling
Global error handling is centralized in `app/core/exceptions/`.
- Every custom business error inherits from `ApplicationException`.
- FastAPI's native `RequestValidationError` and `HTTPException` are seamlessly intercepted.
- Stack traces are completely sanitized and never leaked to the client.

### Standardized Response Formats
All API responses follow a strict Pydantic JSON structure for front-end consistency:
- **Location**: `app/common/schemas/responses.py`
- **Helpers**: `app/common/utils/responses.py` provides `success_response()` and `error_response()`.

### Request ID & Traceability
A central middleware (`app/middleware/request_id.py`) generates a distinct UUID for every incoming HTTP request. This `X-Request-ID` is passed into the `contextvars`, making it immediately accessible inside the logger, and is returned inside the final HTTP Response Header.

### Database Architecture
- **Engine Configuration (`app/db/database.py`)**: Uses SQLAlchemy 2.0's `create_async_engine` configured safely with `pool_pre_ping=True` and `pool_recycle`.
- **Session Lifecycle (`app/db/session.py`)**: Yields an `AsyncSession` injected into endpoints via `Depends(get_db)`. It automatically issues rollbacks upon `Exception` interrupts.
- **Declarative Base (`app/db/base.py`)**: Supplies the master ORM base `Base` alongside standard `TimestampMixin` and `UUIDPrimaryKeyMixin`.

### Entity-Relationship (ER) Architecture
The domain entities are strictly isolated into single-responsibility tables mapped via SQLAlchemy in `app/models/`:
- **User**: The root authentication identity. Owns either a `StudentProfile` OR an `Agency` profile via strict 1-to-1 relationships.
- **StudentProfile**: Contains demographic and academic data. Has a 1-to-Many relationship with `Lead`.
- **Agency**: Educational agencies. Has a 1-to-Many relationship with `Lead`.
- **Scholarship**: Opportunities created by admins/system. Has a 1-to-Many relationship with `Lead`.
- **Lead**: The core pivot bridging a `Student` and a `Scholarship`. Optionally facilitated by an `Agency`.

**Constraints & Indexes**:
- UUIDs are utilized for all primary and foreign keys for decentralized scaling.
- Unique constraints exist on `User.email` and `user_id` inside profiles (enforcing 1-to-1).
- Indexes are dynamically applied on search-heavy columns: `country`, `email`, `status`, and `deadline`.

**Migration Notes**:
To create new migrations after adding models, ensure the model is imported in `app/models/__init__.py`, then run:
```bash
alembic revision --autogenerate -m "Migration description"
alembic upgrade head
```
