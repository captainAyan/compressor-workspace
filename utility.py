
def center_dialog(parent, dialog):
    dialog.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

def format_size(size_bytes):
    """Helper to convert bytes into human-readable string."""
    if not isinstance(size_bytes, (int, float)):
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
