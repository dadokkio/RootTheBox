import strawberry
from . import models
from datetime import datetime
from typing import Optional, Sequence, Union
from sqlalchemy import select, text, desc, func
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper

# SVG and JPG rendering
import cairosvg
from PIL import Image
from io import BytesIO
from numpy import asarray
from pathlib import Path


strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()


@strawberry_sqlalchemy_mapper.type(models.Scenario)
class Scenario:
    pass


@strawberry_sqlalchemy_mapper.type(models.Option)
class Option:
    __exclude__ = ["next_scenario_id"]


@strawberry_sqlalchemy_mapper.type(models.User)
class User:
    pass


@strawberry_sqlalchemy_mapper.type(models.Team)
class Team:
    __exclude__ = ["flag", "box", "hint", "game_level", "penalty"]


@strawberry_sqlalchemy_mapper.type(models.News)
class News:
    pass


@strawberry.input
class NoteFilter:
    """filters by serial"""

    note: str


@strawberry.type
class Scoreboard:
    Name: str
    Score: int
    Flags: int


@strawberry.type
class ScoreboardTimestamped:
    """scoreboard"""

    records: Sequence[Scoreboard]
    timestamp: str


@strawberry.type
class TeamTimestamped:
    """scoreboard"""

    records: Sequence[Team]
    timestamp: str


@strawberry.type
class NewsTimestamped:
    records: Sequence[News]
    timestamp: str


@strawberry.type
class Stats:
    Name: str
    Total: int


@strawberry.type
class StatsTimestamped:
    team_hints: Sequence[Stats]
    team_errors: Sequence[Stats]
    flag_hints: Sequence[Stats]
    flag_errors: Sequence[Stats]
    timestamp: str


@strawberry.type
class ScenarioTimestamped:
    scenario: Optional[Scenario]
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
    img = img.resize((140, 70))
    gray_img = img.quantize(4, dither=Image.Dither.NONE)
    ret_string = ""
    ret_tmp = ""
    block = 1
    for line in asarray(gray_img):
        for col in line:
            ret_tmp += bin(col).replace("0b", "").zfill(2)
            if block % 14 == 0:
                ret_string += hex(int(ret_tmp, 2)).replace("0x", "").zfill(7)
                ret_tmp = ""
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
    def scoreboard(self) -> ScoreboardTimestamped:
        with models.session() as session:
            records = (
                session.query(
                    models.Team._name.label("Name"),
                    models.Team.money.label("Score"),
                    func.count(models.Flag.id).label("Flags"),
                )
                .select_from(models.Team)
                .join(models.Team.flag)
                .group_by(models.Team.id)
                .order_by(desc(models.Team.money))
            )
            return ScoreboardTimestamped(
                records=[
                    Scoreboard(Name=record.Name, Score=record.Score, Flags=record.Flags)
                    for record in records.all()
                ],
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )

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
    def scenario(
        self, uuid: str | None = None, option_uuid: str | None = None
    ) -> ScenarioTimestamped:
        with models.session() as session:
            scenario = None
            if uuid:
                scenario = session.scalars(
                    select(models.Scenario).where(models.Scenario.uuid == uuid)
                ).first()
            elif option_uuid:
                if option := session.scalars(
                    select(models.Option).where(models.Option.uuid == option_uuid)
                ).first():
                    scenario = session.scalars(
                        select(models.Scenario).filter(
                            models.Scenario.id == option.next_scenario_id
                        )
                    ).first()
            return ScenarioTimestamped(
                scenario=scenario,
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

    @strawberry.field
    def stats() -> StatsTimestamped:
        with models.session() as session:
            team_hints = [
                Stats(Name=x[0], Total=x[1])
                for x in session.query(
                    models.Team._name, func.count(models.Hint.id).label("total")
                )
                .select_from(models.Team)
                .join(models.Team.hint)
                .group_by(models.Team)
                .order_by(text("total DESC"))
                .limit(5)
            ]

            team_errors = [
                Stats(Name=x[0], Total=x[1])
                for x in session.query(
                    models.Team._name, func.count(models.Penalty.id).label("total")
                )
                .select_from(models.Team)
                .join(models.Team.penalty)
                .group_by(models.Team)
                .order_by(text("total DESC"))
                .limit(5)
            ]

            flag_hints = [
                Stats(Name=x[0], Total=x[1])
                for x in session.query(
                    func.concat(models.Flag.box_id, ".", models.Flag.id),
                    func.count(models.Hint.id).label("total"),
                )
                .select_from(models.Flag)
                .join(models.Flag.hint)
                .group_by(models.Flag)
                .order_by(text("total DESC"))
                .limit(5)
            ]

            flag_errors = [
                Stats(Name=x[0], Total=x[1])
                for x in session.query(
                    func.concat(models.Flag.box_id, ".", models.Flag.id),
                    func.count(models.Penalty.id).label("total"),
                )
                .select_from(models.Flag)
                .join(models.Flag.penalty)
                .group_by(models.Flag)
                .order_by(text("total DESC"))
                .limit(5)
            ]

            return StatsTimestamped(
                team_hints=team_hints,
                team_errors=team_errors,
                flag_hints=flag_hints,
                flag_errors=flag_errors,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )


strawberry_sqlalchemy_mapper.finalize()
# only needed if you have polymorphic types
additional_types = list(strawberry_sqlalchemy_mapper.mapped_types.values())
schema = strawberry.Schema(query=Query)
