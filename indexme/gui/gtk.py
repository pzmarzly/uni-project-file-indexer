import pathlib

import gi  # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

__all__ = ["Gtk"]
Gtk = Gtk


def load_xml(filename: str) -> Gtk.Builder:
    """
    Loads an Glade XML.
    Paths should be relative to this file.
    """
    root = pathlib.Path(__file__).parent
    builder = Gtk.Builder()
    builder.add_from_file(str(root / filename))
    return builder
