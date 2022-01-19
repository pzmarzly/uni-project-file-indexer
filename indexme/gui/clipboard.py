import subprocess


def copy_path_to_clipboard(path: str) -> None:
    subprocess.run(
        ["xclip", "-selection", "clipboard"],
        input=path.encode(),
    )


def copy_file_to_clipboard(path: str) -> None:
    subprocess.run(
        ["xclip", "-selection", "clipboard", "-t", "text/uri-list"],
        input=f"file://{path}".encode(),
    )
