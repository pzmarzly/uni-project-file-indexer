import subprocess


def copy_path_to_clipboard(path: str) -> None:
    """
    Copies path as text.
    This could probably be merged with copy_file_to_clipboard
    using Gtk.Clipboard.
    """
    subprocess.run(
        ["xclip", "-selection", "clipboard"],
        input=path.encode(),
    )


def copy_file_to_clipboard(path: str) -> None:
    """
    Copies path as uri-list.
    """
    subprocess.run(
        ["xclip", "-selection", "clipboard", "-t", "text/uri-list"],
        input=f"file://{path}".encode(),
    )
