import customtkinter as ctk
import tkinter as tk


class RepeatingButton(ctk.CTkButton):
    def __init__(self, master, command, text, fg_color, width=40, height=40, repeat_delay=200, **kwargs):
        """
        A CustomTkinter button that repeats a command while being held down.

        :param master: Parent widget.
        :param command: Function to execute repeatedly.
        :param repeat_delay: Delay in milliseconds between command executions.
        :param kwargs: Additional keyword arguments for CTkButton.
        """
        super().__init__(master, **kwargs)
        self.command = command
        self.configure(text=text,
                       text_color="black",
                       fg_color=fg_color,
                       width=width,
                       height=height)
        self.repeat_delay = repeat_delay  # milliseconds
        self.is_pressing = False
        self.after_id = None

        # Bind press and release events
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        if not self.is_pressing:
            self.is_pressing = True
            self.execute_command()
            self.schedule_repeat()

    def on_release(self, event):
        self.is_pressing = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    def execute_command(self):
        """Execute the assigned command."""
        if callable(self.command):
            self.command()

    def schedule_repeat(self):
        """Schedule the next command execution."""
        if self.is_pressing:
            self.after_id = self.after(self.repeat_delay, self.repeat_command)

    def repeat_command(self):
        """Execute command and reschedule if still pressing."""
        if self.is_pressing:
            self.execute_command()
            self.schedule_repeat()
