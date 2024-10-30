import customtkinter as ctk


class ConfirmationPopup(ctk.CTkToplevel):
    def __init__(self, master, message="Are you sure?", title="Confirmation"):
        super().__init__(master)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)

        # Make the popup modal
        self.grab_set()
        self.focus_set()

        # Initialize return value
        self.result = False

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Message Label
        self.label = ctk.CTkLabel(self, text=message, wraplength=280, justify="center")
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # Button Frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, pady=(0, 20))

        # Yes Button
        self.yes_button = ctk.CTkButton(self.button_frame, text="Yes", command=self.on_yes)
        self.yes_button.pack(side="left", padx=(0, 10))

        # No Button
        self.no_button = ctk.CTkButton(self.button_frame, text="No", command=self.on_no)
        self.no_button.pack(side="left")

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()