
def source_label_helper(mode, dir, files_array_length):
    """Handles formatting and UI updates based on what mode we are in."""
    if mode == "files":
        return f"{files_array_length} files selected"
    elif mode == "folder":
        return dir
