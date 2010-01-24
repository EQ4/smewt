#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2009 Nicolas Wack <wackou@gmail.com>
#
# Smewt is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Smewt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from objectnode import ObjectNode
from abstractdirectedgraph import AbstractDirectedGraph
from memoryobjectnode import MemoryNode, MemoryObjectNode
from objectgraph import ObjectGraph
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectGraph')


class MemoryGraph(AbstractDirectedGraph):
    _objectNodeClass = MemoryNode

    def __init__(self):
        super(MemoryGraph, self).__init__()
        self._nodes = set()

    def clear(self):
        """Delete all objects in this graph."""
        AbstractDirectedGraph.clear(self)
        self._nodes.clear()

    def createNode(self, props = []):
       # FIXME: this might not work anymore (multiple inheritance)
        return self.__class__._objectNodeClass(self, props)

    def deleteNode(self, node):
        raise NotImplementedError


    def nodes(self):
        for node in self._nodes:
            yield node

    def nodesFromClass(self, cls):
        return (node for node in self._nodes if node.isinstance(cls))

    def contains(self, node):
        """Return whether this graph contains the given node (identity)."""
        return node in self._nodes


class MemoryObjectGraph(MemoryGraph, ObjectGraph):
    _objectNodeClass = MemoryObjectNode
