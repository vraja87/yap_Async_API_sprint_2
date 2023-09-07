from redis.asyncio import Redis
from api.v1 import films, genres, persons
from core import config
from core.logger import logger
from db import search_engine, redis
from db.search_engine import SearchBackendFactory, SearchClientInitializer


from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

fast_api_conf = config.FastApiConf()

app = FastAPI(
    title=fast_api_conf.name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    """
    Initialize resources when the FastAPI application starts.

    Connects to Redis and Elasticsearch databases.
    """
    redis_conf = config.RedisConf()
    search_conf = config.SearchConf.read_config()
    logger.info('Startup api service.')
    redis.redis = Redis.from_url(f"redis://{redis_conf.host}:{redis_conf.port}")
    search_engine.search_engine = await SearchBackendFactory.create_backend(search_conf.backend_type,
                                                                            **search_conf.get_init_params())


@app.on_event('shutdown')
async def shutdown():
    """
    Release resources when the FastAPI application stops.

    Closes connections to Redis and Elasticsearch databases.
    """
    search_conf = config.SearchConf.read_config()
    logger.info('Shutdown api service.')
    await redis.redis.close()
    await SearchClientInitializer.close_client(search_conf.backend_type, search_conf.search_conf.client)


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
