import tkinter as tk
from tkinter import Frame

class AttendancePage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Employee Attendance", font=("Arial", 20)).pack(pady=20)
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack()
