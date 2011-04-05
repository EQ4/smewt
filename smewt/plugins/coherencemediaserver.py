# -*- coding: utf-8 -*-
# -*- Mode: python; coding: utf-8; tab-width: 8; indent-tabs-mode: t; -*-
#
# Copyright 2011, Caleb Callaway <enlightened-despot@gmail.com>
# Copyright 2008-2010, Frank Scholz <dev@coherence-project.org>
# Copyright 2008, James Livingston <doclivingston@gmail.com>
#
# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

from PyQt4.QtCore import QObject, SIGNAL

import coherence.extern.louie as louie

from coherence import log

# for the icon
import os.path, urllib

class CoherencePlugin(log.Loggable,QObject):

    logCategory = 'smewt_coherence_plugin'

    def __init__(self):
        QObject.__init__(self)
        self.coherence = None

    def activate(self, smewt_db):                
        try:
          from smewt.plugins import qt4reactor
          qt4reactor.install()
        except AssertionError, e:
          # sometimes it's already installed
          self.warning("qt4reactor already installed %r" % e)

        self.coherence = self.get_coherence()
        if self.coherence is None:
          self.warning("Coherence is not installed or too old, aborting")
          return

        self.warning("Coherence UPnP plugin activated")

        self.smewt_db = smewt_db
        self.sources = {}
          
        kwargs = {}
        kwargs['smewt_db'] = self.smewt_db
        
        # Get the UUID of the Digital Media Server from the configuration object in the Smewt Db
        dms_uuid = self.smewt_db.find_one('Config').get('coherence_dmsuuid', None)

        if dms_uuid:
          kwargs['uuid'] = dms_uuid
        
        from coherence.upnp.devices.media_server import MediaServer
        from coherencestore import MediaStore
        
        self.server = MediaServer(self.coherence, MediaStore, **kwargs)
        
        from twisted.internet import reactor
        
        #self.connect(self, SIGNAL("deactivating()"), reactor.stop)
        
        reactor.runReturn(installSignalHandlers=False)
        #reactor.run()
        
        # Set the UUID of the Digital Media Server of the configuration object in the Smewt Db
        if dms_uuid is None:
          self.smewt_db.find_one('Config').coherence_dmsuuid = str(self.server.uuid)
          
        self.warning("Media Store available with UUID %s" % str(self.server.uuid))

    def deactivate(self, smewt_db=None):
        self.info("Coherence UPnP plugin deactivated")
        if self.coherence is None:
            return
        
        self.coherence.shutdown()
        
        #from twisted.internet import reactor
        #reactor.stop()
        #self.emit(SIGNAL("deactivating()"))
        
        #from twisted.internet import reactor
        #QTimer.singleShot(0, reactor, SLOT("stop()"));
        
        from twisted.internet import reactor
        reactor.stop()
        
        del self.coherence


    def get_coherence (self):
        coherence_instance = None
        required_version = (0, 5, 7)

        try:
            from coherence.base import Coherence
            from coherence import __version_info__
        except ImportError, e:
            print "Coherence not found"
            return None

        if __version_info__ < required_version:
            required = '.'.join([str(i) for i in required_version])
            found = '.'.join([str(i) for i in __version_info__])
            print "Coherence %s required. %s found. Please upgrade" % (required, found)
            return None

        self.coherence_version = __version_info__

        coherence_config = {
            #'logmode': 'info',
            'controlpoint': 'yes',
            'plugins': {},
            'logmode': 'warn'
        }

        coherence_instance = Coherence(coherence_config)

        return coherence_instance