# -*- coding: utf-8 -*-
"""
Created on Jun 19, 2023

@author: dadokkio

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import logging

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from sqlalchemy import Column
from sqlalchemy.types import Unicode, String
from models import dbsession
from models.BaseModels import DatabaseObject
from builtins import str
from uuid import uuid4

### Constants ###
SUCCESS = "/static/images/success.png"
INFO = "/static/images/info.png"
WARNING = "/static/images/warning.png"
ERROR = "/static/images/error.png"


class News(DatabaseObject):

    """Notification definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))

    title = Column(Unicode(256), nullable=False)
    message = Column(Unicode(256), nullable=False)
    icon_url = Column(Unicode(256), nullable=True)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).order_by(News.created.desc()).all()

    @classmethod
    def admin(cls):
        """Returns a list of unique notifications in the database"""
        return dbsession.query(
            cls.created, cls.icon_url, cls.message, cls.title
        ).distinct()

    @classmethod
    def clear(cls):
        """Deletes all objects in the database"""
        return dbsession.query(cls).delete()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return and object based on a uuid"""
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @classmethod
    def _create(cls, title, message, icon=None):
        """Create a notification and save it to the database"""
        logging.debug("Creating news '%s'" % (title))
        icon = icon if icon is not None else INFO
        notification = News(
            title=str(title),
            message=str(message),
            icon_url=urlparse(icon).path,
        )
        return notification

    def to_dict(self):
        """Return public data as dict"""
        return {"title": self.title, "message": self.message, "icon_url": self.icon_url}
