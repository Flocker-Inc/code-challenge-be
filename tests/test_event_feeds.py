import pytest
from uuid6 import uuid7

from src.models.event_feed_model import EventFeedModel
from src.repos.event_feeds_repo import EventFeedRepo


class TestEventFeedModel:
    def test_create_event_feed(self):
        feed = EventFeedModel(
            host_user_id="user-123",
            title="Test Event",
            description="A test",
            status="draft",
        )
        assert feed.title == "Test Event"
        assert feed.status == "draft"
        assert feed.is_deleted is False

    def test_soft_delete(self):
        feed = EventFeedModel(host_user_id="u1", title=" deletable")
        feed.soft_delete()
        assert feed.is_deleted is True
        assert feed.deleted is not None

    def test_restore(self):
        feed = EventFeedModel(host_user_id="u1", title="restorable")
        feed.soft_delete()
        feed.restore()
        assert feed.is_deleted is False


class TestEventFeedRepo:
    async def test_create_and_get_by_id(self, session):
        repo = EventFeedRepo(session)
        feed = EventFeedModel(host_user_id="u1", title="My Event")
        created = await repo.create(feed)
        assert created.id is not None

        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.title == "My Event"

    async def test_get_by_id_returns_none_for_nonexistent(self, session):
        repo = EventFeedRepo(session)
        found = await repo.get_by_id(uuid7())
        assert found is None

    async def test_get_by_id_excludes_deleted(self, session):
        repo = EventFeedRepo(session)
        feed = EventFeedModel(host_user_id="u1", title="will be deleted")
        await repo.create(feed)
        await repo.delete(feed.id)

        found = await repo.get_by_id(feed.id)
        assert found is None

    async def test_update(self, session):
        repo = EventFeedRepo(session)
        feed = EventFeedModel(host_user_id="u1", title="Original")
        await repo.create(feed)

        updated = await repo.update(feed.id, {"title": "Updated"})
        assert updated is not None
        assert updated.title == "Updated"

    async def test_update_returns_none_for_missing(self, session):
        repo = EventFeedRepo(session)
        result = await repo.update(uuid7(), {"title": "Nope"})
        assert result is None

    async def test_delete_soft(self, session):
        repo = EventFeedRepo(session)
        feed = EventFeedModel(host_user_id="u1", title=" deletable")
        await repo.create(feed)

        success = await repo.delete(feed.id)
        assert success is True

        found = await repo.get_by_id(feed.id)
        assert found is None

    async def test_delete_returns_false_for_missing(self, session):
        repo = EventFeedRepo(session)
        result = await repo.delete(uuid7())
        assert result is False

    async def test_list(self, session):
        repo = EventFeedRepo(session)
        for i in range(3):
            await repo.create(EventFeedModel(host_user_id="u1", title=f"Event {i}"))

        feeds = await repo.list()
        assert len(feeds) >= 3

    async def test_list_excludes_deleted(self, session):
        repo = EventFeedRepo(session)
        e1 = EventFeedModel(host_user_id="u1", title="keep")
        e2 = EventFeedModel(host_user_id="u1", title="delete")
        await repo.create(e1)
        await repo.create(e2)
        await repo.delete(e2.id)

        feeds = await repo.list()
        titles = [f.title for f in feeds]
        assert "keep" in titles
        assert "delete" not in titles


class TestEventFeedAPI:
    async def test_create_event_feed(self, client, auth_headers):
        response = await client.post(
            "/event_feeds/",
            json={"host_user_id": "u1", "title": "API Event", "description": "Via API"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Event"
        assert data["id"] is not None

    async def test_list_event_feeds(self, client, auth_headers):
        await client.post(
            "/event_feeds/", json={"host_user_id": "u1", "title": "Listable"}, headers=auth_headers
        )
        response = await client.get("/event_feeds/", headers=auth_headers)
        assert response.status_code == 200
        titles = [f["title"] for f in response.json()]
        assert "Listable" in titles

    async def test_get_event_feed(self, client, auth_headers):
        create_resp = await client.post(
            "/event_feeds/", json={"host_user_id": "u1", "title": "Gettable"}, headers=auth_headers
        )
        feed_id = create_resp.json()["id"]

        response = await client.get(f"/event_feeds/{feed_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Gettable"

    async def test_get_event_feed_not_found(self, client, auth_headers):
        response = await client.get(f"/event_feeds/{uuid7()}", headers=auth_headers)
        assert response.status_code == 404

    async def test_update_event_feed(self, client, auth_headers):
        create_resp = await client.post(
            "/event_feeds/", json={"host_user_id": "u1", "title": "Updatable"}, headers=auth_headers
        )
        feed_id = create_resp.json()["id"]

        response = await client.put(
            f"/event_feeds/{feed_id}",
            json={"title": "Updated"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    async def test_delete_event_feed(self, client, auth_headers):
        create_resp = await client.post(
            "/event_feeds/", json={"host_user_id": "u1", "title": "Deletable"}, headers=auth_headers
        )
        feed_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/event_feeds/{feed_id}", headers=auth_headers)
        assert delete_resp.status_code == 200

        get_resp = await client.get(f"/event_feeds/{feed_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    async def test_unauthorized_without_key(self, client):
        response = await client.get("/event_feeds/")
        assert response.status_code == 401

    async def test_unauthorized_with_wrong_key(self, client):
        response = await client.get("/event_feeds/", headers={"X-API-Key": "wrong"})
        assert response.status_code == 401
