#!/usr/bin/env python
#-----------------------------------------------------------------------
# gui - First attempt at a freevo gui library
#-----------------------------------------------------------------------
# $Id$
#
# The goal is to make a OO GUI library for use with freevo. The main
# idea is that skins can use or inherit from this class and override
# when needed.
#
# Todo:  o Implement "listbox" for selections with different styles
#          for showing what is selected (glow, bg_color, etc)
#             ListItem -> Label -> Text
#        o Make GraphBar class.
#        o Make more excpetions.
#
# Done:  * Find a way to do Z-index handling.
#        * Split classes into separate files.
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/02/23 18:21:50  rshortt
# Some code cleanup, better OOP, influenced by creating a subclass of RegionScroller called ListBox.
#
# Revision 1.3  2003/02/19 00:58:18  rshortt
# Added scrolldemo.py for a better demonstration.  Use my audioitem.py
# to test.
#
# Revision 1.2  2003/02/18 13:40:53  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
#
# Revision 1.1  2002/12/07 15:21:31  dischi
# moved subdir gui into src
#
# Revision 1.5  2002/10/09 02:35:15  krister
# Removed special workarounds for the old runtime since the new runtime works better.
#
# Revision 1.4  2002/09/26 09:20:58  dischi
# Fixed (?) bug when using freevo_runtime. Krister, can you take a look
# at that?
#
# Revision 1.3  2002/09/21 10:06:47  dischi
# Make it work again, the last change was when we used osd_sdl.py
#
# Revision 1.2  2002/08/18 22:15:20  tfmalt
# o Moved debug and test code to its own file.
#
# Revision 1.1  2002/08/15 22:45:42  tfmalt
# o Inital commit of Freevo GUI library. Files are put in directory 'gui'
#   under Freevo.
# o At the moment the following classes are implemented (but still under
#   development):
#     Border, Color, Label, GUIObject, PopupBox, ZIndexRenderer.
# o These classes are fully workable, any testing and feedback will be
#   appreciated.
#
# Revision 1.2  2002/08/13 12:46:48  tfmalt
# o Implemented ZIndexRenderer to keep track of what is under objects and
#   redrawing supporting N levels of transparency (for example copy gui_sdl
#   to main freevo catalog and run standalone.
#
#-----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------
"""
A Object Oriented GUI Widget library for Freevo

This is aimed at being a general library for GUI programming with Freevo.
It is built directly on top of SDL with pygame, and it's aimed at being
fairly fast.

Event though the library is built from the ground the design is heavy
influenced by other GUI toolkits, such as Java JDK and QT.

Currently not many classes are in place, but hopefully we will add more
in time.
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


DEBUG = 0

import sys
import os.path
    
from gui.Border         import *
from gui.Color          import *
from gui.GUIObject      import *
from gui.PopupBox       import *
from gui.AlertBox       import *
from gui.ConfirmBox     import *
from gui.Label          import *
from gui.Button         import *
from gui.LetterBox      import *
from gui.LetterBoxGroup import *
from gui.RegionScroller import *
from gui.Scrollbar      import *
from gui.InputBox       import *
from gui.exceptions     import *
from gui.scrolldemo     import *
from gui.listboxdemo    import *


if DEBUG:
    from gui.debug import *
    


