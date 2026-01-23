from beanie import init_beanie
from ..models import Hint, User, Level

async def init_database(database):
    await init_beanie(
        database=database,
        document_models=[User],
        allow_index_dropping=False,
        recreate_views=False
    )

    return True