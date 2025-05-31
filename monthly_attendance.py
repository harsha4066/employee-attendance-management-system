import customtkinter as ctk
from tkinter import ttk
import datetime
from db import get_connection

def open_monthly_attendance(employee_id):
    app = ctk.CTk()
    app.title("Monthly Attendance Report")
    app.geometry("900x600")

    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT CONCAT(u.first_name, ' ', u.last_name) AS name, u.email 
            FROM users u 
            WHERE u.id = %s
        """, (employee_id,))
        user_data = cursor.fetchone()

        if user_data:
            ctk.CTkLabel(app, text=f"Employee: {user_data['name']}", font=("Helvetica", 20)).pack(pady=10)
            ctk.CTkLabel(app, text=f"Email: {user_data['email']}", font=("Helvetica", 16)).pack(pady=5)

        cursor.execute("""
            SELECT 
                DATE(check_in) as date,
                TIME(check_in) as check_in_time,
                TIME(check_out) as check_out_time,
                work_hours
            FROM attendance 
            WHERE employee_id = %s 
            AND MONTH(check_in) = %s AND YEAR(check_in) = %s
            ORDER BY check_in ASC
        """, (employee_id, current_month, current_year))
        attendance_data = cursor.fetchall()

        tree_frame = ctk.CTkFrame(app)
        tree_frame.pack(pady=20, padx=10, fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=("date", "check_in", "check_out", "work_hours"), show="headings")
        tree.heading("date", text="Date")
        tree.heading("check_in", text="Check-In")
        tree.heading("check_out", text="Check-Out")
        tree.heading("work_hours", text="Work Hours")

        total_hours = 0.0
        for row in attendance_data:
            tree.insert("", "end", values=(
                row["date"].strftime("%b %d, %Y"),
                row["check_in_time"],
                row["check_out_time"],
                row["work_hours"]
            ))
            total_hours += float(row["work_hours"] or 0)

        tree.pack(fill="both", expand=True)

        ctk.CTkLabel(app, text=f"Total Hours This Month: {total_hours:.2f} hrs", font=("Arial", 16, "bold")).pack(pady=10)

    except Exception as e:
        ctk.CTkLabel(app, text=f"Error: {str(e)}", text_color="red").pack(pady=20)
    finally:
        cursor.close()
        conn.close()

    app.mainloop()
