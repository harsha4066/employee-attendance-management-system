import customtkinter as ctk
from db import get_connection
from datetime import date
from navigator import return_to_login
from monthly_attendance import open_monthly_attendance

def open_employee_dashboard(user_id):
    def get_employee_data():
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT first_name, last_name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.execute("SELECT designation FROM employees WHERE user_id = %s", (user_id,))
        designation = cursor.fetchone()
        cursor.execute("""
            SELECT check_in, check_out, work_hours FROM attendance
            WHERE employee_id = %s AND DATE(check_in) = CURDATE()
        """, (user_id,))
        today = cursor.fetchone()
        cursor.execute("""
            SELECT SUM(work_hours) FROM attendance
            WHERE employee_id = %s AND MONTH(check_in) = MONTH(CURDATE()) AND YEAR(check_in) = YEAR(CURDATE())
        """, (user_id,))
        total = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()
        return user, designation, today, total

    def check_in():
        try:
            conn = get_connection()
            cursor = conn.cursor(buffered=True)
            cursor.execute("INSERT INTO attendance (employee_id) VALUES (%s)", (user_id,))
            conn.commit()
            refresh_info()
            show_past_attendance()
            status_label.configure(text="Checked in successfully.")
        except Exception as e:
            status_label.configure(text=str(e))
        finally:
            cursor.close()
            conn.close()

    def check_out():
        try:
            conn = get_connection()
            cursor = conn.cursor(buffered=True)
            cursor.execute("""
                UPDATE attendance SET check_out = NOW()
                WHERE employee_id = %s AND check_out IS NULL
            """, (user_id,))
            conn.commit()
            refresh_info()
            show_past_attendance()
            status_label.configure(text="Checked out successfully.")
        except Exception as e:
            status_label.configure(text=str(e))
        finally:
            cursor.close()
            conn.close()

    def refresh_info():
        user, designation, today, total = get_employee_data()
        name_label.configure(text=f"Name: {user[0]} {user[1]}")
        designation_label.configure(text=f"Designation: {designation[0] if designation else 'N/A'}")
        date_label.configure(text=f"Today's date: {date.today().strftime('%m/%d/%Y')}")
        if today:
            checkin_label.configure(text=f"Check-In: {today[0].strftime('%H:%M:%S')}")
            checkout_label.configure(text=f"Check-Out: {today[1].strftime('%H:%M:%S') if today[1] else '—'}")
            hours_label.configure(text=f"Hours: {today[2] if today[2] else 0}")
        else:
            checkin_label.configure(text="Check-In: ———")
            checkout_label.configure(text="Check-Out: ———")
            hours_label.configure(text="Hours: —")
        total_hours_label.configure(text=f"Total Work Hours: {total}")

    def show_past_attendance():
        for widget in history_frame.winfo_children():
            widget.destroy()
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""
            SELECT DATE(check_in), TIME(check_in), TIME(check_out), work_hours
            FROM attendance
            WHERE employee_id = %s
            ORDER BY check_in DESC
            LIMIT 20
        """, (user_id,))
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        headers = ["Date", "Check-In", "Check-Out", "Hours"]
        for i, col in enumerate(headers):
            header = ctk.CTkLabel(history_frame, text=col, font=("Arial", 13, "bold"), text_color="white", fg_color="#2563EB", width=130)
            header.grid(row=0, column=i, padx=1, pady=2)

        for r_idx, row in enumerate(records):
            for c_idx, value in enumerate(row):
                cell = ctk.CTkLabel(history_frame, text=str(value), font=("Arial", 12), fg_color="#F4F4F4", width=130)
                cell.grid(row=r_idx+1, column=c_idx, padx=1, pady=1)

    def logout():
        app.destroy()
        import subprocess
        subprocess.Popen(["python", "main1.py"])

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.geometry("1250x750")
    app.title("Employee Dashboard")

    nav = ctk.CTkFrame(app, height=60, fg_color="black")
    nav.pack(fill="x")
    ctk.CTkLabel(nav, text="Employee Dashboard", font=("Arial", 22, "bold"), text_color="white").place(x=30, y=15)
    ctk.CTkButton(nav, text="View Monthly Attendance", command=lambda: open_monthly_attendance(user_id), width=200).place(x=860, y=15)
    ctk.CTkButton(nav, text="Logout", fg_color="red", text_color="white", width=80, command=logout).place(x=1080, y=15)

    card = ctk.CTkFrame(app, width=800, height=350, corner_radius=15)
    card.place(x=250, y=80)

    ctk.CTkLabel(card, text="Check-In & Check-Out", font=("Arial", 16, "bold")).place(x=60, y=30)
    ctk.CTkButton(card, text="Check-In", fg_color="#2563EB", width=200, height=45, font=("Arial", 14, "bold"), command=check_in).place(x=60, y=80)
    ctk.CTkButton(card, text="Check-Out", fg_color="#EF4444", width=200, height=45, font=("Arial", 14, "bold"), command=check_out).place(x=60, y=140)

    ctk.CTkLabel(card, text="Employee Info", font=("Arial", 16, "bold")).place(x=460, y=30)
    name_label = ctk.CTkLabel(card, text="Name:", font=("Arial", 13))
    name_label.place(x=460, y=70)
    designation_label = ctk.CTkLabel(card, text="Designation:", font=("Arial", 13))
    designation_label.place(x=460, y=95)
    date_label = ctk.CTkLabel(card, text="Today's date:", font=("Arial", 13))
    date_label.place(x=460, y=120)

    ctk.CTkLabel(card, text="Today’s Attendance:", font=("Arial", 13, "bold")).place(x=460, y=150)
    checkin_label = ctk.CTkLabel(card, text="Check-In: ——", font=("Arial", 13))
    checkin_label.place(x=460, y=180)
    checkout_label = ctk.CTkLabel(card, text="Check-Out: ——", font=("Arial", 13))
    checkout_label.place(x=460, y=200)
    hours_label = ctk.CTkLabel(card, text="Hours: ——", font=("Arial", 13))
    hours_label.place(x=460, y=220)

    total_hours_label = ctk.CTkLabel(card, text="Total Work Hours:", font=("Arial", 13, "bold"))
    total_hours_label.place(x=460, y=265)

    status_label = ctk.CTkLabel(app, text="", font=("Arial", 12), text_color="green")
    status_label.place(relx=0.5, rely=0.935, anchor="center")

    ctk.CTkLabel(app, text="Past Attendance Records", font=("Arial", 18, "bold")).place(x=300, y=430)
    global history_frame
    history_frame = ctk.CTkFrame(app, width=600, height=200, corner_radius=10)
    history_frame.place(x=300, y=460)

    refresh_info()
    show_past_attendance()
    app.mainloop()
