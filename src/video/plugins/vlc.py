# -*- coding: iso-8859-1 -*-

# vlc.py - based on mplayer.py and xine.py

import os, re
import threading
import popen2
#import kaa.metadata as metadata

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.
import plugin

from event import *

class PluginInterface(plugin.Plugin):
    """
    VLC plugin for the video player
    
    originally only used for RTSP streams
    """

    def __init__(self):
        plugin.Plugin.__init__(self)
        plugin.register(Vlc(), plugin.VIDEO_PLAYER, True)

    def config(self):
        return [('VLC_CMD', '/usr/bin/vlc', 'Path to your vlc executable'),
                ('VLC_OPTIONS', 'None', 'Add your specific VLC options here'), 
                ('VIDEO_VLC_SUFFIX', '[]', 'List of suffixes to be played with vlc'),
               ]


class Vlc:
    """
    the main class to control vlc
    """
    def __init__(self):
        """
        init the vlc object
        """
        self.name       = 'vlc'
        self.app_mode   = 'video'
        self.app        = None
        self.plugins    = []
        self.cmd        = config.VLC_CMD


    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if not item.url:
            return 0
        if item.url[:7] == 'rtsp://':
            _debug_('vlc rating: %r good' % (item.url), 2)
            return 2
        # dvd with menu
        if item.url.startswith('dvd://') and item.url.endswith('/'):
            _debug_('vlc rating: %r good' % (item.url), 2)
            return 2
        # mimetype list from config (user's wishes)
        if item.mimetype in config.VIDEO_VLC_SUFFIX:
            _debug_('vlc rating: %r good' % (item.url), 2)
            return 2
        # network stream
        if item.network_play:
            _debug_('vlc rating: %r possible' % (item.url), 2)
            return 1
        _debug_('vlc rating: %r unplayable' % (item.url), 2)
        return 0


    def play(self, options, item):
        """
        play a videoitem with vlc
        """
        self.options = options
        self.item    = item

        mode         = item.mode
        url          = item.url

        self.item_info    = None
        self.item_length  = -1
        self.item.elapsed = 0

        try:
            _debug_('Vlc.play(): url=%s' % url)
        except UnicodeError:
            _debug_('Vlc.play(): [non-ASCII data]')

        if config.VLC_OPTIONS:
            vlc_options=config.VLC_OPTIONS

        command = self.cmd + ' ' + vlc_options + ' --intf dummy -f --key-quit=esc "%s"' % url
        rc.app(self)

        self.app = childapp.ChildApp2(command)
        return None


    def stop(self):
        """
        Stop vlc
        """
        if not self.app:
            return
        self.app.kill(2)

        rc.app(None)
        self.app = None


    def eventhandler(self, event, menuw=None):
        """
        eventhandler for vlc control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        #print "VLC::EventHendler : " + str(event)
        if not self.app:
            #print "VLC::Eventhandler : NNE"
            return self.item.eventhandler(event)

        if event == STOP:
            self.stop()
            return self.item.eventhandler(event)

        if event in ( PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        return self.item.eventhandler(event)
