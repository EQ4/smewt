#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from smewtdict import SmewtDict, ValidatingSmewtDict
from smewtexception import SmewtException
from textutils import toUtf8
from smewt.datamodel import BaseObject, MemoryObjectGraph, Equal

# This file contains the 2 base MediaObject types used in Smewt:
#  - Media: is the type used to represent physical files on the hard disk.
#    It always has at least 2 properties: 'filename' and 'sha1'
#  - Metadata: is the type used to represent a media entity independent
#    of its physical location.
#
# Two MediaObject can point to the same AbstractMediaObject, such as the video and
# the subtitle files for an episode will point to the same Episode AbstractMediaObject
#
# The job of a guesser is to map a MediaObject to its corresponding AbstractMediaObject


class Metadata(BaseObject):
    schema = { 'confidence': float,
               'watched': bool
               }

    valid = []


class Media(BaseObject):
    schema = { 'filename': unicode,
               'sha1': unicode,
               'metadata': Metadata,
               'watched': bool, # TODO: or is the one from Metadata sufficient?

               # used by guessers and solvers
               'matches': Metadata
               }

    valid = [ 'filename' ]
    reverseLookup = { 'metadata': 'files',
                      'matches': 'query' }

    types = { 'video': [ 'avi', 'ogm', 'mkv', 'mpg', 'mpeg' ],
              'subtitle': [ 'sub', 'srt' ]
              }


    def ext(self):
        return self.filename.split('.')[-1]

    def type(self):
        ext = self.ext()
        for name, exts in Media.types.items():
            if ext in exts:
                return name
        return 'unknown type'


def foundMetadata(query, result, link = True):
    """Return a graph that contains:
     - the only Media object found in the query graph
     - the result object linked as metadata to the previous media object

    WARNING: this functions messes with the data in the query graph, do not reuse it after
    calling this function.
    """
    # TODO: check that result is valid
    solved = MemoryObjectGraph()

    # remove the stale 'matches' link before adding the media to the resulting graph
    #query.displayGraph()
    media = query.findOne(Media)
    media.matches = []
    media.metadata = []
    m = solved.addObject(media)

    if result is None:
        return solved

    if isinstance(result, list):
        result = [ solved.addObject(n, recurse = Equal.OnLiterals) for n in result ]
    else:
        result = solved.addObject(result, recurse = Equal.OnLiterals)

    #solved.displayGraph()
    if link:
        m.metadata = result

    return solved


def foundAllMetadata(query, result):
    """Return a graph that contains:
     - the only Media object found in the query graph
     - all the Media found in the result graph, linked as metadata to the media object

    WARNING: this functions messes with the data in the query graph, do not reuse it after
    calling this function.
    """
    # TODO: check that result is valid
    solved = MemoryObjectGraph()
    solved += result.findAll(Metadata)

    # remove the stale 'matches' link before adding the media to the resulting graph
    media = query.findOne(Media)
    media.matches = []
    solved.addObject(media).metadata = solved.findAll(Metadata)
    return solved

