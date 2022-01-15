import subprocess

import typer

from indexme.gui.gtk import Gtk
from indexme.gui.main_window import MainWindow

app = typer.Typer()


@app.command()
def gui(
    root: str = typer.Option("~", help="Where to start searching"),
    open: bool = typer.Option(
        True, help="Open file on selection instead of printing filename"
    ),
    exit: bool = typer.Option(False, help="Exit after selecting file"),
) -> None:
    window = MainWindow(root)

    if open:
        window.add_action(lambda path: subprocess.call(["xdg-open", path]))
    else:
        window.add_action(lambda path: print(path))

    if exit:
        window.add_action(lambda _path: Gtk.main_quit())

    window.show()
    Gtk.main()
