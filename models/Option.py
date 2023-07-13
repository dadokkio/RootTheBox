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
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, String
from models import dbsession
from models.Scenario import Scenario
from models.BaseModels import DatabaseObject
from libs.ValidationError import ValidationError
from builtins import str


class Option(DatabaseObject):

    """
    Option that can be selected by players and what not.
    """

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    scenario_id = Column(
        Integer, ForeignKey("scenario.id", ondelete="SET NULL"), nullable=True
    )
    next_scenario_id = Column(
        Integer, ForeignKey("scenario.id", ondelete="SET NULL"), nullable=True
    )

    _name = Column(Unicode(32), nullable=True)
    _description = Column(Unicode(512), nullable=False)
    _order = Column(Integer, nullable=True, index=True)

    @classmethod
    def all(cls):
        """Returns a list of all objects in the database"""
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        """Returns a the object with id of _id"""
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_name(cls, name):
        """Returns a the object with name of _name"""
        return dbsession.query(cls).filter_by(_name=str(name)).first()

    @classmethod
    def by_uuid(cls, _uuid):
        """Return and object based on a uuid"""
        return dbsession.query(cls).filter_by(uuid=str(_uuid)).first()

    @property
    def name(self):
        if self._name and len(self._name) > 0:
            return self._name
        else:
            return "Question %d" % self.order

    @name.setter
    def name(self, value):
        if not len(value) <= 32:
            raise ValidationError(
                "Option name must be less than 32 characters: %s" % value
            )
        self._name = str(value)

    @property
    def order(self):
        if not self._order:
            self._order = self.scenario.options.index(self) + 1
        return self._order

    @order.setter
    def order(self, value):
        if value:
            self._order = int(value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = str(value)[:512]

    @property
    def scenario(self):
        return Scenario.by_id(self.scenario_id)

    @property
    def next_scenario(self):
        if self.next_scenario_id:
            return Scenario.by_id(self.next_scenario_id)
        return None

    def to_xml(self, parent):
        """Write attributes to XML doc"""
        option_elem = ET.SubElement(parent, "option")
        option_elem.set("type", self._type)
        ET.SubElement(option_elem, "name").text = self._name
        ET.SubElement(option_elem, "description").text = self.description

    def to_dict(self):
        """Returns public data as a dict"""
        scenario = Scenario.by_id(self.scenario_id)
        if self.next_scenario:
            next_scenario = Scenario.by_id(self.next_scenario_id).uuid
        else:
            next_scenario = ""
        return {
            "name": self.name,
            "uuid": self.uuid,
            "description": self.description,
            "order": self.order,
            "scenario": scenario.uuid,
            "next_scenario": next_scenario.uuid,
        }

    def __repr__(self):
        return "<Option - name:%s>" % (self.name,)

    def __str__(self):
        return self.name

    def __cmp__(self, other):
        """Compare based on the order"""
        this, that = self.order, other.order
        if this > that:
            return 1
        elif this == that:
            return 0
        else:
            return -1

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
