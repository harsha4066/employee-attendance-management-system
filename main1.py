import customtkinter as ctk
from tkinter import messagebox, Label
from db import get_connection
from register import open_register_window
from admin_dashboard import open_admin_dashboard
from PIL import Image, ImageTk

def login_user():
    from employee_dashboard import open_employee_dashboard
    email = email_entry.get()
    password = password_entry.get()
    role = role_dropdown.get().lower()

    try:
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s AND role=%s", (email, password, role))
        result = cursor.fetchone()
        if result:
            messagebox.showinfo("Success", f"Welcome {role.capitalize()}!")
            app.destroy()
            if role == "admin":
                open_admin_dashboard()
            else:
                open_employee_dashboard(result[0])
        else:
            messagebox.showerror("Error", "Invalid credentials.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()

def open_login_window():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    global app, email_entry, password_entry, role_dropdown
    app = ctk.CTk()
    app.geometry("800x500")
    app.title("Login")

    left = ctk.CTkFrame(app, width=400)
    left.pack(side="left", fill="both")
    right = ctk.CTkFrame(app, width=400, fg_color="#0A57F4")
    right.pack(side="right", fill="both")

    # Load icons
    user_icon = ctk.CTkImage(Image.open(r"C:\Users\Harsha\PycharmProjects\pythonProject4\Images\user.png"), size=(20, 20))
    password_icon = ctk.CTkImage(Image.open(r"C:\Users\Harsha\PycharmProjects\pythonProject4\Images\icons8-password-50.png"), size=(20, 20))

    # Role Dropdown
    role_dropdown = ctk.CTkOptionMenu(left, values=["Employee", "Admin"])
    role_dropdown.set("Employee")
    role_dropdown.place(relx=0.5, rely=0.25, anchor="center")

    # Email Frame (Icon + Entry together)
    email_frame = ctk.CTkFrame(left, fg_color="transparent")  # transparent frame
    email_frame.place(relx=0.5, rely=0.35, anchor="center")

    ctk.CTkLabel(email_frame, image=user_icon, text="").pack(side="left", padx=5)
    email_entry = ctk.CTkEntry(email_frame, placeholder_text="Email", width=200)
    email_entry.pack(side="left")

    # Password Frame (Icon + Entry together)
    password_frame = ctk.CTkFrame(left, fg_color="transparent")
    password_frame.place(relx=0.5, rely=0.45, anchor="center")

    ctk.CTkLabel(password_frame, image=password_icon, text="").pack(side="left", padx=5)
    password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*", width=200)
    password_entry.pack(side="left")

    # Show Password Checkbox
    def toggle_password_visibility():
        if show_password_var.get():
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")

    show_password_var = ctk.BooleanVar()
    show_password_checkbox = ctk.CTkCheckBox(left, text="Show Password", variable=show_password_var, command=toggle_password_visibility)
    show_password_checkbox.place(relx=0.5, rely=0.53, anchor="center")

    # Login Button
    ctk.CTkButton(left, text="Login", command=login_user).place(relx=0.5, rely=0.6, anchor="center")

    # Footer
    ctk.CTkLabel(left, text="© American Developer 2025", text_color="blue").place(relx=0.5, rely=0.7, anchor="center")

    # Right Panel Texts
    ctk.CTkLabel(right, text="Employee Attendance\nManagement System", font=("Helvetica", 20, "bold"),
                text_color="white", justify="center").place(relx=0.5, rely=0.3, anchor="center")

    ctk.CTkLabel(right, text="New Here?", font=("Arial", 14, "bold"), text_color="white").place(relx=0.5, rely=0.45, anchor="center")
    ctk.CTkLabel(right, text="Please Register yourself first", text_color="white").place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkButton(right, text="Register", command=lambda: [app.destroy(), open_register_window()]).place(relx=0.5, rely=0.57, anchor="center")

    app.mainloop()

if __name__ == "__main__":
    open_login_window()
