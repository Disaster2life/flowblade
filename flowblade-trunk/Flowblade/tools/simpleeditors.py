"""
    Flowblade Movie Editor is a nonlinear video editor.
    Copyright 2012 Janne Liljeblad.

    This file is part of Flowblade Movie Editor <http://code.google.com/p/flowblade>.

    Flowblade Movie Editor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Flowblade Movie Editor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Flowblade Movie Editor. If not, see <http://www.gnu.org/licenses/>.
"""

"""
Module for creating simple editors for e.g. container clips program data.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository import GObject

import dialogutils
import gui
import guiutils


SIMPLE_EDITOR_TEXT = 0
SIMPLE_EDITOR_FLOAT = 1
SIMPLE_EDITOR_INT = 2
SIMPLE_EDITOR_COLOR = 3

SIMPLE_EDITOR_LEFT_WIDTH = 150


def show_blender_container_clip_program_editor(callback, blender_objects):
    # Create panels for objects
    panels = []
    editors = []
    for obj in blender_objects:
        # object is [name, type, editors_list] see blenderprojectinit.py
        editors_data_list = obj[2]
        editors_panel = Gtk.VBox(True, 2)
        for editor_data in editors_data_list:
            prop_path, label_text, tooltip, editor_type, value = editor_data
            editor_type = int(editor_type)
            editor = get_editor(editor_type, (obj[0], prop_path), label_text, value)
            if editor_type == SIMPLE_EDITOR_TEXT:
                editor.return_quoted_string = True # we are calling exec() using these values and adding the needed quptes is best handled here.
            editor.blender_editor_data = editor_data # We need this the later to apply the changes.
            editors.append(editor)
            
            editors_panel.pack_start(editor, False, False, 0)

        if len(editors_data_list) > 0:
            panel = guiutils.get_named_frame(obj[0] + " - " + obj[1], editors_panel)
            panels.append(panel)
        
    # Create and show dialog
    dialog = Gtk.Dialog(_("Blender Project Edit"), gui.editor_window.window,
                        Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        (_("Cancel"), Gtk.ResponseType.REJECT,
                         _("Save Changes"), Gtk.ResponseType.ACCEPT))

    pane = Gtk.VBox(False, 2)
    for panel in panels:
        pane.pack_start(panel, False, False, 0)

    alignment = dialogutils.get_default_alignment(pane)
    dialogutils.set_outer_margins(dialog.vbox)
    dialog.vbox.pack_start(alignment, True, True, 0)

    dialog.set_default_response(Gtk.ResponseType.REJECT)
    dialog.set_resizable(False)
    dialog.connect('response', callback, editors)
    dialog.show_all()


# ----------------------------------------------------------------------- editors
def get_editor(editor_type, id_data, label_text, value):
    if editor_type == SIMPLE_EDITOR_TEXT:
        return TextEditor(id_data, label_text, value)


class AbstractSimpleEditor(Gtk.HBox):
    
    def __init__(self, id_data):
        GObject.GObject.__init__(self)
        self.id_data = id_data # the data needed to target edited values on correct object.
        
    def build_editor(self, label_text, widget):
        left_box = guiutils.get_left_justified_box([Gtk.Label(label=label_text)])
        left_box.set_size_request(SIMPLE_EDITOR_LEFT_WIDTH, guiutils.TWO_COLUMN_BOX_HEIGHT)
        self.pack_start(left_box, False, True, 0)
        self.pack_start(widget, True, True, 0)


class TextEditor(AbstractSimpleEditor):

    def __init__(self, id_data, label_text, value):
        AbstractSimpleEditor.__init__(self, id_data)
        
        self.return_quoted_string = False # This is set elsewhere if needed
        
        # If input value has quotes we need to strip them before editing
        # and put back when value is asked for.
        if value[0:1] == '"':
            value = value[1:len(value) - 1]

        self.entry = Gtk.Entry()
        self.entry.set_text(value)
        
        self.build_editor(label_text, self.entry)

    def get_value(self):
        value = self.entry.get_text()
        if self.return_quoted_string == True:
            return '"' + self.entry.get_text()  + '"'
        else:
            return self.value



    