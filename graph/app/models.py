import os
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Flag(Base):
    __tablename__ = "flag"
    __table_args__ = (Index("ix_flag__order", "_order"),)
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    box_id = Column(ForeignKey("box.id"), nullable=False)
    _name = Column(String(64))
    _order = Column(Integer)
    box = relationship("Box", back_populates="flag")
    team = relationship("Team", secondary="team_to_flag", back_populates="flag")
    user = relationship("User", secondary="user_to_flag", back_populates="flag")
    hint = relationship("Hint", back_populates="flag")
    penalty = relationship("Penalty", back_populates="flag")


class Box(Base):
    __tablename__ = "box"
    __table_args__ = (Index("ix_box__order", "_order"),)
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    game_level_id = Column(ForeignKey("game_level.id"), nullable=False)
    _name = Column(String(32), nullable=False, unique=True)
    _description = Column(String(1024))
    _order = Column(Integer)
    game_level = relationship("GameLevel", back_populates="box")
    team = relationship("Team", secondary="team_to_box", back_populates="box")
    flag = relationship("Flag", back_populates="box")
    hint = relationship("Hint", back_populates="box")


class GameLevel(Base):
    __tablename__ = "game_level"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _name = Column(String(32))
    _description = Column(String(512))
    box = relationship("Box", back_populates="game_level")
    team = relationship(
        "Team", secondary="team_to_game_level", back_populates="game_level"
    )


class Hint(Base):
    __tablename__ = "hint"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    box_id = Column(ForeignKey("box.id"), nullable=False)
    flag_id = Column(ForeignKey("flag.id"))
    box = relationship("Box", back_populates="hint")
    flag = relationship("Flag", back_populates="hint")
    team = relationship("Team", secondary="team_to_hint", back_populates="hint")


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _handle = Column(String(16), nullable=False, unique=True)
    money = Column(Integer, nullable=False)
    _avatar = Column(String(64))
    _name = Column(String(64))
    _email = Column(String(64))
    _notes = Column(String(512))
    team_id = Column(ForeignKey("team.id"))
    team = relationship("Team", back_populates="user")
    flag = relationship("Flag", secondary="user_to_flag", back_populates="user")
    penalty = relationship("Penalty", back_populates="user")


class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _name = Column(String(24), nullable=False, unique=True)
    money = Column(Integer, nullable=False)
    _motto = Column(String(32))
    _avatar = Column(String(64))
    game_level = relationship(
        "GameLevel", secondary="team_to_game_level", back_populates="team"
    )
    box = relationship("Box", secondary="team_to_box", back_populates="team")
    user = relationship("User", back_populates="team")
    flag = relationship("Flag", secondary="team_to_flag", back_populates="team")
    hint = relationship("Hint", secondary="team_to_hint", back_populates="team")
    penalty = relationship("Penalty", back_populates="team")


class Penalty(Base):
    __tablename__ = "penalty"
    id = Column(Integer, primary_key=True)
    team_id = Column(ForeignKey("team.id", ondelete="CASCADE"))
    flag_id = Column(ForeignKey("flag.id", ondelete="CASCADE"))
    user_id = Column(ForeignKey("user.id"))
    flag = relationship("Flag", back_populates="penalty")
    team = relationship("Team", back_populates="penalty")
    user = relationship("User", back_populates="penalty")


t_team_to_box = Table(
    "team_to_box",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column("box_id", ForeignKey("box.id", ondelete="CASCADE"), nullable=False),
)


t_team_to_game_level = Table(
    "team_to_game_level",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column(
        "game_level_id", ForeignKey("game_level.id", ondelete="CASCADE"), nullable=False
    ),
)


t_team_to_flag = Table(
    "team_to_flag",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column("flag_id", ForeignKey("flag.id", ondelete="CASCADE"), nullable=False),
)


t_user_to_flag = Table(
    "user_to_flag",
    metadata,
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
    Column("flag_id", ForeignKey("flag.id", ondelete="CASCADE"), nullable=False),
)


t_team_to_hint = Table(
    "team_to_hint",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column("hint_id", ForeignKey("hint.id", ondelete="CASCADE"), nullable=False),
)

postgres = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/{os.getenv('POSTGRES_DB')}"
engine = create_engine(postgres)
session = sessionmaker(bind=engine)
