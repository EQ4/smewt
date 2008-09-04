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

from smewt import config
from smewt.guessers.guesser import Guesser
from smewt.media.series import Episode
from smewt.media.series.IMDBSerieMetadataFinder import IMDBSerieMetadataFinder

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode


class EpGuideQuerier(QObject):
    episodeLists = {}

    def __init__(self, mediaObject):
        super(EpGuideQuerier, self).__init__()

        self.mediaObject = mediaObject

        self.connect(self, SIGNAL('gotEpisodeList'),
                     self.makeGuesses)

        if config.test_localweb:
            self.connect(self, SIGNAL('gotSerie'),
                         self.getEpisodeList)
            self.getGoogleResult(True)
            return

        # urllib doesn't cut it against google, better use webkit here...
        #return urlopen('http://www.google.com/search', urlencode({'q': name})).read()
        self.googleResult = None
        self.queryPage = QWebView()

        self.connect(self.queryPage, SIGNAL('loadFinished(bool)'),
                     self.getGoogleResult)

        self.connect(self, SIGNAL('gotSerie'),
                     self.getEpisodeList)


    def query(self):
        if self.episodeLists.has_key(self.mediaObject['serie']):
            self.emit(SIGNAL('gotEpisodeList'))
        else:
            logging.info('Guesser: EpGuides - looking for serie %s', self.mediaObject['serie'])
            query = 'allintitle: site:epguides.com ' + self.mediaObject['serie']
            url = QUrl.fromEncoded('http://www.google.com/search?' + urlencode({'q': query},  doseq=True))
            self.queryPage.load(url)

    def getGoogleResult(self, ok):
        logging.info('Guesser: EpGuides - got result url from google ok = %s', ok)
        if config.test_localweb:
            self.googleResult = open(config.local_epguides_googleresult).read().decode('utf-8')
        else:
            self.googleResult = unicode(self.queryPage.page().mainFrame().toHtml())

        matches = re.compile('<h2 class.*?a href=\"(.*?)\" class').findall(self.googleResult)
        if not matches:
            self.episodeLists[self.mediaObject['serie']] = []
            self.emit(SIGNAL('gotEpisodeList'))
            return

        self.serieUrl = matches[0]
        logging.info('Found: %s', self.serieUrl)
        self.emit(SIGNAL('gotSerie'), self.serieUrl)

    def getEpisodeList(self, url):
        logging.info('Getting episode list...')
        if config.test_localweb:
            html = open(config.local_epguides_episodelist).read()
        else:
            html = urlopen(url).read()
        logging.info('Guesser: EpGuides - got episodes list from epguides')

        # extract serie name
        try:
            serieName = re.compile('<h1>.*?>(.*?)</a></h1>').findall(html)[0]
        except IndexError:
            self.episodeLists[self.mediaObject['serie']] = []
            self.emit(SIGNAL('gotEpisodeList'))
            return

        #print 'found seriename:', serieName

        # extract episode table text
        tableText = re.compile('<pre>(.*?)</pre>', re.DOTALL).findall(html)[0]

        # try to get the info for each episode
        episodes = []
        for line in tableText.split('\n'):
            rexp = '[0-9]+\. *(?P<season>[0-9]+)- *(?P<episodeNumber>[0-9]+) *(?P<prodNumber>[^ ]+) *'
            rexp += '(?P<originalAirDate>[0-9]+ ... [0-9]+)?.*href="(?P<epguideUrl>.*?)">(?P<title>.*)</a>'
            result = re.compile(rexp).search(line)
            if result:
                # FIXME: surely there is a better way to do this...
                # we get this from the web, assume iso-8859-1
                d = result.groupdict()
                for name, value in d.items():
                    if type(value) == str:
                        d[name] = value.decode('iso-8859-1')
                newep = Episode.fromDict(d)
                newep['serie'] = unicode(serieName)

                episodes.append(newep)

        self.episodeLists[self.mediaObject['serie']] = episodes
        self.emit(SIGNAL('gotEpisodeList'))
        #self.episodes = episodes

    def makeGuesses(self):
        import copy
        guesses = []
        episodeList = self.episodeLists[self.mediaObject['serie']]
        for newep in episodeList:
            # Calculate the confidence of the episode
            # We compare how many matching properties it has with the input mediaObject
            # we weight the matching by the confidence of each property
            commonProps = set(newep.properties) & set(self.mediaObject.properties)
            episodeConfidence = 0.0
            for prop in commonProps:
                if newep[prop] == self.mediaObject[prop]:
                    #episodeConfidence += newep.confidence.get(prop, 1.0) * self.mediaObject.confidence.get(prop, 1.0)
                    #try:
                    episodeConfidence += 1.0
                    #except

            episodeConfidence /= float(len(commonProps)) + 1
            #print 'Guesser: episode confidence == %.3f' % episodeConfidence
            #print newep

            guess = Episode()
            guess.confidence = episodeConfidence
            for prop in newep.properties:
                guess[prop] = newep[prop]
                #guess.confidence[prop] = 0.9 * episodeConfidence

            guesses.append(guess)

        self.emit(SIGNAL('finished'), self.mediaObject, guesses)

class IMDBMetadataProvider(QObject):
    def __init__(self, metadata):
        super(IMDBMetadataProvider, self).__init__()

        if not metadata['serie']:
            raise SmewtException('IMDBMetadataProvider: Metadata doesn\'t contain \'serie\' field: %s', md)

        self.metadata = metadata
        self.imdb = IMDBSerieMetadataFinder()

    def start(self):
        name = self.metadata['serie']
        url = self.imdb.getSerieUrl(name)
        eps = self.imdb.getAllEpisodes(name, url)
        lores, hires = self.imdb.getSeriePoster(url)
        for ep in eps:
            ep['loresImage'] = lores
            ep['hiresImage'] = hires

        self.emit(SIGNAL('finished'), self.metadata, eps)


class EpisodeIMDB(Guesser):

    supportedTypes = [ 'video' ]

    def __init__(self):
        super(EpisodeIMDB, self).__init__()

    def start(self, query):
        self.checkValid(query)
        self.query = query

        found = query.metadata
        media = query.media[0]
        self.webparser = {}

        for md in list(found):
            if md['serie']:
                self.webparser[md] = IMDBMetadataProvider(md)
                self.connect(self.webparser[md], SIGNAL('finished'),
                             self.queryFinished)
            else:
                logging.warning('EpisodeIMDB: Metadata doesn\'t contain \'serie\' field: %s', md)

        for mdprovider in self.webparser.values():
            mdprovider.start()

    def queryFinished(self, metadata, guesses):
        del self.webparser[metadata]

        self.query.metadata += guesses

        if len(self.webparser) == 0:
            self.emit(SIGNAL('finished'), self.query)