import tkinter as tk
from tkinter import ttk


class TransparentText(tk.Text):
    def __init__(self, master, root, alpha=0.8, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.root = root  # Store reference to the root window
        self.alpha = alpha

        # Make the root window transparent
        self.root.attributes('-alpha', self.alpha)

        # Make the textbox transparent
        self.configure(bg='SystemButtonFace')  # Use system color
        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)

    def on_focus_in(self, event):
        self.root.attributes('-alpha', 1.0)

    def on_focus_out(self, event):
        self.root.attributes('-alpha', self.alpha)


# Create the main window
root = tk.Tk()
root.title("Transparent Textbox")
root.geometry("300x200")

# Create a frame to hold the textbox
frame = ttk.Frame(root)
frame.pack(expand=True, fill='both', padx=10, pady=10)

# Create the transparent textbox
text = TransparentText(frame, root, alpha=0.7, wrap='word', width=30, height=10)
text.pack(expand=True, fill='both')

# Insert some text
text.insert('1.0', "This is a transparent textbox. Type here...")

# Run the application
root.mainloop()