import subprocess
from typing import Any, Callable, Optional
import gi
import pathlib
import typer
import os
import pathlib

from sqlalchemy.orm.session import Session
from indexme.db.connection import connect
from indexme.db.file_ops import GetAllFiles, get_file
from indexme.db.file_model import File, format_bytes

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

app = typer.Typer()


def load_xml(file: str) -> Gtk.Builder:
    root = pathlib.Path(__file__).parent
    builder = Gtk.Builder()
    builder.add_from_file(str(root / file))
    return builder


class MainWindow:
    def __init__(self):
        self.builder = load_xml("main_window.glade")
        self.Session = connect()
        self.root = os.path.abspath(str(pathlib.Path.home()))
        self.added_rows = dict()

        self.window = self.builder.get_object("window")
        self.window.connect("destroy", Gtk.main_quit)

        self.store = self.builder.get_object("store")
        self.treeview = self.builder.get_object("treeview")
        self.treeview.connect(
            "row-activated", lambda _this, _num, _col: self._row_activated()
        )

        self.search = self.builder.get_object("search")
        self.search.connect("search-changed", lambda _this: self._update_search())

    def show(self) -> None:
        self.window.show()

    def set_action(self, action: Callable[[str], Any]) -> None:
        self.action = action

    def _update_search(self) -> None:
        text = self.search.get_text()
        self._clear_rows()
        with self.Session() as s:
            for file in GetAllFiles(s, self.root).with_name(text).limit(100):
                self._add_row(s, file.path, file)

    def _clear_rows(self) -> None:
        self.store.clear()
        self.added_rows.clear()

    def _add_row(self, session: Session, path: str, file: Optional[File]) -> None:
        data = [path, "", ""]
        if file is not None:
            size = "dir" if file.is_dir else format_bytes(file.size)
            data = [file.path, file.name, size]

        parent_path = os.path.dirname(path)
        parent = None
        if parent_path != self.root:
            if parent_path not in self.added_rows:
                parent_file = get_file(session, parent_path)
                self._add_row(session, parent_path, parent_file)
            parent = self.added_rows[parent_path]

        row = self.store.append(parent, data)
        self.added_rows[path] = row

    def _row_activated(self) -> None:
        store, iter = self.treeview.get_selection().get_selected()
        if iter is None:
            return
        path = store[iter][0]
        if self.action is not None:
            self.action(path)


@app.command()
def gui(
    open: bool = typer.Option(
        True, help="Open file on selection instead of printing filename"
    )
) -> None:
    window = MainWindow()

    if open:
        window.set_action(lambda path: subprocess.call(["xdg-open", path]))
    else:
        window.set_action(lambda path: print(path))

    window.show()
    Gtk.main()
