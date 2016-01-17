#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Simple GTK+ script for Ubuntu Unity indicator menu.
#
# Looks for a file ~/.textlines that contains lines of text you often use.
# Shows the lines in an indicator menu. Clicking a line will insert it into 
# the clipboard, ready to Ctrl+P post.
#
# Based on https://github.com/tobyS/indicator-chars

import os
import re
import gtk
import gio
import signal
import subprocess
import appindicator

APP_NAME = 'textlines-indicator'
APP_VERSION = '0.2'

class TextLinesIndicator:
    CHARS_PATH = os.path.join(os.getenv('HOME'), '.textlines')
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        self.ind = appindicator.Indicator(
            "TextLines", os.path.join(self.SCRIPT_DIR, 'textlines16x16.png'),
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

        self.update_menu()

    def create_menu_item(self, label):
        item = gtk.MenuItem()
        item.set_label(label)
        return item

    def on_chars_changed(self, filemonitor, file, other_file, event_type):
        if event_type == gio.FILE_MONITOR_EVENT_CHANGES_DONE_HINT:
            print 'Textlines changed, updating menu...'
            self.update_menu()
    
    def update_menu(self, widget=None, data=None):
        try:
            charDef = open(self.CHARS_PATH).readlines()
        except IOError:
            charDef = []

        menu = gtk.Menu()
        
        for charLine in charDef:
            charLine = unicode(charLine)
            charLine = charLine.strip()
            parentItem = self.create_menu_item(charLine)
            parentItem.connect("activate", self.on_char_click, charLine)
            menu.append(parentItem)

        menu.append(gtk.SeparatorMenuItem())
        quit_item = self.create_menu_item('Quit')
        quit_item.connect("activate", self.on_quit)
        menu.append(quit_item)

        self.ind.set_menu(menu)
        menu.show_all()

    def on_char_click(self, widget, text):
        if text != None:
            cb = gtk.Clipboard()
            cb.set_text(text)

    def on_quit(self, widget):
        gtk.main_quit()

if __name__ == "__main__":
    # Catch CTRL-C
    signal.signal(signal.SIGINT, lambda signal, frame: gtk.main_quit())

    # Run the indicator
    i = TextLinesIndicator()
    
    # Monitor bookmarks changes 
    file = gio.File(i.CHARS_PATH)
    monitor = file.monitor_file()
    monitor.connect("changed", i.on_chars_changed)
    
    # Main gtk loop
    gtk.main()
