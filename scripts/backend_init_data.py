import asyncio
import datetime
import json
import logging
from typing import Any, Dict, Union

import aiofiles
from psycopg2 import errors
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.session import async_session
from models.all_models import Product


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def read_json(file_name: str) -> Union[list, dict]:
    """
    Read json file.

    :param file_name: name of file
    :return: The file json content
    """
    try:
        async with aiofiles.open(file_name) as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        logger.warning(f"{file_name} does not exist: skipping!")
        return []

async def commit_rows(db: AsyncSession, db_row, record):
    """
    Commit into database.

    :param db: database session
    :param db_row: database model to commit
    :param record: model item
    """
    try:
        await db.commit()
        await db.refresh(db_row)
    except IntegrityError as e:
        await db.rollback()
        if isinstance(e.orig, errors.UniqueViolation):
            raise RuntimeError(f"The record violates unique constraint: {record}")
        elif isinstance(e.orig, errors.ForeignKeyViolation):
            raise RuntimeError(f"The record violates Foreign Key constraint: {record}")
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"Couldn't add the record {record} to the DB: {e}")


async def insert_from_json(db: AsyncSession, file_name: str, object_class):
    """
    Insert `object_class` record values from json file.

    :param db: database session
    :param file_name: name of file
    :param object_class: database model's class
    """
    data_to_insert = await read_json(file_name)
    for record in data_to_insert:
        db_row = object_class(**record)
        db.add(db_row)
        await commit_rows(db, db_row, record)


async def insert_products_records(db: AsyncSession):
    """
    Insert team role records from data file.

    :param db: database session
    """
    await insert_from_json(db, f"{settings.DATA_DIRECTORY_PATH}/products.json", Product)


async def main():
    """
    Execute database initialization
    """
    async with async_session() as db:
        await insert_products_records(db)



if settings.INITIALIZE_DB:
    asyncio.run(main())
else:
    logger.info("Skipping the database initialization step")
