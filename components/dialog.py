import tkinter as tk

def show_info_dialog(parent, title_text, content_text):
    """Creates a custom modal popup dialog for Help or Shortcuts."""
    dialog = tk.Toplevel(parent)
    dialog.title(title_text)
    dialog.geometry("350x250")
    dialog.transient(parent)  # Keep on top of the main window
    dialog.grab_set()         # Make modal (locks interaction with main window)

    # Content Label / Text area
    label = tk.Label(dialog, text=content_text, justify="left", padx=20, pady=20, font=("Arial", 10))
    label.pack(fill="both", expand=True)

    # Close Button
    close_btn = tk.Button(dialog, text="Close", width=10, command=dialog.destroy)
    close_btn.pack(pady=10)

    # Center the dialog relative to the parent window
    dialog.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
