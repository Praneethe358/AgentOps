from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings

class CheckpointManager:
    _checkpointer: AsyncPostgresSaver = None
    _context_manager = None

    @classmethod
    async def get_checkpointer(cls) -> AsyncPostgresSaver:
        """
        Initializes and creates necessary checkpoint tables in Postgres on first load.
        """
        if cls._checkpointer is None:
            # Initialize async Postgres saver connection pool
            cls._context_manager = AsyncPostgresSaver.from_conn_string(settings.POSTGRES_URI)
            cls._checkpointer = await cls._context_manager.__aenter__()
            
            # Setup creates the required checkpoint tables automatically
            await cls._checkpointer.setup()
            
        return cls._checkpointer
