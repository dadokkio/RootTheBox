import strawberry
from . import models
from sqlalchemy import select
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper

strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()


@strawberry_sqlalchemy_mapper.type(models.User)
class User:
    __exclude__ = ["password"]


@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        with models.session() as session:
            return session.scalars(select(models.User)).all()


strawberry_sqlalchemy_mapper.finalize()
# only needed if you have polymorphic types
additional_types = list(strawberry_sqlalchemy_mapper.mapped_types.values())
schema = strawberry.Schema(query=Query)
