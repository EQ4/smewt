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

from PyQt4.QtCore import Qt, SIGNAL, QObject
from smewtexception import SmewtException
from workerthread import WorkerThread
from mediaobject import Media, Metadata
import logging

class BaseChain(QObject):
    def __init__(self, *args):
        super(BaseChain, self).__init__()

        self.chain = args
        if not args:
            raise SmewtException('Tried to build an empty solving chain')

    def connectChain(self, connectionType):
        # connect each element (guesser, solver) to the next
        for elem, next in zip(self.chain[:-1], self.chain[1:]):
            self.connect(elem, SIGNAL('finished'),
                         next.start, connectionType)

        # connect the last solver's finished to the whole chain finish method
        self.connect(self.chain[-1], SIGNAL('finished'),
                     self.finished, connectionType)

    def finished(self, result):
        self.result = result
        media = result.findAll(Media)[0]
        if media.metadata:
            logging.info('Solving chain for file %s found metadata: %s', str(media), str(media.metadata))
        else:
            logging.info('Solving chain for file %s didn\'t find any metadata...', str(media))

        self.emit(SIGNAL('finished'), result)


class SolvingChain(BaseChain):
    def __init__(self, *args):
        super(SolvingChain, self).__init__(*args)
        self.connectChain(Qt.QueuedConnection)

    def start(self, query):
        '''Launches the solving chain process asynchronously, eg: it returns
        immediately and will emit the signal 'finished' along with the result of
        it when done.'''
        self.chain[0].start(query)


class BlockingChain(BaseChain):
    def __init__(self, *args):
        super(BlockingChain, self).__init__(*args)
        self.connectChain(Qt.DirectConnection)

    def solve(self, query):
        '''Launches the solving chain process synchronously, eg: it will only
        return when it has finished solving the chain. This method returns the
        result of the chain.'''
        self.chain[0].start(query)
        return self.result
