# Import all the models, so that Base has them before being
# imported by Alembic

from models.base import BaseClass # noqa: F401
from models.all_models import User, Check, ProductCheck  # noqa: F401

