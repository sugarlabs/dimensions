#Copyright (c) 2009, Walter Bender

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import sugar
from sugar.activity import activity
try: # 0.86+ toolbar widgets
    from sugar.bundle.activitybundle import ActivityBundle
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.graphics.toolbarbox import ToolbarButton
except ImportError:
    pass
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.menuitem import MenuItem
from sugar.graphics.icon import Icon
from sugar.datastore import datastore

from gettext import gettext as _
import locale
import os.path

from sprites import *
import window

SERVICE = 'org.sugarlabs.VisualMatchActivity'
IFACE = SERVICE
PATH = '/org/augarlabs/VisualMatchActivity'

#
# Sugar activity
#
class VisualMatchActivity(activity.Activity):

    def __init__(self, handle):
        super(VisualMatchActivity,self).__init__(handle)

        try:
            # Use 0.86 toolbar design
            toolbar_box = ToolbarBox()

            # Buttons added to the Activity toolbar
            activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.show()

            # Button 1
            self.button1 = ToolButton( "button1off" )
            self.button1.set_tooltip(_('Button 1'))
            self.button1.props.sensitive = True
            self.button1.connect('clicked', self._button1_cb)
            toolbar_box.toolbar.insert(self.button1, -1)
            self.button1.show()

            # 3x3 Button
            self.button2 = ToolButton( "button2on" )
            self.button2.set_tooltip(_('Button 2'))
            self.button2.props.sensitive = True
            self.button2.connect('clicked', self._button2_cb)
            toolbar_box.toolbar.insert(self.button2, -1)
            self.button2.show()

            separator = gtk.SeparatorToolItem()
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # Label for showing status
            self.results_label = gtk.Label(_("say something here"))
            self.results_label.show()
            results_toolitem = gtk.ToolItem()
            results_toolitem.add(self.results_label)
            toolbar_box.toolbar.insert(results_toolitem,-1)

            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            separator.show()
            toolbar_box.toolbar.insert(separator, -1)

            # The ever-present Stop Button
            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl>Q'
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()

            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()

        except NameError:
            # Use pre-0.86 toolbar design
            self.toolbox = activity.ActivityToolbox(self)
            self.set_toolbox(self.toolbox)

            self.projectToolbar = ProjectToolbar(self)
            self.toolbox.add_toolbar( _('Project'), self.projectToolbar )

            self.toolbox.show()

        # Create a canvas
        canvas = gtk.DrawingArea()
        canvas.set_size_request(gtk.gdk.screen_width(), \
                                gtk.gdk.screen_height())
        self.set_canvas(canvas)
        canvas.show()
        self.show_all()

        # Initialize the canvas
        self.tw = window.new_window(canvas, \
                                    os.path.join(activity.get_bundle_path(), \
                                                 'images/card'), \
                                    self)

        # Read the mode from the Journal
        try:
            if self.metadata['status'] == 'one':
                self.show_button1()
            elif self.metadata['status'] == 'two':
                self.show_button2()
        except:
            self.metadata['status'] = "two"


    #
    # Button callbacks
    #
    def _button1_cb(self, button):
        self.show_button1()
        return True

    def show_button1(self):
        self.button1.set_icon("button1on")
        self.button2.set_icon("button2off")
        self.metadata['status'] = "one"
        # do something here

    def _button2_cb(self, button):
        self.show_button2()
        return True

    def show_button2(self):
        self.button1.set_icon("button1off")
        self.button2.set_icon("button2on")
        self.metadata['status'] = "two"
        # do something here

    """
    Write the additional status to the Journal
    """
    def write_file(self, file_path):
        pass

#
# Project toolbar for pre-0.86 toolbars
#
class ProjectToolbar(gtk.Toolbar):

    def __init__(self, pc):
        gtk.Toolbar.__init__(self)
        self.activity = pc

        # Button 1
        self.activity.button1 = ToolButton( "button1off" )
        self.activity.button1.set_tooltip(_('Button 1'))
        self.activity.button1.props.sensitive = True
        self.activity.button1.connect('clicked', self.activity._button1_cb)
        self.insert(self.activity.button1, -1)
        self.activity.button1.show()

        # Button 2
        self.activity.button2 = ToolButton( "button2on" )
        self.activity.button2.set_tooltip(_('Button 2'))
        self.activity.button2.props.sensitive = True
        self.activity.button2.connect('clicked', self.activity._button2_cb)
        self.insert(self.activity.button2, -1)
        self.activity.button2.show()

        separator = gtk.SeparatorToolItem()
        separator.set_draw(True)
        self.insert(separator, -1)
        separator.show()

        # Label for showing status
        self.activity.results_label = gtk.Label(\
            _("say something here"))
        self.activity.results_label.show()
        self.activity.results_toolitem = gtk.ToolItem()
        self.activity.results_toolitem.add(self.activity.results_label)
        self.insert(self.activity.results_toolitem, -1)
        self.activity.results_toolitem.show()
