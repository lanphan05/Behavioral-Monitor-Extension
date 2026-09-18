"""initial_schema

Revision ID: a9f2b2a9c6c2
Revises:
Create Date: 2026-09-17 23:00:00.000000

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a9f2b2a9c6c2"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "model_registry",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("artifact_path", sa.Text(), nullable=False),
        sa.Column("metrics_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_model_registry_name"),
        "model_registry",
        ["name"],
        unique=False,
    )

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "api_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_api_tokens_token_hash"),
        "api_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_api_tokens_user_id"),
        "api_tokens",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)

    op.create_table(
        "behavior_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("client_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=128), nullable=False),
        sa.Column(
            "payload_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_behavior_events_session_id_client_ts",
        "behavior_events",
        ["session_id", "client_ts"],
        unique=False,
    )
    op.create_index(
        op.f("ix_behavior_events_type"),
        "behavior_events",
        ["type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_behavior_events_user_id"),
        "behavior_events",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "feature_windows",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "features_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_feature_windows_session_id"),
        "feature_windows",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_feature_windows_user_id"),
        "feature_windows",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "scores",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("feature_window_id", sa.UUID(), nullable=True),
        sa.Column("model_id", sa.UUID(), nullable=True),
        sa.Column("score_value", sa.Float(), nullable=False),
        sa.Column(
            "scored_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["feature_window_id"],
            ["feature_windows.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["model_id"], ["model_registry.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_scores_feature_window_id"),
        "scores",
        ["feature_window_id"],
        unique=False,
    )
    op.create_index(op.f("ix_scores_model_id"), "scores", ["model_id"], unique=False)
    op.create_index(op.f("ix_scores_session_id"), "scores", ["session_id"], unique=False)
    op.create_index(op.f("ix_scores_user_id"), "scores", ["user_id"], unique=False)

    op.create_table(
        "peaks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("score_id", sa.UUID(), nullable=True),
        sa.Column("peaked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("peak_score", sa.Float(), nullable=False),
        sa.Column("code_context", sa.Text(), nullable=True),
        sa.Column("context_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["score_id"], ["scores.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_peaks_score_id"), "peaks", ["score_id"], unique=False)
    op.create_index(op.f("ix_peaks_session_id"), "peaks", ["session_id"], unique=False)
    op.create_index(op.f("ix_peaks_user_id"), "peaks", ["user_id"], unique=False)

    op.create_table(
        "labels",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("score_id", sa.UUID(), nullable=True),
        sa.Column("peak_id", sa.UUID(), nullable=True),
        sa.Column("label_value", sa.String(length=128), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("meta_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["peak_id"], ["peaks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["score_id"], ["scores.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_labels_label_value"),
        "labels",
        ["label_value"],
        unique=False,
    )
    op.create_index(op.f("ix_labels_peak_id"), "labels", ["peak_id"], unique=False)
    op.create_index(op.f("ix_labels_score_id"), "labels", ["score_id"], unique=False)
    op.create_index(op.f("ix_labels_session_id"), "labels", ["session_id"], unique=False)
    op.create_index(op.f("ix_labels_user_id"), "labels", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_labels_user_id"), table_name="labels")
    op.drop_index(op.f("ix_labels_session_id"), table_name="labels")
    op.drop_index(op.f("ix_labels_score_id"), table_name="labels")
    op.drop_index(op.f("ix_labels_peak_id"), table_name="labels")
    op.drop_index(op.f("ix_labels_label_value"), table_name="labels")
    op.drop_table("labels")

    op.drop_index(op.f("ix_peaks_user_id"), table_name="peaks")
    op.drop_index(op.f("ix_peaks_session_id"), table_name="peaks")
    op.drop_index(op.f("ix_peaks_score_id"), table_name="peaks")
    op.drop_table("peaks")

    op.drop_index(op.f("ix_scores_user_id"), table_name="scores")
    op.drop_index(op.f("ix_scores_session_id"), table_name="scores")
    op.drop_index(op.f("ix_scores_model_id"), table_name="scores")
    op.drop_index(op.f("ix_scores_feature_window_id"), table_name="scores")
    op.drop_table("scores")

    op.drop_index(op.f("ix_feature_windows_user_id"), table_name="feature_windows")
    op.drop_index(op.f("ix_feature_windows_session_id"), table_name="feature_windows")
    op.drop_table("feature_windows")

    op.drop_index(op.f("ix_behavior_events_user_id"), table_name="behavior_events")
    op.drop_index(op.f("ix_behavior_events_type"), table_name="behavior_events")
    op.drop_index("ix_behavior_events_session_id_client_ts", table_name="behavior_events")
    op.drop_table("behavior_events")

    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")

    op.drop_index(op.f("ix_api_tokens_user_id"), table_name="api_tokens")
    op.drop_index(op.f("ix_api_tokens_token_hash"), table_name="api_tokens")
    op.drop_table("api_tokens")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_model_registry_name"), table_name="model_registry")
    op.drop_table("model_registry")
