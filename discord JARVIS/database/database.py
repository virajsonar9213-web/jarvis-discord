"""
JARVIS Database Module

Async SQLite database using aiosqlite.
Handles all database operations for the bot.
"""

import aiosqlite
from pathlib import Path
from typing import Optional


class Database:
    """Async database manager for JARVIS."""

    def __init__(self, db_path: str = "data/jarvis.db"):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Connect to the database and initialize schema."""
        # Ensure data directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self._initialize_schema()

    async def _initialize_schema(self) -> None:
        """Initialize database schema from SQL file if needed."""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            schema_sql = schema_path.read_text(encoding="utf-8")

            # Execute schema in a transaction
            await self.conn.executescript(schema_sql)
            await self.conn.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def execute(
        self,
        query: str,
        params: tuple | None = None,
    ) -> aiosqlite.Cursor:
        """Execute a query and return the cursor."""
        if params:
            return await self.conn.execute(query, params)
        return await self.conn.execute(query)

    async def fetchone(
        self,
        query: str,
        params: tuple | None = None,
    ) -> Optional[dict]:
        """Fetch a single row as a dictionary."""
        cursor = await self.execute(query, params)
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    async def fetchall(
        self,
        query: str,
        params: tuple | None = None,
    ) -> list[dict]:
        """Fetch all rows as a list of dictionaries."""
        cursor = await self.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def commit(self) -> None:
        """Commit pending transactions."""
        await self.conn.commit()

    async def get_schema_version(self) -> int:
        """Get the current database schema version."""
        row = await self.fetchone("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        return row["version"] if row else 0

    async def initialize_defaults(self, owner_id: int, owner_name: str, friend_id: int, friend_name: str) -> None:
        """Initialize default data for a new database."""
        # Create users
        await self.execute(
            "INSERT OR IGNORE INTO users (discord_id, username, is_owner) VALUES (?, ?, 1)",
            (owner_id, owner_name),
        )
        await self.execute(
            "INSERT OR IGNORE INTO users (discord_id, username, is_owner) VALUES (?, ?, 0)",
            (friend_id, friend_name),
        )

        # Set default bot settings
        defaults = {
            "gemini_model": "gemini-2.0-flash",
            "response_length": "normal",
            "memory_enabled": "true",
            "notifications_enabled": "true",
        }
        for key, value in defaults.items():
            await self.execute(
                "INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)",
                (key, value),
            )

        await self.commit()
