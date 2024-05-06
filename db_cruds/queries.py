from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from models.all_models import Check, ProductCheck, User

COUNT_TOTAL_AND_REST_QUERY = (
    select(Check,
           func.sum(ProductCheck.price * ProductCheck.quantity).label("total"),
           Check.amount - func.sum(ProductCheck.price * ProductCheck.quantity).label("rest"),
           )
    .join(ProductCheck)
    .group_by(Check.check_id)
)

BASE_CHECK_GET_QUERY = (
    select(
        Check,
        func.concat(User.first_name, " ", User.last_name).label("full_customer_name")
    )
    .join(ProductCheck, ProductCheck.check_id == Check.check_id)
    .join(User, User.user_id == Check.customer_id)
    .options(joinedload(Check.details))
    # .options(contains_eager(Check.details))
    .options(joinedload(Check.customer))

)

BASE_CHECK_GET_LIST_QUERY = (
    select(
        Check,
        func.sum(ProductCheck.price * ProductCheck.quantity).label("total"),
        (Check.amount - func.sum(ProductCheck.price * ProductCheck.quantity)).label("rest"),
        func.concat(User.first_name, " ", User.last_name).label("full_customer_name")
    )
    .join(ProductCheck, ProductCheck.check_id == Check.check_id)
    .join(User, User.user_id == Check.customer_id)
    .options(joinedload(Check.details))
    .group_by(Check.check_id, User.first_name, User.last_name)
)