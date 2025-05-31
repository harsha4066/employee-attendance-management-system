import customtkinter as ctk
from tkinter import messagebox, Label
from db import get_connection
from PIL import Image, ImageTk

def open_register_window():
    def register_user():
        role = role_dropdown.get().lower()
        data = (
            first_name_entry.get(),
            last_name_entry.get(),
            email_entry.get(),
            password_entry.get(),
            role,
            designation_entry.get()
        )

        if not all(data):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor(buffered=True)

            cursor.execute("INSERT INTO users (first_name, last_name, email, password, role) VALUES (%s, %s, %s, %s, %s)", data[:5])
            user_id = cursor.lastrowid
            if role == "employee":
                cursor.execute("INSERT INTO employees (user_id, designation) VALUES (%s, %s)", (user_id, data[5]))
            else:
                cursor.execute("INSERT INTO admins (user_id, department) VALUES (%s, %s)", (user_id, data[5]))

            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            window.destroy()
            __import__("main1").open_login_window()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

    window = ctk.CTk()
    window.title("Register")
    window.geometry("800x500")

    left = ctk.CTkFrame(window, width=400, fg_color="#0A57F4")
    left.pack(side="left", fill="both")
    image_location = Image.open(r"C:\Users\Harsha\PycharmProjects\pythonProject4\Images\4894766.jpg")
    resized_image = image_location.resize((500, 650))
    img = ImageTk.PhotoImage(resized_image)
    Label(left, image=img).place(x=0, y=0)

    right = ctk.CTkFrame(window, width=400, fg_color="#0A57F4")
    right.pack(side="right", fill="both")

    # Load icons
    user_icon = ctk.CTkImage(Image.open(r"C:\Users\Harsha\PycharmProjects\pythonProject4\Images\user.png"), size=(25, 25))
    email_icon = ctk.CTkImage(Image.open(r"C:\Users\Harsha\PycharmProjects\pythonProject4\Images\icons8-email-30.png"), size=(25, 25))
    lock_icon = ctk.CTkImage(Image.open(r"C:\Users\Harsha\PycharmProjects\pythonProject4\Images\icons8-lock-50.png"), size=(25, 25))
    designation_icon = ctk.CTkImage(Image.open(r"C:\Users\Harsha\PycharmProjects\pythonProject4\Images\icons8-designation-64.png"), size=(25, 25))

    # Role Dropdown
    role_dropdown = ctk.CTkOptionMenu(right, values=["Employee", "Admin"], width=250)
    role_dropdown.set("Employee")
    role_dropdown.place(relx=0.5, rely=0.1, anchor="center")

    # Helper function to create field with icon + entry
    def create_field(y_pos, icon, placeholder_text, show_text=""):
        frame = ctk.CTkFrame(right, fg_color="transparent")
        frame.place(relx=0.5, rely=y_pos, anchor="center")

        ctk.CTkLabel(frame, image=icon, text="").pack(side="left", padx=5)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder_text, show=show_text, width=220)
        entry.pack(side="left")
        return entry

    # First name
    first_name_entry = create_field(0.2, user_icon, "First Name")

    # Last name
    last_name_entry = create_field(0.28, user_icon, "Last Name")

    # Email
    email_entry = create_field(0.36, email_icon, "Email")

    # Password
    password_entry = create_field(0.44, lock_icon, "Password", show_text="*")

    # Designation
    designation_entry = create_field(0.52, designation_icon, "Designation/Department")

    # Register and Back buttons
    ctk.CTkButton(right, text="Register", width=250, command=register_user).place(relx=0.5, rely=0.62, anchor="center")
    ctk.CTkButton(right, text="Back", width=250, command=lambda: [window.destroy(), __import__("main1").open_login_window()]).place(relx=0.5, rely=0.72, anchor="center")

    window.mainloop()
