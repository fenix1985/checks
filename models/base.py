from sqlalchemy.orm import declared_attr, DeclarativeBase


class BaseClass(DeclarativeBase):

    @declared_attr
    def __tablename__(cls) -> str:

        return cls.__name__.lower()

    @classmethod
    def pk(cls):
        """
        Get primary key from sqlalchemy mapper object

        :param mapper: sqlalchemy mapper object
        :return: primary key column
        """
        return cls.__mapper__.primary_key[0]
