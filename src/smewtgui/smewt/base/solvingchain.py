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

from PyQt4.QtCore import SIGNAL, QObject
from smewtexception import SmewtException

class SolvingChain(QObject):
    def __init__(self, *args):
        super(SolvingChain, self).__init__()

        self.chain = args
        if not args:
            raise SmewtException('Tried to build an empty solving chain')

        # connect each element (guesser, solver) to the next
        for elem, next in zip(self.chain[:-1], self.chain[1:]):
            self.connect(elem, SIGNAL('finished'),
                         next.start)

        # connect the last solver's finished to the whole chain finish method
        self.connect(self.chain[-1], SIGNAL('finished'),
                     self.finished)


    def start(self):
        self.chain[0].start()

    def finished(self, result):
        self.emit(SIGNAL('finished'), result)
