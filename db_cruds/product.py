from sqlalchemy.ext.asyncio import AsyncSession

from db_cruds.base import DBConnectorBase
from models.all_models import ProductCheck
from schemas.product import Product


class DBProductCheckOps(DBConnectorBase[ProductCheck, Product, Product]):
    """ProductCheck class to perform orm operations on products"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, ProductCheck)
