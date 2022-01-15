import os
import pathlib
import subprocess
from typing import Any, Callable, Dict, List, Optional

import gi  # type: ignore
import typer
from sqlalchemy.orm.session import Session

from indexme.db.connection import connect
from indexme.db.file_model import File, format_bytes
from indexme.db.file_ops import GetAllFiles, get_file

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore

app = typer.Typer()


def load_xml(file: str) -> Gtk.Builder:
    root = pathlib.Path(__file__).parent
    builder = Gtk.Builder()
    builder.add_from_file(str(root / file))
    return builder


class MainWindow:
    def __init__(self) -> None:
        self.builder = load_xml("main_window.glade")
        self.Session = connect()

        self.root = os.path.abspath(str(pathlib.Path.home()))
        self.added_rows: Dict[str, Gtk.TreeRow] = dict()
        self.actions: List[Callable[[str], Any]] = []

        self.window = self.builder.get_object("window")
        self.window.connect("destroy", Gtk.main_quit)

        self.store = self.builder.get_object("store")
        self.tree_view = self.builder.get_object("treeview")
        self.tree_view.connect(
            "row-activated", lambda _this, _num, _col: self._row_activated()
        )

        self.search = self.builder.get_object("search")
        self.search.connect("search-changed", lambda _this: self._update_search())

    def show(self) -> None:
        self.window.show()

    def add_action(self, action: Callable[[str], Any]) -> None:
        self.actions.append(action)

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
        data = [path, "", "", 0, "", 0, ""]
        if file is not None:
            size = "dir" if file.is_dir else format_bytes(file.size)
            created_at = int(file.created_at.timestamp()), str(file.created_at)
            modified_at = int(file.modified_at.timestamp()), str(file.modified_at)
            data = [file.path, file.name, size, *created_at, *modified_at]

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
        store, iter = self.tree_view.get_selection().get_selected()
        if iter is None:
            return

        if store.iter_has_child(iter):
            tree_path = store.get_path(iter)
            if self.tree_view.row_expanded(tree_path):
                self.tree_view.collapse_row(tree_path)
            else:
                self.tree_view.expand_row(tree_path, False)
        else:
            path = store[iter][0]
            for action in self.actions:
                action(path)


@app.command()
def gui(
    open: bool = typer.Option(
        True, help="Open file on selection instead of printing filename"
    ),
    exit: bool = typer.Option(False, help="Exit after selecting file"),
) -> None:
    window = MainWindow()

    if open:
        window.add_action(lambda path: subprocess.call(["xdg-open", path]))
    else:
        window.add_action(lambda path: print(path))

    if exit:
        window.add_action(lambda _path: Gtk.main_quit())

    window.show()
    Gtk.main()
