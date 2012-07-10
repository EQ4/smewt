#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@smewt.com>
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

from guessit.patterns import video_exts
from smewt.base import Metadata, utils, SmewtUrl

class Series(Metadata):

    #typename = 'Series'

    schema = { 'title': unicode,
               'numberSeasons': int,
               #'episodeList': list
               }

    valid = [ 'title' ]
    unique = [ 'title' ]

    #converters = { 'episodeList': lambda x:x } #parseEpisodeList }

    def niceString(self):
        return 'series %s' % self.title


class Episode(Metadata):

    #typename = 'Episode'

    schema = { 'series': Series,
               'season': int,
               'episodeNumber': int,
               'title': unicode
               }

    valid = [ 'series', 'season', 'episodeNumber' ]
    reverse_lookup = { 'series': 'episodes' }
    #order = [ 'series', 'season', 'episodeNumber',  'title' ]

    unique = [ 'series', 'season', 'episodeNumber' ]

    converters = {}

    def niceString(self):
        return 'episode %dx%02d of %s' % (self.season, self.episodeNumber, self.series.niceString())

    @staticmethod
    def isValidEpisode(filename):
        extPatterns = [ '*.' + ext for ext in video_exts ]
        return utils.matchFile(filename, extPatterns) #and getsize(filename) < 600 * 1024 * 1024

    def playUrl(self):
        # FIXME: we should do sth smarter here, such as ask the user, or at least warn him
        files = self.get('files')
        if not files:
            # dirty fix so we don't crash if the episode has no associated video file:
            filename = ''
        elif isinstance(files, list):
            filename = files[0].filename
        else:
            filename = files.filename

        return SmewtUrl('action', 'play', { 'filename1': filename })
