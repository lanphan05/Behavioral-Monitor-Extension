"""Tests for session management authentication and user isolation."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_health_is_unauthenticated(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_session_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/sessions", json={"title": "no-auth"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_stop_session_requires_auth(client: AsyncClient) -> None:
    response = await client.post(f"/sessions/{uuid.uuid4()}/stop")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_and_stop_session_for_owner(
    client: AsyncClient,
    user_a_token: str,
) -> None:
    create = await client.post(
        "/sessions",
        headers=auth_header(user_a_token),
        json={"title": "coding", "meta_json": {"editor": "vscode"}},
    )
    assert create.status_code == 201
    body = create.json()
    assert body["title"] == "coding"
    assert body["meta_json"] == {"editor": "vscode"}
    assert body["started_at"] is not None
    assert body["ended_at"] is None
    session_id = body["id"]

    stop = await client.post(
        f"/sessions/{session_id}/stop",
        headers=auth_header(user_a_token),
    )
    assert stop.status_code == 200
    stopped = stop.json()
    assert stopped["id"] == session_id
    assert stopped["ended_at"] is not None
    assert stopped["started_at"] is not None


@pytest.mark.asyncio
async def test_cannot_stop_another_users_session(
    client: AsyncClient,
    user_a_token: str,
    user_b_token: str,
) -> None:
    create = await client.post(
        "/sessions",
        headers=auth_header(user_a_token),
        json={"title": "user-a-session"},
    )
    assert create.status_code == 201
    session_id = create.json()["id"]

    # User B must not be able to stop (or observe) User A's session.
    stop = await client.post(
        f"/sessions/{session_id}/stop",
        headers=auth_header(user_b_token),
    )
    assert stop.status_code == 404

    # Owner can still stop it.
    owner_stop = await client.post(
        f"/sessions/{session_id}/stop",
        headers=auth_header(user_a_token),
    )
    assert owner_stop.status_code == 200
    assert owner_stop.json()["ended_at"] is not None


@pytest.mark.asyncio
async def test_created_session_belongs_to_authenticated_user(
    client: AsyncClient,
    user_a_token: str,
    user_b_token: str,
) -> None:
    created_a = await client.post(
        "/sessions",
        headers=auth_header(user_a_token),
        json={"title": "a"},
    )
    created_b = await client.post(
        "/sessions",
        headers=auth_header(user_b_token),
        json={"title": "b"},
    )
    assert created_a.status_code == 201
    assert created_b.status_code == 201

    user_a_id = (await client.get("/me", headers=auth_header(user_a_token))).json()["id"]
    user_b_id = (await client.get("/me", headers=auth_header(user_b_token))).json()["id"]

    assert created_a.json()["user_id"] == user_a_id
    assert created_b.json()["user_id"] == user_b_id
    assert created_a.json()["user_id"] != created_b.json()["user_id"]


@pytest.mark.asyncio
async def test_stop_unknown_session_returns_404(
    client: AsyncClient,
    user_a_token: str,
) -> None:
    response = await client.post(
        f"/sessions/{uuid.uuid4()}/stop",
        headers=auth_header(user_a_token),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stop_already_stopped_session_returns_409(
    client: AsyncClient,
    user_a_token: str,
) -> None:
    create = await client.post(
        "/sessions",
        headers=auth_header(user_a_token),
        json={"title": "once"},
    )
    session_id = create.json()["id"]
    first = await client.post(
        f"/sessions/{session_id}/stop",
        headers=auth_header(user_a_token),
    )
    second = await client.post(
        f"/sessions/{session_id}/stop",
        headers=auth_header(user_a_token),
    )
    assert first.status_code == 200
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_revoked_token_cannot_manage_sessions(
    client: AsyncClient,
    user_a_token: str,
) -> None:
    # Create a second token, revoke it, then ensure it cannot create sessions.
    listed = await client.get("/tokens", headers=auth_header(user_a_token))
    assert listed.status_code == 200
    token_id = listed.json()[0]["id"]

    created = await client.post(
        "/tokens",
        headers=auth_header(user_a_token),
        json={"name": "temp"},
    )
    assert created.status_code == 201
    temp_token = created.json()["token"]
    temp_id = created.json()["id"]

    revoked = await client.delete(
        f"/tokens/{temp_id}",
        headers=auth_header(user_a_token),
    )
    assert revoked.status_code == 200
    assert revoked.json()["revoked_at"] is not None

    denied = await client.post(
        "/sessions",
        headers=auth_header(temp_token),
        json={"title": "should-fail"},
    )
    assert denied.status_code == 401

    # Original token still works.
    ok = await client.post(
        "/sessions",
        headers=auth_header(user_a_token),
        json={"title": "still-ok"},
    )
    assert ok.status_code == 201
    assert token_id  # fixture token remains listed earlier
