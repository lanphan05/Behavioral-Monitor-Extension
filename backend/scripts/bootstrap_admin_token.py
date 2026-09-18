#!/usr/bin/env python3
"""Bootstrap an admin user and API token.

Reads ``BOOTSTRAP_ADMIN_TOKEN`` and ``DATABASE_URL`` from the environment
(or ``.env``). Stores only the SHA-256 hash of the token in PostgreSQL and
prints the plaintext once when a new token row is created.

Usage (from the backend directory, with venv active):

    python -m scripts.bootstrap_admin_token

Optional env:

    BOOTSTRAP_ADMIN_EMAIL   (default: admin@behavioral.local)
    BOOTSTRAP_ADMIN_NAME    (default: Admin)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow running as ``python scripts/bootstrap_admin_token.py`` from backend/.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.auth.security import generate_api_token, hash_api_token
from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services.tokens import (
    create_user_token,
    find_token_by_hash,
    get_or_create_user_by_email,
)


async def bootstrap() -> int:
    settings = get_settings()
    email = __import__("os").environ.get(
        "BOOTSTRAP_ADMIN_EMAIL",
        "admin@behavioral.local",
    )
    display_name = __import__("os").environ.get("BOOTSTRAP_ADMIN_NAME", "Admin")

    plaintext = settings.bootstrap_admin_token.strip()
    generated = False
    if not plaintext:
        plaintext = generate_api_token()
        generated = True

    token_hash = hash_api_token(plaintext)

    async with AsyncSessionLocal() as db:
        user = await get_or_create_user_by_email(
            db,
            email=email,
            display_name=display_name,
        )

        existing = await find_token_by_hash(db, token_hash)
        if existing is not None:
            if existing.revoked_at is not None:
                print(
                    "A revoked token with this hash already exists. "
                    "Set a new BOOTSTRAP_ADMIN_TOKEN or create a token via the API.",
                    file=sys.stderr,
                )
                return 1
            print("Admin token already bootstrapped (hash present in database).")
            print(f"user_id={user.id}")
            print(f"token_id={existing.id}")
            print("Plaintext is not re-displayed for existing tokens.")
            return 0

        row, returned = await create_user_token(
            db,
            user=user,
            name="bootstrap-admin",
            plaintext=plaintext,
        )

    print("Bootstrap admin token created.")
    print(f"user_id={user.id}")
    print(f"user_email={user.email}")
    print(f"token_id={row.id}")
    if generated:
        print(
            "BOOTSTRAP_ADMIN_TOKEN was empty; a secure token was generated.",
            file=sys.stderr,
        )
    print("--- plaintext token (store securely; shown only once) ---")
    print(returned)
    print("---------------------------------------------------------")
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(bootstrap()))


if __name__ == "__main__":
    main()
