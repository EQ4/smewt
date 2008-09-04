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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class BookmarkWidget(QPushButton):
    def __init__(self,  desc,  url):
        super(BookmarkWidget,  self).__init__(desc)
        self.url = url
        self.connect(self,  SIGNAL('clicked()'),  self.sendUrl)

    def sendUrl(self):
        self.emit(SIGNAL('selected'),  self.url)

class BookmarkListWidget(QWidget):
    def __init__(self):
        super(BookmarkListWidget, self).__init__()
        self.bookmarks = {'All Series':'smewt://serie/all'}

        layout = QVBoxLayout()

        for name,  url in self.bookmarks.items():
            button = BookmarkWidget(name,  url)
            self.connect(button,  SIGNAL('selected'),  self.sendUrl)
            layout.addWidget(button)
        layout.addStretch(1)

        self.setLayout(layout)

    def sendUrl(self,  url):
        self.emit(SIGNAL('selected'),  url)