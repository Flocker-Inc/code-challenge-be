# Flocker Backend Engineering Code Challenge

This challenge is embedded in a **simplified version of the Flocker REST API** — same patterns, naming, and conventions you'll encounter day-to-day.

This challenge is an opportunity for you to display your knowledge of system architecture, design patterns, code quality, and best practices.

**Time expectation:** ~2 hours.

---

## The Application

A simplified Event Feed management API built with:

- **FastAPI** — async web framework
- **SQLAlchemy 2.0** — async ORM
- **SQLite** — database (zero setup, no Docker needed)
- **Pydantic v2** — schema validation
- **Pendulum** — datetime handling
- **uuid6** — UUID7 primary keys
- **pytest + httpx** — testing

### What's the same as the real Flocker codebase

| Convention | This challenge | Flocker production |
|---|---|---|
| **Router → Model → Repo → Schema** | Same 4-layer pattern | Identical |
| **Naming** | `event_feed_model.py`, `event_feeds_repo.py`, `event_feeds_route.py` | Identical convention |
| **Soft deletes** | `deleted` timestamp, filtered in `get_by_id` | Identical |
| **UUID7** | `uuid6.uuid7()` for primary keys | Identical |
| **Pendulum** | All datetimes use Pendulum, not `datetime` | Identical |
| **One schema per resource** | `EventFeedSchema` handles create/read/update | Identical |
| **Async SQLAlchemy** | `async with get_async_session()` | Identical |
| **Auth** | Auth enforced at router level | Same concept (simplified) |
| **Repo pattern** | `BaseRepo[T]` with `get_by_id`, `create`, `update`, `delete` | Identical |
| **Test split** | Model tests + repo tests + API tests | Identical |

### What's simplified

| Aspect | This challenge | Flocker production |
|---|---|---|
| **Database** | SQLite (zero setup) | PostgreSQL 15 + asyncpg |
| **Auth** | Static API key | FastAPI Users + JWT + CloudFront cookies |
| **Model** | Flat columns | Mega-tables with JSONB, H3 geospatial, relationships |

The patterns are the same — the complexity is reduced so you can focus on architecture, not infrastructure.

### Architecture Pattern

The code follows the **Router → Model → Repo → Schema** pattern:

| Layer | Directory | Convention |
|---|---|---|
| **Model** | `src/models/` | Singular `_model.py` |
| **Schema** | `src/schemas/` | Singular `_schema.py` |
| **Repo** | `src/repos/` | Plural `_repo.py` |
| **Router** | `src/routers/` | Plural `_route.py` |
| **Core** | `src/core/` | Base classes |

Key conventions:
- **Routers** handle auth + orchestration only — no business logic
- **Repos** are thin query wrappers — no business logic
- **Schemas** handle serialization and validation — one schema per resource
- **Soft deletes** — records get a `deleted` timestamp instead of being removed
- **UUID7** for time-sortable primary keys
- **Pendulum** for all datetime handling
- Auth via `X-API-Key` header

### Project Structure

```
flocker-code-challenge-be/
├── pyproject.toml
├── src/
│   ├── app.py                    # FastAPI entry point
│   ├── session.py                # Database session management
│   ├── auth.py                   # API key authentication
│   ├── core/
│   │   ├── base_model.py         # Base + BaseModel (soft delete, UUID7, Pendulum)
│   │   ├── base_schema.py        # BaseSchema (from_attributes=True)
│   │   └── base_repo.py          # BaseRepo[T] (CRUD + soft delete)
│   ├── models/
│   │   ├── event_feed_model.py           # EventFeedModel
│   │   └── event_feed_reactions_model.py # EventFeedReactionsModel (you create)
│   ├── schemas/
│   │   └── event_feed_schema.py          # EventFeedSchema
│   ├── repos/
│   │   ├── event_feeds_repo.py           # EventFeedRepo
│   │   └── event_feed_reactions_repo.py  # EventFeedReactionsRepo (you create)
│   └── routers/
│       └── event_feeds_route.py          # /event_feeds/ CRUD endpoints
└── tests/
    ├── conftest.py
    └── test_event_feeds.py       # Tests (model/repo/API)
```

### Getting Started

```bash
uv sync
uv run pytest
uv run uvicorn src.app:app  # Run the server
```

Test the running server:

```bash
curl -H "X-API-Key: flocker-challenge-key-2024" http://localhost:8000/event_feeds/
```

---

### Background

In the real Flocker codebase, data is stored in two complementary layers:
- **Satellite tables**: source-of-truth for individual interactions (reactions, comments, members)
- **Mega-tables**: denormalized JSON columns on the main resource for single-read performance

The `EventFeedModel` currently has flat columns only — no satellite or mega-table pattern exists.

The challenge tests your ability to extend both storage layers, design Pydantic schemas with validation, and handle a dual-write path across the 4-layer architecture.

## Requirements

**Add reactions to Event Feeds.**

An event feed should track reactions — likes, loves, fires, laughs, supports. Each individual reaction is recorded in a satellite `event_feed_reactions` table (source of truth). Reaction counts are denormalized on `EventFeedModel` so that list endpoints return counts in a single read — no N+1 queries.

- `POST /event_feeds/{feed_id}/reactions` accepts `{"reaction": "like"}` and writes to **both** the satellite table and the denormalized JSON column on `EventFeedModel`
- `GET /event_feeds/` and `GET /event_feeds/{id}` return the denormalized reaction counts
- Invalid reaction types are rejected

Valid reaction types: `like`, `love`, `fire`, `laugh`, `support`

---

## Submission

Send us your completed repository