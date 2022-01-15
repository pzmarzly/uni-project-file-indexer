import subprocess
from typing import Any, Callable
import gi
import pathlib
import typer
from indexme.db.connection import connect

from indexme.db.file_ops import GetAllFiles

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

        self.store.clear()
        with self.Session() as s:
            for file in GetAllFiles(s, "/").with_name(text).limit(100):
                self.store.append(None, [file.path, file.name, str(file.size)])

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
