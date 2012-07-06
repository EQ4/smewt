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

from pygoo import MemoryObjectGraph
from smewt.base import SmewtException, Media, Config
from serieobject import Series, Episode
from smewt.media import get_mako_template, render_mako_template
from smewt.media.subtitle.subtitleobject import Subtitle
from smewt.base.utils import smewtDirectory


def render_mako(url, collection):
    tmap = { 'single': 'view_episodes_by_season.mako',
             'all': 'view_all_series.mako',
             'suggestions': 'view_episode_suggestions.mako'
             }

    t = get_mako_template('series', tmap, url.viewType)

    if url.viewType == 'single':
        # FIXME: this definitely doesn't belong here...
        try:
            config = collection.find_one(Config)
        except ValueError:
            config = collection.Config(displaySynopsis = True)

        return t.render_unicode(series = collection.find_one(Series, title=url.args['title']),
                                displaySynopsis = config.displaySynopsis)

    elif url.viewType == 'all':
        return t.render(series = collection.find_all(Series))

    elif url.viewType == 'suggestions':
        return t.render(episodes=[ ep for ep in collection.find_all(Episode) if 'lastViewed' in ep ])

    else:
        raise SmewtException('Invalid view type: %s' % url.viewType)


def render(url, collection):
    return render_mako_template(render_mako, url, collection)
