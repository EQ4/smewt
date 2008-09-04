#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@gmail.com>
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

from smewt.mediaobject import Metadata

def parseEpisodeList(string):
    # blah
    return []


class Serie(Metadata):

    typename = 'Serie'

    schema = { 'title': unicode,
               'numberSeasons': int,
               'episodeList': list
               }

    unique = [ 'title' ]

    converters = { 'episodeList': parseEpisodeList }



    def __init__(self):
        Metadata.__init__(self)

    @staticmethod
    def fromDict(d):
        result = SerieObject()
        Metadata.readFromDict(result, headers, row)
        return result

    @staticmethod
    def fromRow(headers, row):
        result = SerieObject()
        Metadata.readFromRow(result, headers, row)
        return result


class Episode(Metadata):

    typename = 'Episode'

    schema = { 'serie': unicode,
               'season': int,
               'episodeNumber': int,
               'title': unicode
               }

    order = [ 'serie', 'season', 'episodeNumber',  'title' ]

    unique = [ 'serie', 'season', 'episodeNumber' ]

    converters = {}

    def __init__(self, copy = None):
        Metadata.__init__(self)
        if copy:
            self.readFromDict(copy.toDict())

    @staticmethod
    def fromDict(d):
        result = Episode()
        Metadata.readFromDict(result, d)
        return result

    @staticmethod
    def fromRow(headers, row):
        result = EpisodeObject()
        Metadata.readFromRow(result, headers, row)
        return result