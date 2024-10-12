import customtkinter as ctk


class DroneStatusIndicator(ctk.CTkFrame):
    def __init__(self, root,
                 position=None,
                 text_color: str = "white",
                 font: tuple = ("Helvetica", 15, "bold"),
                 padx: int = 10,
                 pady: tuple[int, int] = (5, 5),
                 width: int = 20,
                 height: int = 20):
        super().__init__(master=root)

        if position is None:
            position = [125, 40]
        self.root = root
        self.position = position
        self.text_color = text_color
        self.font = font
        self.padx = padx
        self.pady = pady
        self.width = width
        self.height = height
        self.configure(fg_color="transparent")
        self.place(x=self.position[0], y=self.position[1])

        # Create the circle indicator
        self.circle = ctk.CTkLabel(self, width=self.width, height=self.height,
                                   text="", corner_radius=int(self.width / 2), fg_color="red")
        self.circle.pack(padx=self.padx, pady=self.pady)

        # Initial state
        self.state = "Disconnected"
        self.blinking = False
        self.blink_state = False

        # Set color according to state
        self.update_circle()

        # Bind hover events for tooltip
        self.circle.bind("<Enter>", self.show_tooltip)
        self.circle.bind("<Leave>", self.hide_tooltip)
        self.tooltip = None

    def update_circle(self):
        # Stop blinking before updating state
        self.blinking = False

        # Update the circle color and blinking behavior based on the state
        if self.state == "Disconnected":
            self.circle.configure(fg_color="red")
        elif self.state == "Connecting":
            self.blink_color = "orange"
            self.blinking = True
            self.blink()
        elif self.state == "Setting geofence":
            self.blink_color = "blue"
            self.blinking = True
            self.blink()
        elif self.state == "Retrieving parameters":
            self.blink_color = "yellow"
            self.blinking = True
            self.blink()
        elif self.state == "Connected":
            self.circle.configure(fg_color="green")
        else:
            # Default to red if state is unknown
            self.circle.configure(fg_color="red")

    def blink(self):
        if self.blinking:
            # Toggle the blink state
            if self.blink_state:
                self.circle.configure(fg_color=self.blink_color)
            else:
                self.circle.configure(fg_color="transparent")
            self.blink_state = not self.blink_state
            # Call this method again after 500 milliseconds
            self.after(500, self.blink)

    def show_tooltip(self, event):
        if self.tooltip:
            return
        # Get the position of the circle
        x = self.circle.winfo_rootx() + self.circle.winfo_width() // 2
        y = self.circle.winfo_rooty() - 30  # Position tooltip above the circle

        # Create a Toplevel window for the tooltip
        self.tooltip = ctk.CTkToplevel(self, fg_color="#303030")
        self.tooltip.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip.geometry(f"+{x}+{y}")
        # Create a label inside the tooltip window
        tooltip_label = ctk.CTkLabel(self.tooltip, text=self.state, text_color=self.text_color, font=self.font, padx=3, pady=3)
        tooltip_label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def set_state(self, new_state):
        self.state = new_state
        self.update_circle()
