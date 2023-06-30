# -*- coding: utf-8 -*-
"""
Created on Mar 12, 2012

@author: moloch

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


import xml.etree.cElementTree as ET

from uuid import uuid4
from collections import OrderedDict
from sqlalchemy import Column
from sqlalchemy.types import Unicode, String
from sqlalchemy.orm import relationship, backref
from libs.ValidationError import ValidationError
from models import dbsession
from models.BaseModels import DatabaseObject
from builtins import str


class Scenario(DatabaseObject):

    """Scenario definition"""

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    _name = Column(Unicode(32))
    _description = Column(Unicode(512))
    _options = relationship(
        "Option",
        backref=backref("scenario", lazy="select"),
        foreign_keys="Option.scenario_id",
        cascade="all,delete,delete-orphan",
    )

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return sorted(dbsession.query(cls).all())

    @classmethod
    def count(cls):
        return dbsession.query(cls).count()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return and object based on a uuid"""
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @classmethod
    def optionlist(self, scenario_id=None):
        options = self.by_id(scenario_id).options
        optionlist = OrderedDict()
        for option in options:
            optionlist[option.uuid] = option.name
        return optionlist

    @property
    def options(self):
        return self._options

    @property
    def name(self):
        return str(self._name)

    @name.setter
    def name(self, value):
        if len(value) <= 32:
            self._name = value
        else:
            raise ValidationError("Max name length is 32")

    @property
    def description(self):
        if self._description is None:
            return ""
        return self._description

    @description.setter
    def description(self, value):
        if 512 < len(value):
            raise ValidationError("Description cannot be greater than 512 characters")
        self._description = str(value)

    def to_xml(self, parent):
        scenario_elem = ET.SubElement(parent, "scenario")
        ET.SubElement(scenario_elem, "name").text = str(self._name)
        ET.SubElement(scenario_elem, "description").text = str(self._description)
        options_elem = ET.SubElement(scenario_elem, "flags")
        options_elem.set("count", "%s" % str(len(self.options)))
        for option in self.options:
            option.to_xml(options_elem)

    def to_dict(self):
        """Return public data as dict"""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "optionlist": self.optionlist(self.id),
        }

    def __repr__(self):
        return "<Scenario - title: %s>" % (self.title,)

    def __str__(self):
        return self.title

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __hash__(self):
        return hash(self.uuid)
