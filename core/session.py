import re
from contextlib import asynccontextmanager

from asyncpg import exceptions
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette import status

from core.config import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
async_session = sessionmaker(
    bind=engine,class_=AsyncSession, autoflush=False, expire_on_commit=False, autocommit=False
)



@asynccontextmanager
async def run_transaction(session: AsyncSession):
    """
    Begins a new transaction and commits if execution succeeds otherwise rollbacks.
    """
    transaction = await session.begin()
    try:
        yield
        await transaction.commit()
    except IntegrityError as e:
        await transaction.rollback()
        if e.orig.sqlstate == exceptions.UniqueViolationError.sqlstate:
            # see https://github.com/MagicStack/asyncpg/issues/227
            match = re.search(r"DETAIL:[\w\W]*?\(([\w\W]+?)\)=\(([\w\W]+?)\)([\W\w]+)", str(e.orig))
            msg = f"{match.group(1).replace('_', ' ').capitalize()} {match.group(2)}{match.group(3)}"
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
        elif e.orig.sqlstate == exceptions.ForeignKeyViolationError.sqlstate:
            msg = f"Foreign key violation: {e}"
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
        else:
            msg = f"Database validation error: {e}"
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    except DataError as e:
        await transaction.rollback()
        if e.orig.sqlstate == exceptions.InvalidTextRepresentationError.sqlstate:
            msg = f"Invalid input value: {e}"
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
        else:
            msg = f"Database input error: {e}"
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)
    except (HTTPException, RequestValidationError) as e:
        await transaction.rollback()
        raise e
    except Exception as e:
        await transaction.rollback()
        msg = f"Could not process the record: {e}"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg)
