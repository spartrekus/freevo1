#if 0 /*
# -----------------------------------------------------------------------
# file_ops.py - Small file operations (currently only delete)
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.18  2004/02/14 13:03:32  dischi
# o make it possible to turn off the menu item for delete image/info
# o use new menu delete_submenu function
#
# Revision 1.17  2004/01/31 13:15:14  dischi
# only add the plugin if the parent is a dir
#
# Revision 1.16  2004/01/30 20:42:03  dischi
# set item.image to parent when deleting it
#
# Revision 1.15  2004/01/09 21:11:45  dischi
# crash on debug: item may have no url
#
# Revision 1.14  2004/01/04 11:17:38  dischi
# make it possible to delete only the image
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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
# ----------------------------------------------------------------------- */
#endif

import os
import config
import plugin
import util

from gui.ConfirmBox import ConfirmBox

class PluginInterface(plugin.ItemPlugin):
    """
    small plugin to delete files
    """
    def config(self):
        return [ ('FILE_OPS_ALLOW_DELETE_IMAGE', True,
                  'Add delete image to the menu.'),
	         ('FILE_OPS_ALLOW_DELETE_INFO', True,
                  'Add delete info to the menu.') ]

    def actions(self, item):
        """
        create list of possible actions
        """
        if not item.parent or not item.parent.type == 'dir':
            # only activate this for directory listings
            return []

        self.item = item

        items = []
        
        if hasattr(item, 'files') and item.files:
            if item.files.delete_possible():
                items.append((self.confirm_delete, _('Delete'), 'delete'))
            if item.files.fxd_file and config.FILE_OPS_ALLOW_DELETE_INFO:
                items.append((self.confirm_info_delete, _('Delete info'), 'delete_info'))
            if item.files.image and config.FILE_OPS_ALLOW_DELETE_IMAGE:
                items.append((self.confirm_image_delete, _('Delete image'), 'delete_image'))
        return items


    def confirm_delete(self, arg=None, menuw=None):
        self.menuw = menuw
        ConfirmBox(text=_('Do you wish to delete\n \'%s\'?') % self.item.name,
                   handler=self.delete_file, default_choice=1).show()
        
    def confirm_info_delete(self, arg=None, menuw=None):
        self.menuw = menuw
        ConfirmBox(text=_('Delete info about\n \'%s\'?') % self.item.name,
                   handler=self.delete_info, default_choice=1).show()

    def confirm_image_delete(self, arg=None, menuw=None):
        self.menuw = menuw
        ConfirmBox(text=_('Delete image about\n \'%s\'?') % self.item.name,
                   handler=self.delete_image, default_choice=1).show()

    def safe_unlink(self, filename):
        try:
            os.unlink(filename)
        except:
            print 'can\'t delete %s' % filename
        
    def delete_file(self):
        self.item.files.delete()
        if self.menuw:
            self.menuw.delete_submenu(True, True)

    def delete_info(self):
        self.safe_unlink(self.item.files.image)
        self.safe_unlink(self.item.files.fxd_file)
        if self.menuw:
            self.menuw.delete_submenu(True, True)

    def delete_image(self):
        self.safe_unlink(self.item.files.image)
        if self.item.parent:
            self.item.image = self.item.parent.image
        else:
            self.item.image = None
        if self.menuw:
            self.menuw.delete_submenu(True, True)
