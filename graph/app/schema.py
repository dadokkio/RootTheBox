import strawberry
from . import models
from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import select, text, desc
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper

# SVG and JPG rendering
import cairosvg
from PIL import Image
from io import BytesIO
from numpy import asarray
from pathlib import Path


strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()


@strawberry_sqlalchemy_mapper.type(models.User)
class User:
    __exclude__ = ["_password"]


@strawberry_sqlalchemy_mapper.type(models.Team)
class Team:
    pass


@strawberry_sqlalchemy_mapper.type(models.Hint)
class Hint:
    pass


@strawberry_sqlalchemy_mapper.type(models.News)
class News:
    pass


@strawberry.input
class NoteFilter:
    note: str


@strawberry.type
class TeamTimestamped:
    records: Sequence[Team]
    timestamp: str


@strawberry.type
class HintsTimestamped:
    records: Sequence[Hint]
    timestamp: str


@strawberry.type
class UsersTimestamped:
    records: Sequence[User]
    timestamp: str


@strawberry.type
class NewsTimestamped:
    records: Sequence[News]
    timestamp: str


def convert_photo(path: Optional[str], team: bool = True) -> str:
    if path:
        path = f"/avatars/{path}"
    else:
        path = "/avatars/default_team.jpg" if team else "/avatars/default_user.jpg"

    if Path(path).suffix.lower() == ".svg":
        out = BytesIO()
        cairosvg.svg2png(url=path, write_to=out)
        img = Image.open(out)
    else:
        img = Image.open(path)
    img = img.convert("RGB")
    img = img.resize((112, 56))
    gray_img = img.quantize(4, dither=Image.Dither.NONE)
    ret_string = ""
    ret_tmp = ""
    block = 1
    for line in asarray(gray_img):
        for col in line:
            ret_tmp += bin(col).replace("0b", "").zfill(2)
            if block == 14:
                ret_string += hex(int(ret_tmp, 2)).replace("0x", "")
                ret_string += "|"
                ret_tmp = ""
                block = 0
            block += 1
    return ret_string


@strawberry.type
class Query:
    @strawberry.field
    def me(self, where: NoteFilter) -> Optional[User]:
        with models.session() as session:
            me = session.scalars(
                select(models.User).where(models.User._notes == where.note)
            ).first()
            if me:
                me._avatar = convert_photo(me._avatar, team=False)  # type: ignore
                return me
            return me

    @strawberry.field
    def myteam(self, where: NoteFilter) -> Optional[Team]:
        with models.session() as session:
            team = session.scalars(
                select(models.Team)
                .join(models.User)
                .where(models.User._notes == where.note)
            ).first()
            if team:
                team._avatar = convert_photo(team._avatar, team=True)  # type: ignore
                return team
            return team

    @strawberry.field
    def teams(self, order_by: str, limit: int, offset: int = 0) -> TeamTimestamped:
        with models.session() as session:
            return TeamTimestamped(
                records=session.scalars(
                    select(models.Team)
                    .limit(limit)
                    .offset(offset)
                    .order_by(desc(text(order_by)))
                ).all(),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )

    @strawberry.field
    def hints(self, order_by: str, limit: int, offset: int = 0) -> HintsTimestamped:
        with models.session() as session:
            return HintsTimestamped(
                records=session.scalars(
                    select(models.Hint)
                    .limit(limit)
                    .offset(offset)
                    .order_by(desc(text(order_by)))
                ).all(),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )

    @strawberry.field
    def users(self, order_by: str, limit: int, offset: int = 0) -> UsersTimestamped:
        with models.session() as session:
            return UsersTimestamped(
                records=session.scalars(
                    select(models.User)
                    .limit(limit)
                    .offset(offset)
                    .order_by(desc(text(order_by)))
                ).all(),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )

    @strawberry.field
    def news(self, order_by: str, limit: int, offset: int = 0) -> NewsTimestamped:
        with models.session() as session:
            return NewsTimestamped(
                records=session.scalars(
                    select(models.News)
                    .limit(limit)
                    .offset(offset)
                    .order_by(desc(text(order_by)))
                ).all(),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )


strawberry_sqlalchemy_mapper.finalize()
# only needed if you have polymorphic types
additional_types = list(strawberry_sqlalchemy_mapper.mapped_types.values())
schema = strawberry.Schema(query=Query)
