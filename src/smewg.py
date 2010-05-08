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

from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QStatusBar, QProgressBar, QHBoxLayout, QStackedWidget, QIcon, QSystemTrayIcon, QAction, QMenu, QMessageBox, QToolBar
from PyQt4.QtCore import SIGNAL, QSize, Qt, QSettings, QVariant, QPoint, QSize, QObject
import sys, logging, os, os.path
from smewt.gui import MainWidget, FeedWatchWidget
from smewt.base.utils import smewtDirectory

log = logging.getLogger('smewg')
DEFAULT_WIDTH = 900
DEFAULT_HEIGHT = 740


class StatusWidget(QWidget):
    def __init__(self):
        super(QWidget,  self).__init__()

        layout = QHBoxLayout()
        layout.addStretch()

        self.progressBar = QProgressBar()

        layout.addWidget(self.progressBar)

        self.setLayout(layout)
        return

class SmewtGui(QMainWindow):

    def __init__(self):
        super(SmewtGui, self).__init__()
        self.setWindowTitle('Smewg - An Ordinary Smewt Gui')

        self.readWindowSettings()

        self.icon = QIcon(smewtDirectory('smewt', 'icons', 'smewt.svg'))
        self.setWindowIcon(self.icon)

        self.createWidgets()
        self.createActions()

        # create menubar
        mainMenu = self.menuBar().addMenu('Main')
        mainMenu.addAction(self.quitAction)

        importMenu = self.menuBar().addMenu('Collection')
        importMenu.addAction(self.selectMoviesFoldersAction)
        importMenu.addAction(self.selectSeriesFoldersAction)
        importMenu.addSeparator()
        importMenu.addAction(self.updateCollectionAction)
        # temporarily hide as it creates more problems than it solves
        #importMenu.addAction(self.rescanCollectionAction)

        helpMenu = self.menuBar().addMenu('Help')
        helpMenu.addAction(self.aboutAction)
        helpMenu.addAction(self.aboutQtAction)

        # create toolbar
        navigationToolBar = QToolBar('Navigation')
        navigationToolBar.addAction(self.backAction)
        navigationToolBar.addAction(self.fwdAction)
        navigationToolBar.addAction(self.homeAction)
        navigationToolBar.addSeparator()
        navigationToolBar.addAction(self.zoomOutAction)
        navigationToolBar.addAction(self.zoomInAction)
        navigationToolBar.addSeparator()
        navigationToolBar.addAction(self.fullScreenAction)
        navigationToolBar.setIconSize(QSize(32,32))
        navigationToolBar.setObjectName('navigationToolBar')
        self.addToolBar(navigationToolBar)
        self.createTrayIcon()

        # tmp
        self.connect(self.mainWidget, SIGNAL('feedwatcher'),
                     self.showFeedWatcher)

    def shutdown(self):
        self.mainWidget.shutdown()

    def showFeedWatcher(self):
        self.tabWidget.setCurrentIndex(1)

    def showSpeedDial(self):
        self.tabWidget.setCurrentIndex(0)
        self.mainWidget.speedDial()

    def createWidgets(self):
        self.mainWidget = MainWidget()
        self.feedWatchWidget = FeedWatchWidget()

        self.tabWidget = QStackedWidget()
        self.tabWidget.addWidget(self.mainWidget)
        self.tabWidget.addWidget(self.feedWatchWidget)

        self.setCentralWidget(self.tabWidget)

        self.statusWidget = StatusWidget()
        self.statusBar().addPermanentWidget(self.statusWidget)


        self.connect(self.mainWidget, SIGNAL('progressChanged'), self.progressChanged)

    def createActions(self):
        self.quitAction = QAction('Quit', self)
        self.connect(self.quitAction, SIGNAL('triggered()'),
                     self.quit)

        self.minimizeAction = QAction('Minimize', self)
        self.connect(self.minimizeAction, SIGNAL('triggered()'),
                     self.hide)

        self.restoreAction = QAction('Restore', self)
        self.connect(self.restoreAction, SIGNAL('triggered()'),
                     self.showNormal)

        self.aboutAction = QAction('About', self)
        self.connect(self.aboutAction, SIGNAL('triggered()'),
                     self.about)

        self.aboutQtAction = QAction('About Qt', self)
        self.connect(self.aboutQtAction, SIGNAL('triggered()'),
                     self.aboutQt)


        # navigation bar
        self.backAction = QAction(QIcon(smewtDirectory('smewt', 'icons', 'go-previous.png')), 'Back', self)
        self.backAction.setStatusTip('Go back')
        self.connect(self.backAction, SIGNAL('triggered()'),
                     self.mainWidget.back)

        self.fwdAction = QAction(QIcon(smewtDirectory('smewt', 'icons', 'go-next.png')), 'Forward', self)
        self.fwdAction.setStatusTip('Go forward')
        self.connect(self.fwdAction, SIGNAL('triggered()'),
                     self.mainWidget.forward)

        self.homeAction = QAction(QIcon(smewtDirectory('smewt', 'icons', 'go-home.png')), 'Home (Speed Dial)', self)
        self.homeAction.setStatusTip('Returns to the speed dial')
        self.connect(self.homeAction, SIGNAL('triggered()'),
                     self.showSpeedDial)


        self.zoomInAction = QAction(QIcon(smewtDirectory('smewt', 'icons', 'zoom-in.png')), 'Zoom in', self)
        self.zoomInAction.setStatusTip('Make the text larger')
        self.connect(self.zoomInAction, SIGNAL('triggered()'),
                     self.mainWidget.zoomIn)

        self.zoomOutAction = QAction(QIcon(smewtDirectory('smewt', 'icons', 'zoom-out.png')), 'Zoom out', self)
        self.zoomOutAction.setStatusTip('Make the text smaller')
        self.connect(self.zoomOutAction, SIGNAL('triggered()'),
                     self.mainWidget.zoomOut)

        self.fullScreenAction = QAction(QIcon(smewtDirectory('smewt', 'icons', 'view-fullscreen.png')), 'Full Screen', self)
        self.fullScreenAction.setStatusTip('Toggle fullscreen mode')
        self.fullScreenAction.setCheckable(True)
        self.connect(self.fullScreenAction, SIGNAL('triggered()'),
                     self.toggleFullScreen)

        # import actions

        self.selectMoviesFoldersAction = QAction('Select movies folders', self)
        self.selectMoviesFoldersAction.setStatusTip('Select the folders containing movies')
        self.connect(self.selectMoviesFoldersAction,  SIGNAL('triggered()'),
                     self.mainWidget.selectMoviesFolders)

        self.selectSeriesFoldersAction = QAction('Select series folders', self)
        self.selectSeriesFoldersAction.setStatusTip('Select the folders containing series')
        self.connect(self.selectSeriesFoldersAction,  SIGNAL('triggered()'),
                     self.mainWidget.selectSeriesFolders)

        self.updateCollectionAction = QAction('Update collection', self)
        self.updateCollectionAction.setStatusTip('Update the collection')
        self.connect(self.updateCollectionAction,  SIGNAL('triggered()'),
                     self.mainWidget.updateCollection)

        self.rescanCollectionAction = QAction('Rescan collection', self)
        self.rescanCollectionAction.setStatusTip('Rescan the collection')
        self.connect(self.rescanCollectionAction,  SIGNAL('triggered()'),
                     self.mainWidget.rescanCollection)

    def toggleFullScreen(self):
        flag = Qt.WindowFullScreen if self.fullScreenAction.isChecked() else ~Qt.WindowFullScreen
        self.setWindowState(self.windowState() ^ Qt.WindowFullScreen  )

    def quit(self):
        self.writeWindowSettings()
        self.mainWidget.quit()
        QApplication.instance().quit()

    def readWindowSettings(self):
        settings = QSettings()
        pos = settings.value("MainWindow/pos", QVariant(QPoint((QApplication.desktop().width()-DEFAULT_WIDTH)/2, (QApplication.desktop().width()-DEFAULT_HEIGHT)/2))).toPoint()
        size = settings.value("MainWindow/size", QVariant(QSize(DEFAULT_WIDTH, DEFAULT_HEIGHT))).toSize()
        self.resize(size)
        self.move(pos)

        self.restoreState(settings.value("MainWindow/windowstate").toByteArray())

    def writeWindowSettings(self):
        settings = QSettings()
        settings.setValue("MainWindow/pos", QVariant(self.pos()))
        settings.setValue("MainWindow/size", QVariant(self.size()))

        settings.setValue("MainWindow/windowstate", QVariant(self.saveState()))


    def createTrayIcon(self):
        trayMenu = QMenu(self)
        trayMenu.addAction(self.minimizeAction)
        trayMenu.addAction(self.restoreAction)
        trayMenu.addSeparator()
        trayMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self.icon, self)
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.setVisible(True)

        self.connect(self.trayIcon, SIGNAL('activated(QSystemTrayIcon::ActivationReason)'),
                     self.iconActivated)

    def setVisible(self, visible):
        self.minimizeAction.setEnabled(visible)
        self.restoreAction.setEnabled(not visible)
        QMainWindow.setVisible(self, visible)


    def iconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.setVisible(False)
            else:
                self.setVisible(True)

    def closeEvent(self, event):
        self.writeWindowSettings()
        self.hide()
        event.ignore()

    def progressChanged(self,  tagged,  total):
        if total == 0:
            self.statusWidget.progressBar.reset()
        else:
            self.statusWidget.progressBar.setMaximum(total)
            self.statusWidget.progressBar.setValue(tagged)

    def about(self):
        QMessageBox.about(self, 'About Smewt',
'''Smewt - a smart media manager

(c) 2008-2010 Nicolas Wack, Ricard Marxer
GPLv3 licensed''')

    def aboutQt(self):
        QMessageBox.aboutQt(self)


if __name__ == '__main__':
    import smewt
    app = QApplication(sys.argv)
    app.setOrganizationName('DigitalGaia')
    app.setOrganizationDomain('smewt.com')
    app.setApplicationName(smewt.APP_NAME)

    #from smewt.base import cache
    #cache.load('/tmp/smewt.cache')

    print 'smewt directory:',  smewtDirectory('smewt', 'media', 'speeddial')

    sgui = SmewtGui()

    QObject.connect(app, SIGNAL('aboutToQuit()'),
                    sgui.shutdown)

    sgui.show()
    app.exec_()

    #log.info('Writing cache to disk...')
    #cache.save('/tmp/smewt.cache')
    log.info('Exiting')
    sys.exit() # why is this necessary when running from eric?
