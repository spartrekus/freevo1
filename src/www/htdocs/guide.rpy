#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# guide.rpy - Web interface to the Freevo EPG.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.20  2004/02/09 21:23:42  outlyer
# New web interface...
#
# * Removed as much of the embedded design as possible, 99% is in CSS now
# * Converted most tags to XHTML 1.0 standard
# * Changed layout tables into CSS; content tables are still there
# * Respect the user configuration on time display
# * Added lots of "placeholder" tags so the design can be altered pretty
#   substantially without touching the code. (This means using
#   span/div/etc. where possible and using 'display: none' if it's not in
#   _my_ design, but might be used by someone else.
# * Converted graphical arrows into HTML arrows
# * Many minor cosmetic changes
#
# Revision 1.19  2003/10/20 02:24:17  rshortt
# more tv_util fixes
#
# Revision 1.18  2003/09/07 18:50:56  dischi
# make description shorter if it's too long
#
# Revision 1.17  2003/09/07 01:02:13  gsbarbieri
# Fixed a bug in guide that appeared with the new PRECISION thing.
#
# Revision 1.16  2003/09/06 22:58:13  mikeruelle
# fix something i don't think sould have a gap

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

import sys, string
import time

from www.web_types import HTMLResource, FreevoResource
from twisted.web.woven import page

import util.tv_util as tv_util
import util
import config 
import tv.epg_xmltv 
import tv.record_client as ri
from twisted.web import static

DEBUG = 0

TRUE = 1
FALSE = 0

MAX_DESCRIPTION_CHAR = 1000

class GuideResource(FreevoResource):

    def makecategorybox(self, chanlist):
        allcategories = []
        for chan in chanlist:
            for prog in chan.programs:
                if prog.categories:
                    allcategories.extend(prog.categories)
        if allcategories:
            allcategories=util.unique(allcategories)
            allcategories.sort()
        else:
            return ''
        retval = '<select name="category">' + "\n"
        for cat in allcategories:
            retval += '<option value="%s" ' % cat
            retval += '>%s' % cat
            retval += "\n"
        retval += '</select>' + "\n"
        return retval

    def maketimejumpboxday(self, gstart):
        retval='<select name="day">\n'
        myt = time.time()
        myt_t = time.localtime(myt)
        gstart_t = time.localtime(gstart)
        myt = time.mktime((myt_t[0], myt_t[1], myt_t[2], 0, 0, 5, 
                           myt_t[6], myt_t[7], -1))
        listh = tv_util.when_listings_expire()
        if listh == 0:
            return retval + '</select>\n'
        listd = int((listh/24)+2)
        for i in range(1, listd):
            retval += '<option value="' + str(myt) + '"'
            myt_t = time.localtime(myt)
            if (myt_t[0] == gstart_t[0] and \
                myt_t[1] == gstart_t[1] and \
                myt_t[2] == gstart_t[2]):
                retval += ' SELECTED '
            retval += '>' + time.strftime('%a %b %d', myt_t) + '\n'
            myt += 60*60*24
        retval += '</select>\n'
        return retval


    def maketimejumpboxoffset(self, gstart):
        retval = '<select name="offset">\n'
        myt = gstart
        myt_t = time.localtime(myt)
        hrstart = time.mktime((myt_t[0], myt_t[1], myt_t[2], 0, 0, 5, 
                               myt_t[6], myt_t[7], -1))
        hrinc = hrstart
        hrstop = hrstart + (60*60*24)
        while (hrinc < hrstop):
            myoff = hrinc - hrstart
            retval += '<option value="' + str(myoff) + '"'
            if (abs(gstart - hrinc) < 60):
                retval += ' SELECTED '
            retval += '>' + time.strftime(config.TV_TIMEFORMAT, time.localtime(hrinc)) + '\n'
            hrinc += config.WWW_GUIDE_INTERVAL * 60
        retval += '</select>\n'
        return retval


    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        INTERVAL = config.WWW_GUIDE_INTERVAL * 60
        PRECISION = config.WWW_GUIDE_PRECISION * 60
        cpb = INTERVAL / PRECISION # cols per block/interval
        n_cols = config.WWW_GUIDE_COLS

        mfrguidestart = time.time()
        mfrguideinput = fv.formValue(form, 'stime')
        mfrguideinputday = fv.formValue(form, 'day')
        mfrguideinputoff = fv.formValue(form, 'offset')
        if mfrguideinput:
            mfrguidestart = int(mfrguideinput)
        elif mfrguideinputday and mfrguideinputoff:
            mfrguidestart = float(mfrguideinputday) + float(mfrguideinputoff)
        now = int(mfrguidestart / INTERVAL) * INTERVAL
        now2 = int(time.time() / INTERVAL) * INTERVAL
        mfrnextguide = now + INTERVAL * n_cols
        mfrnextguide += 10
        mfrprevguide = now - INTERVAL * n_cols
        mfrprevguide += 10
        if mfrprevguide < now2:
            mfrprevguide = 0

        guide = tv.epg_xmltv.get_guide()
        (got_schedule, schedule) = ri.getScheduledRecordings()
        if got_schedule:
            schedule = schedule.getProgramList()

        fv.printHeader('TV Guide', config.WWW_STYLESHEET, config.WWW_JAVASCRIPT, selected='TV Guide')
        fv.res += '<div id="content">\n';
        fv.res += '&nbsp;<br/>\n'
        if not got_schedule:
            fv.res += '<h4>The recording server is down, recording information is unavailable.</h4>'

        pops = ''
        desc = ''

        fv.tableOpen()
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('<form>Time:&nbsp;' + self.maketimejumpboxday(now) + self.maketimejumpboxoffset(now) + '<input type=submit value="View"></form>', 'class="utilhead1"')
        categorybox =  self.makecategorybox(guide.chan_list)
        if categorybox:
            fv.tableCell('<form action="genre.rpy">Show&nbsp;Category:&nbsp;'+categorybox+'<input type=submit value="Change"></form>', 'class="utilhead2"')
        fv.tableRowClose()
        fv.tableClose()

        fv.tableOpen('cols=\"%d\"' % \
                     ( n_cols*cpb + 1 ) )
        showheader = 0
        for chan in guide.chan_list:
            #put guidehead every X rows
            if showheader % 15 == 0:
                fv.tableRowOpen('class="chanrow"')
                headerstart = int(mfrguidestart / INTERVAL) * INTERVAL
                fv.tableCell(time.strftime('%b %d', time.localtime(headerstart)), 'class="guidehead"')
                for i in range(n_cols):
                    if i == n_cols-1 or i == 0:
                        dacell = ''
                        datime = time.strftime(config.TV_TIMEFORMAT, time.localtime(headerstart))
                        if i == n_cols-1:
                            dacell = datime + '&nbsp;&nbsp;<a href="guide.rpy?stime=%i">&raquo;</a>' % mfrnextguide
                        else:                            
                            if mfrprevguide > 0:
                                dacell = '<a href="guide.rpy?stime=%i">&laquo;</a>&nbsp;&nbsp;' % mfrprevguide + datime
                            else:
                                dacell = datime
                        fv.tableCell(dacell, 'class="guidehead"  colspan="%d"' % cpb)
                    else:
                        fv.tableCell(time.strftime(config.TV_TIMEFORMAT, time.localtime(headerstart)),
                                     'class="guidehead" colspan="%d"' % cpb)
                    headerstart += INTERVAL
                fv.tableRowClose()
            showheader+= 1
                
            now = mfrguidestart
            fv.tableRowOpen('class="chanrow"')
            # chan.displayname = string.replace(chan.displayname, "&", "SUB")
            fv.tableCell(chan.displayname, 'class="channel"')
            c_left = n_cols * cpb

            if not chan.programs:
                fv.tableCell('&laquo; NO DATA &raquo;', 'class="programnodata" colspan="%s"' % (n_cols* cpb) )

            for prog in chan.programs:
                if prog.stop > mfrguidestart and \
                   prog.start < mfrnextguide and \
                   c_left > 0:

                    status = 'program'

                    if got_schedule:
                        (result, message) = ri.isProgScheduled(prog, schedule)
                        if result:
                            status = 'scheduled'
                            really_now = time.time()
                            if prog.start <= really_now and prog.stop >= really_now:
                                # in the future we should REALLY see if it is 
                                # recording instead of just guessing
                                status = 'recording'

                    if prog.start <= now and prog.stop >= now:
                        cell = ""
                        if prog.start <= now - INTERVAL:
                            # show started earlier than the guide start,
                            # insert left arrows
                            cell += '&laquo; '
                        showtime_left = int(prog.stop - now + ( now % INTERVAL ) )
                        intervals = showtime_left / PRECISION
                        colspan = intervals
                        # prog.title = string.replace(prog.title, "&", "SUB")
                        # prog.desc = string.replace(prog.desc, "&", "SUB")
                        cell += '%s' % prog.title
                        if colspan > c_left:                            
                            # show extends past visible range,
                            # insert right arrows
                            cell += '   &raquo;'
                            colspan = c_left
                        popid = '%s:%s' % (prog.channel_id, prog.start)

                        if prog.desc == '':
                            desc = ( 'Sorry, the program description for ' + \
                                     '<b>%s</b> is unavailable.' ) % prog.title
                        else:
                            desc = prog.desc

                        desc = desc.lstrip()
                        if MAX_DESCRIPTION_CHAR and len(desc) > MAX_DESCRIPTION_CHAR:
                            desc=desc[:desc[:MAX_DESCRIPTION_CHAR].rfind('.')] + '. [...]'
                        pops += """
<div id="%s" class="proginfo">
   <table class="popup"
          onmouseover="focusPop('%s');"
          onmouseout="unfocusPop('%s');">
      <thead>
         <tr>
            <td>
               %s
            </td>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td class="progdesc">
               %s
            </td>            
         </tr>
         <tr>
         <td class="progtime">
            <b>Start:</b> %s, 
            <b>Stop:</b> %s,
            <b>Runtime:</b> %smin
            </td>
         </td>
      </tbody>
      <tfoot>
         <tr>
            <td>
               <table class="popupbuttons">
                  <tbody>
                     <tr>
                        <td onclick="document.location='record.rpy?chan=%s&start=%s&action=add'">
                           Record
                        </td>
                        <td onclick="document.location='edit_favorite.rpy?chan=%s&start=%s&action=add'">
                           Add to Favorites
                        </td>
                        <td onclick="javascript:closePop('%s');">
                           Close Window
                        </td>
                     </tr>
                  </tbody>
               </table>
            </td>
         </tr>
      </tfoot>
   </table>
</div>
                        """ % ( popid, popid, popid, prog.title, desc,
                                time.strftime(config.TV_TIMEFORMAT, time.localtime( prog.start ) ),
                                time.strftime(config.TV_TIMEFORMAT, time.localtime( prog.stop ) ),
                                int( ( prog.stop - prog.start ) / 60 ),
                                prog.channel_id, prog.start,
                                prog.channel_id, prog.start, popid )
                        
                        style = ''
                        if colspan == n_cols * cpb:
                            style += 'text-align: center; '
                        
                        fv.tableCell(cell, 'class="'+status+'" onclick="showPop(\'%s\', this)" colspan="%s" style="%s"' % (popid, colspan, style))
                        now += colspan * PRECISION
                        c_left -= colspan

            fv.tableRowClose()
        fv.tableClose()
        
        fv.res += pops

        fv.printSearchForm()
        fv.printLinks()
        fv.res += '</div>'
        fv.printFooter()

        return fv.res


resource = GuideResource()
