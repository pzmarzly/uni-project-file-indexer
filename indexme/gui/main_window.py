import os
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm.session import Session

from indexme.db.connection import connect
from indexme.db.file_model import File, format_bytes
from indexme.db.file_ops import FileSortDirection, GetAllFiles, get_file
from indexme.gui.gtk import Gtk, load_xml


class MainWindow:
    """
    Application's main window.
    """

    def __init__(self, root: str) -> None:
        self.builder = load_xml("main_window.glade")
        self.Session = connect()

        self.root = os.path.abspath(os.path.expanduser(root))
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
        self.search.connect("search-changed", lambda _this: self._search_changed())

    def show(self) -> None:
        """
        Displays the window.
        """
        self.window.show()

    def add_action(self, action: Callable[[str], Any]) -> None:
        """
        Attach action to non-expandable row activation.
        """
        self.actions.append(action)

    def _search_changed(self) -> None:
        text = self.search.get_text()
        self._clear_rows()
        if len(text) > 0:
            with self.Session() as s:
                for file in (
                    GetAllFiles(s, self.root)
                    .with_name(text)
                    .with_sorting(FileSortDirection("path"))
                    .limit(100)
                ):
                    self._add_row(s, file.path, file)

    def _clear_rows(self) -> None:
        self.store.clear()
        self.added_rows.clear()

    def _add_row(self, session: Session, path: str, file: Optional[File]) -> None:
        data = [path, os.path.basename(path), "", 0, "", 0, ""]
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
