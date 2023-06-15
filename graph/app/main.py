from .schema import schema
from . import models
from fastapi import FastAPI
from fastapi import Request, WebSocket, Response
from typing import Union, Optional, Any
from strawberry.asgi import GraphQL
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader


class RTBGraphQL(GraphQL):
    async def get_context(
        self, request: Union[Request, WebSocket], response: Optional[Response] = None
    ) -> Any:
        return {
            "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=models.session()),
        }


graphql_app = RTBGraphQL(schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
