## Todo
[] create "save as" option, so that user can save the file with custom name
[x] add indefinite progress bad under the viewer, to indicate background task
[] create data view. A excel like view in a popup window, that shows the data of all the files that were compressed
[] change the listbox to a treeview, and show a check mark for the files that are already saved


create component classes, use this format

class ComponentName(ttk.Frame):
  def __init__(self, parent):
    super().__init__(parent)
    -- this is where you initialize the default values --
  create_widgets():
    -- this is where you create all the widgets --

  -- rest of the methods --

