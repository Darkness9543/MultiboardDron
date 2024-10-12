import customtkinter as ctk


class ColorCircle(ctk.CTkFrame):
    def __init__(self, master, color, size=30, border_width=2, **kwargs):
        super().__init__(master, width=size, height=size, fg_color="transparent", **kwargs)
        self.size = size
        self.color = color
        self.border_width = border_width

        self.canvas = ctk.CTkCanvas(self, width=size, height=size, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_circle()

    def draw_circle(self):
        self.canvas.delete("all")  # Clear the canvas
        # Draw the outer circle (border)
        self.canvas.create_oval(
            self.border_width / 2,
            self.border_width / 2,
            self.size - self.border_width / 2,
            self.size - self.border_width / 2,
            outline="black",
            width=self.border_width,
            fill=""
        )
        # Draw the inner circle (filled color)
        self.canvas.create_oval(
            self.border_width,
            self.border_width,
            self.size - self.border_width,
            self.size - self.border_width,
            fill=self.color,
            outline=""
        )

    def set_color(self, color):
        self.color = color
        self.draw_circle()