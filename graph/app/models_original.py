import os
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _category = Column(String(64), nullable=False, unique=True)
    created = Column(DateTime)
    _description = Column(String(1024))

    box = relationship("Box", back_populates="category")


class Corporation(Base):
    __tablename__ = "corporation"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _name = Column(String(32), nullable=False, unique=True)
    created = Column(DateTime)
    _description = Column(String(512))

    box = relationship("Box", back_populates="corporation")


class GameLevel(Base):
    __tablename__ = "game_level"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _number = Column(Integer, nullable=False, unique=True)
    _buyout = Column(Integer, nullable=False)
    _type = Column(String(16), nullable=False)
    _reward = Column(Integer, nullable=False)
    created = Column(DateTime)
    next_level_id = Column(ForeignKey("game_level.id"))
    _name = Column(String(32))
    _description = Column(String(512))

    next_level = relationship(
        "GameLevel", remote_side=[id], back_populates="next_level_reverse"
    )
    next_level_reverse = relationship(
        "GameLevel", remote_side=[next_level_id], back_populates="next_level"
    )
    team = relationship(
        "Team", secondary="team_to_game_level", back_populates="game_level"
    )
    box = relationship("Box", back_populates="game_level")


class MarketItem(Base):
    __tablename__ = "market_item"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    name = Column(String(64), nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String(256), nullable=False)
    created = Column(DateTime)
    description = Column(String(1024))

    team = relationship("Team", secondary="team_to_item", back_populates="item")


class RegistrationToken(Base):
    __tablename__ = "registration_token"

    id = Column(Integer, primary_key=True)
    value = Column(String(6), nullable=False, unique=True)
    used = Column(Boolean, nullable=False)
    created = Column(DateTime)


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _name = Column(String(24), nullable=False, unique=True)
    money = Column(Integer, nullable=False)
    created = Column(DateTime)
    _motto = Column(String(32))
    _avatar = Column(String(64))
    _notes = Column(String(512))
    code = Column(String(16), unique=True)

    game_level = relationship(
        "GameLevel", secondary="team_to_game_level", back_populates="team"
    )
    item = relationship("MarketItem", secondary="team_to_item", back_populates="team")
    box = relationship("Box", secondary="team_to_box", back_populates="team")
    file_upload = relationship("FileUpload", back_populates="team")
    game_history = relationship("GameHistory", back_populates="team")
    paste_bin = relationship("PasteBin", back_populates="team")
    user = relationship("User", back_populates="team")
    flag = relationship("Flag", secondary="team_to_flag", back_populates="team")
    source_code = relationship(
        "SourceCode", secondary="team_to_source_code", back_populates="team"
    )
    hint = relationship("Hint", secondary="team_to_hint", back_populates="team")
    penalty = relationship("Penalty", back_populates="team")


class Theme(Base):
    __tablename__ = "theme"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _name = Column(String(64), nullable=False, unique=True)
    created = Column(DateTime)

    theme_file = relationship("ThemeFile", back_populates="theme")
    user = relationship("User", back_populates="theme")


class Box(Base):
    __tablename__ = "box"
    __table_args__ = (Index("ix_box__order", "_order"),)

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    corporation_id = Column(ForeignKey("corporation.id"), nullable=False)
    _name = Column(String(32), nullable=False, unique=True)
    game_level_id = Column(ForeignKey("game_level.id"), nullable=False)
    _locked = Column(Boolean, nullable=False)
    garbage = Column(String(32), nullable=False, unique=True)
    created = Column(DateTime)
    category_id = Column(ForeignKey("category.id"))
    _operating_system = Column(String(16))
    _description = Column(String(1024))
    _capture_message = Column(String(1024))
    _difficulty = Column(String(16))
    _avatar = Column(String(64))
    _value = Column(Integer)
    _order = Column(Integer)
    flag_submission_type = Column(String(21))

    category = relationship("Category", back_populates="box")
    corporation = relationship("Corporation", back_populates="box")
    game_level = relationship("GameLevel", back_populates="box")
    team = relationship("Team", secondary="team_to_box", back_populates="box")
    flag = relationship("Flag", back_populates="box")
    ip_address = relationship("IpAddress", back_populates="box")
    source_code = relationship("SourceCode", back_populates="box")
    hint = relationship("Hint", back_populates="box")


class FileUpload(Base):
    __tablename__ = "file_upload"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    team_id = Column(ForeignKey("team.id"), nullable=False)
    byte_size = Column(Integer, nullable=False)
    _description = Column(String(1024), nullable=False)
    _file_name = Column(String(64), nullable=False)
    created = Column(DateTime)

    team = relationship("Team", back_populates="file_upload")


class GameHistory(Base):
    __tablename__ = "game_history"

    id = Column(Integer, primary_key=True)
    team_id = Column(ForeignKey("team.id"), nullable=False)
    _type = Column(String(20), nullable=False)
    _value = Column(Integer, nullable=False)
    created = Column(DateTime)

    team = relationship("Team", back_populates="game_history")


class PasteBin(Base):
    __tablename__ = "paste_bin"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    team_id = Column(ForeignKey("team.id"), nullable=False)
    _name = Column(String(32), nullable=False)
    _contents = Column(String(4096), nullable=False)
    created = Column(DateTime)

    team = relationship("Team", back_populates="paste_bin")


t_team_to_game_level = Table(
    "team_to_game_level",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column(
        "game_level_id", ForeignKey("game_level.id", ondelete="CASCADE"), nullable=False
    ),
)


t_team_to_item = Table(
    "team_to_item",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column("item_id", ForeignKey("market_item.id", ondelete="CASCADE"), nullable=False),
)


class ThemeFile(Base):
    __tablename__ = "theme_file"

    id = Column(Integer, primary_key=True)
    theme_id = Column(ForeignKey("theme.id"), nullable=False)
    _file_name = Column(String(64), nullable=False)
    created = Column(DateTime)

    theme = relationship("Theme", back_populates="theme_file")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    _locked = Column(Boolean, nullable=False)
    _handle = Column(String(16), nullable=False, unique=True)
    money = Column(Integer, nullable=False)
    theme_id = Column(ForeignKey("theme.id"), nullable=False)
    algorithm = Column(String(8), nullable=False)
    created = Column(DateTime)
    team_id = Column(ForeignKey("team.id"))
    _avatar = Column(String(64))
    last_login = Column(DateTime)
    logins = Column(Integer)
    _name = Column(String(64))
    _email = Column(String(64))
    password = Column(String(64))
    bank_password = Column(String(128))
    _notes = Column(String(512))
    _expire = Column(DateTime)

    team = relationship("Team", back_populates="user")
    theme = relationship("Theme", back_populates="user")
    email_token = relationship("EmailToken", back_populates="user")
    flag = relationship("Flag", secondary="user_to_flag", back_populates="user")
    notification = relationship("Notification", back_populates="user")
    password_token = relationship("PasswordToken", back_populates="user")
    permission = relationship("Permission", back_populates="user")
    swat = relationship(
        "Swat", foreign_keys="[Swat.target_id]", back_populates="target"
    )
    swat_ = relationship("Swat", foreign_keys="[Swat.user_id]", back_populates="user")
    wall_of_sheep = relationship(
        "WallOfSheep", foreign_keys="[WallOfSheep.cracker_id]", back_populates="cracker"
    )
    wall_of_sheep_ = relationship(
        "WallOfSheep", foreign_keys="[WallOfSheep.victim_id]", back_populates="victim"
    )
    penalty = relationship("Penalty", back_populates="user")


class EmailToken(Base):
    __tablename__ = "email_token"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(64), nullable=False, unique=True)
    valid = Column(Boolean, nullable=False)
    created = Column(DateTime)

    user = relationship("User", back_populates="email_token")


class Flag(Base):
    __tablename__ = "flag"
    __table_args__ = (Index("ix_flag__order", "_order"),)

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    box_id = Column(ForeignKey("box.id"), nullable=False)
    _token = Column(String(256), nullable=False)
    _description = Column(String(1024), nullable=False)
    _value = Column(Integer, nullable=False)
    _locked = Column(Boolean, nullable=False)
    created = Column(DateTime)
    lock_id = Column(ForeignKey("flag.id", ondelete="SET NULL"))
    _name = Column(String(64))
    _capture_message = Column(String(512))
    _case_sensitive = Column(Integer)
    _original_value = Column(Integer)
    _order = Column(Integer)
    _type = Column(String(16))

    box = relationship("Box", back_populates="flag")
    lock = relationship("Flag", remote_side=[id], back_populates="lock_reverse")
    lock_reverse = relationship("Flag", remote_side=[lock_id], back_populates="lock")
    team = relationship("Team", secondary="team_to_flag", back_populates="flag")
    user = relationship("User", secondary="user_to_flag", back_populates="flag")
    flag_attachment = relationship("FlagAttachment", back_populates="flag")
    flag_choice = relationship("FlagChoice", back_populates="flag")
    hint = relationship("Hint", back_populates="flag")
    penalty = relationship("Penalty", back_populates="flag")


class IpAddress(Base):
    __tablename__ = "ip_address"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    box_id = Column(ForeignKey("box.id"), nullable=False)
    created = Column(DateTime)
    _address = Column(String(80))
    visible = Column(Boolean)

    box = relationship("Box", back_populates="ip_address")


class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False)
    message = Column(String(256), nullable=False)
    created = Column(DateTime)
    user_id = Column(ForeignKey("user.id"))
    viewed = Column(Boolean)
    icon_url = Column(String(256))

    user = relationship("User", back_populates="notification")


class PasswordToken(Base):
    __tablename__ = "password_token"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    value = Column(String(64), nullable=False, unique=True)
    used = Column(Boolean, nullable=False)
    created = Column(DateTime)

    user = relationship("User", back_populates="password_token")


class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(64), nullable=False)
    created = Column(DateTime)

    user = relationship("User", back_populates="permission")


class SourceCode(Base):
    __tablename__ = "source_code"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    box_id = Column(ForeignKey("box.id", ondelete="CASCADE"), nullable=False)
    _price = Column(Integer, nullable=False)
    _description = Column(String(1024), nullable=False)
    _file_name = Column(String(64), nullable=False)
    created = Column(DateTime)
    checksum = Column(String(40))

    box = relationship("Box", back_populates="source_code")
    team = relationship(
        "Team", secondary="team_to_source_code", back_populates="source_code"
    )


class Swat(Base):
    __tablename__ = "swat"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    user_id = Column(ForeignKey("user.id"), nullable=False)
    target_id = Column(ForeignKey("user.id"), nullable=False)
    paid = Column(Integer, nullable=False)
    created = Column(DateTime)
    accepted = Column(Boolean)
    completed = Column(Boolean)

    target = relationship("User", foreign_keys=[target_id], back_populates="swat")
    user = relationship("User", foreign_keys=[user_id], back_populates="swat_")


t_team_to_box = Table(
    "team_to_box",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column("box_id", ForeignKey("box.id", ondelete="CASCADE"), nullable=False),
)


class WallOfSheep(Base):
    __tablename__ = "wall_of_sheep"

    id = Column(Integer, primary_key=True)
    preimage = Column(String(32), nullable=False)
    value = Column(Integer, nullable=False)
    victim_id = Column(ForeignKey("user.id"), nullable=False)
    cracker_id = Column(ForeignKey("user.id"), nullable=False)
    created = Column(DateTime)

    cracker = relationship(
        "User", foreign_keys=[cracker_id], back_populates="wall_of_sheep"
    )
    victim = relationship(
        "User", foreign_keys=[victim_id], back_populates="wall_of_sheep_"
    )


class FlagAttachment(Base):
    __tablename__ = "flag_attachment"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    flag_id = Column(ForeignKey("flag.id"), nullable=False)
    _file_name = Column(String(64), nullable=False)
    created = Column(DateTime)

    flag = relationship("Flag", back_populates="flag_attachment")


class FlagChoice(Base):
    __tablename__ = "flag_choice"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    flag_id = Column(ForeignKey("flag.id"), nullable=False)
    created = Column(DateTime)
    _choice = Column(String(256))

    flag = relationship("Flag", back_populates="flag_choice")


class Hint(Base):
    __tablename__ = "hint"

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    box_id = Column(ForeignKey("box.id"), nullable=False)
    _price = Column(Integer, nullable=False)
    _description = Column(String(1024), nullable=False)
    created = Column(DateTime)
    flag_id = Column(ForeignKey("flag.id"))

    box = relationship("Box", back_populates="hint")
    flag = relationship("Flag", back_populates="hint")
    team = relationship("Team", secondary="team_to_hint", back_populates="hint")


class Penalty(Base):
    __tablename__ = "penalty"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    team_id = Column(ForeignKey("team.id", ondelete="CASCADE"))
    flag_id = Column(ForeignKey("flag.id", ondelete="CASCADE"))
    user_id = Column(ForeignKey("user.id"))
    _token = Column(String(256))

    flag = relationship("Flag", back_populates="penalty")
    team = relationship("Team", back_populates="penalty")
    user = relationship("User", back_populates="penalty")


t_team_to_flag = Table(
    "team_to_flag",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column("flag_id", ForeignKey("flag.id", ondelete="CASCADE"), nullable=False),
)


t_team_to_source_code = Table(
    "team_to_source_code",
    metadata,
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), nullable=False),
    Column(
        "source_code_id",
        ForeignKey("source_code.id", ondelete="CASCADE"),
        nullable=False,
    ),
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
