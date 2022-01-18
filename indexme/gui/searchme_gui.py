import os
import subprocess
from typing import Optional

import typer

from indexme.gui.gtk import Gtk
from indexme.gui.main_window import MainWindow

app = typer.Typer()


@app.command()
def gui(
    root: str = typer.Argument("~", help="Where to start searching"),
    open: bool = typer.Option(
        True, "--open/--print", help="Open file on selection or printing path?"
    ),
    xargs: bool = typer.Option(False, help="Print xargs-readable NUL-sep. list"),
    exit: bool = typer.Option(False, help="Exit after selecting a file"),
    extension: Optional[str] = typer.Option(None, help="File extension"),
    executable: Optional[bool] = typer.Option(None, help="Search for executables?"),
    suid: Optional[bool] = typer.Option(None, help="Search for SUID bits?"),
    directories: Optional[bool] = typer.Option(None, help="Search for directories?"),
) -> None:
    """
    Opens a search window. Requires GTK.

    \b
    Examples:
      searchme-gui ~/Desktop
        Opens a search window in browser mode.
      searchme-gui ~ --print --exit | tr -d '\n' | xclip -selection clipboard
        Opens a search window. Upon selecting a file, path is copied to clipboard and program quits.
      searchme-gui --extension png --print --xargs | xargs -0 -L 1 xclip -selection clipboard -t image/png -i
        Interactively copies images to clipboard.
    """
    window = MainWindow(root)

    window.add_filter(
        lambda query: query.with_extension(extension)
        .with_executable_bit(executable)
        .with_suid_bit(suid)
        .with_directories_bit(directories)
    )

    if open:
        window.add_action(lambda path: subprocess.call(["xdg-open", path]))
    else:
        window.add_action(
            lambda path: print(
                os.path.relpath(path), end=("\0" if xargs else "\n"), flush=True
            )
        )

    if exit:
        window.add_action(lambda _path: Gtk.main_quit())

    window.show()
    Gtk.main()
