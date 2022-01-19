import pathlib

import gi  # type: ignore

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # type: ignore

Gtk, Gdk = Gtk, Gdk
__all__ = ["Gtk", "Gdk", "load_glade"]


def load_glade(filename: str) -> Gtk.Builder:
    """
    Loads an Glade XML.
    Paths should be relative to this file.
    """
    root = pathlib.Path(__file__).parent
    builder = Gtk.Builder()
    builder.add_from_file(str(root / filename))
    return builder
