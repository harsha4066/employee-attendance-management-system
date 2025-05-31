import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import csv
from db import get_connection
import matplotlib.pyplot as plt


def open_admin_dashboard():
    global content_frame, app

    app = ctk.CTk()
    app.geometry("1400x700")
    app.title("Admin Dashboard")

    view_mode = tk.StringVar(value="attendance")

    def logout():
        app.destroy()
        import subprocess
        subprocess.Popen(["python", "main1.py"])

    def switch_view(mode):
        view_mode.set(mode)
        if mode == "attendance":
            show_todays_activity()
        elif mode == "details":
            show_employee_details()

    def download_employee_report():
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""
            SELECT u.first_name, u.last_name, u.email, a.check_in, a.check_out, a.work_hours
            FROM attendance a
            JOIN users u ON a.employee_id = u.id
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                                 title="Save Employee Report As")
        if file_path:
            with open(file_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["First Name", "Last Name", "Email", "Check-In", "Check-Out", "Hours Worked"])
                writer.writerows(data)

    def download_todays_report():
        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""
            SELECT CONCAT(u.first_name, ' ', u.last_name), a.check_in, a.check_out, a.work_hours
            FROM attendance a
            JOIN users u ON a.employee_id = u.id
            WHERE DATE(a.check_in) = CURDATE()
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                                 title="Save Today's Report As")
        if file_path:
            with open(file_path, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Employee Name", "Check-In", "Check-Out", "Hours Worked"])
                writer.writerows(data)

    def show_todays_activity():
        global content_frame
        for widget in content_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(content_frame, text="Today’s Activity", font=("Arial", 16, "bold"), text_color="black").pack(anchor="w")

        table_header = ctk.CTkFrame(content_frame, fg_color="#2563EB", height=40, width=1000)
        table_header.pack(pady=5)
        columns = ["Employee Name", "Check-In Time", "Check-Out Time", "Hours Worked"]
        for i, col in enumerate(columns):
            ctk.CTkLabel(table_header, text=col, font=("Arial", 13, "bold"), text_color="white").place(x=10 + i * 240, y=5)

        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""
            SELECT CONCAT(u.first_name, ' ', u.last_name), a.check_in, a.check_out, a.work_hours
            FROM attendance a
            JOIN users u ON a.employee_id = u.id
            WHERE DATE(a.check_in) = CURDATE()
            ORDER BY a.check_in DESC
        """)
        today_data = cursor.fetchall()
        cursor.close()
        conn.close()

        for row in today_data:
            row_frame = ctk.CTkFrame(content_frame, fg_color="#F9f9f9", height=35, width=1000)
            row_frame.pack(pady=2)
            for j, val in enumerate(row):
                ctk.CTkLabel(row_frame, text=str(val) if val else "-", font=("Arial", 10), text_color="black").place(x=15 + j * 240, y=5)

        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Download Full Report", command=download_employee_report, fg_color="#2563EB",
                      text_color="white", hover_color="#1E40AF", width=160).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Export Today's Report", command=download_todays_report, fg_color="#2563EB",
                      text_color="white", hover_color="#1E40AF", width=180).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="View Employee Graph", command=view_employee_graph, fg_color="#2563EB",
                      text_color="white", hover_color="#1E40AF", width=180).pack(side="left", padx=10)

    def view_employee_graph():
        last_name = simpledialog.askstring("Input", "Enter Employee Last Name:")
        email = simpledialog.askstring("Input", "Enter Employee Email:")

        if not last_name or not email:
            messagebox.showerror("Error", "Both Last Name and Email are required.")
            return

        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        query = """
            SELECT a.check_in, a.work_hours
            FROM attendance a
            JOIN users u ON a.employee_id = u.id
            WHERE u.last_name = %s AND u.email = %s
            ORDER BY a.check_in
        """
        cursor.execute(query, (last_name, email))
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        if not records:
            messagebox.showinfo("No Data", "No attendance records found for this employee.")
            return

        dates = [r[0].strftime("%Y-%m-%d") for r in records]
        hours = [float(r[1]) for r in records]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, hours, marker='o', color='blue')
        plt.title(f"Work Hours for {last_name}")
        plt.xlabel("Date")
        plt.ylabel("Hours Worked")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_employee_details():
        global content_frame
        for widget in content_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(content_frame, text="Employee Details", font=("Arial", 16, "bold"), text_color="black").pack(
            anchor="w", pady=(0, 5))

        search_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        search_frame.pack(pady=(0, 5), anchor="w")

        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by First or Last Name", width=300)
        search_entry.pack(side="left", padx=(0, 10))

        def search_employees():
            keyword = search_entry.get().lower()
            for widget in employee_list_inner_frame.winfo_children():
                widget.destroy()

            conn = get_connection()
            cursor = conn.cursor(buffered=True)
            query = """
                SELECT u.id, u.first_name, u.last_name, u.email, e.designation
                FROM users u
                JOIN employees e ON u.id = e.user_id
                WHERE LOWER(u.first_name) LIKE %s OR LOWER(u.last_name) LIKE %s
            """
            cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            employees = cursor.fetchall()
            conn.close()

            for emp in employees:
                create_employee_row(emp)

        ctk.CTkButton(search_frame, text="Search", command=search_employees, fg_color="#2563EB").pack(side="left")

        header = ctk.CTkFrame(content_frame, fg_color="#2563EB", height=40)
        header.pack(fill="x", pady=(5, 0))

        headers = ["ID", "First Name", "Last Name", "Email", "Designation", "Actions"]
        col_widths = [120, 120, 250, 150, 100, 200]

        x_position = 10
        for i, h in enumerate(headers):
            ctk.CTkLabel(header, text=h, font=("Arial", 13, "bold"), text_color="white").place(x=x_position, y=8)
            x_position += col_widths[i]

        employee_list_canvas = tk.Canvas(content_frame, height=400, width=1200, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=employee_list_canvas.yview)
        employee_list_scrollable_frame = ctk.CTkFrame(employee_list_canvas, fg_color="transparent")

        employee_list_scrollable_frame.bind(
            "<Configure>",
            lambda e: employee_list_canvas.configure(
                scrollregion=employee_list_canvas.bbox("all")
            )
        )

        employee_list_canvas.create_window((0, 0), window=employee_list_scrollable_frame, anchor="nw")
        employee_list_canvas.configure(yscrollcommand=scrollbar.set)

        employee_list_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        employee_list_inner_frame = employee_list_scrollable_frame

        def create_employee_row(emp):
            row_frame = ctk.CTkFrame(employee_list_inner_frame, fg_color="#F9f9f9", height=40, width=1200)
            row_frame.pack(pady=2, fill="x", padx=5)
            row_frame.pack_propagate(False)

            x_pos = 10
            values = [emp[0], emp[1], emp[2], emp[3], emp[4]]
            for j, val in enumerate(values):
                ctk.CTkLabel(row_frame, text=str(val), font=("Arial", 11), text_color="black").place(x=x_pos, y=8)
                x_pos += col_widths[j]

            ctk.CTkButton(row_frame, text="Update", command=lambda id=emp[0]: open_update_modal(id), width=50,
                          fg_color="#2563EB").place(x=x_pos, y=5)
            ctk.CTkButton(row_frame, text="inactive", command=lambda id=emp[0]: delete_employee(id), width=50,
                          fg_color="red").place(x=x_pos + 90, y=5)

        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("""
            SELECT u.id, u.first_name, u.last_name, u.email, e.designation
            FROM users u
            JOIN employees e ON u.id = e.user_id
        """)
        employees = cursor.fetchall()
        conn.close()

        for emp in employees:
            create_employee_row(emp)

    def delete_employee(user_id):
        confirm = messagebox.askyesno("Confirm", "Are you sure to delete?")
        if not confirm:
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM attendance WHERE employee_id = %s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "Employee deleted.")
            show_employee_details()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def open_update_modal(user_id):
        modal = ctk.CTkToplevel()
        modal.title("Update Employee")
        modal.geometry("400x400")

        conn = get_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT first_name, last_name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.execute("SELECT designation FROM employees WHERE user_id = %s", (user_id,))
        emp = cursor.fetchone()
        conn.close()

        first_name_entry = ctk.CTkEntry(modal, placeholder_text="First Name")
        first_name_entry.insert(0, user[0])
        first_name_entry.pack(pady=5)

        last_name_entry = ctk.CTkEntry(modal, placeholder_text="Last Name")
        last_name_entry.insert(0, user[1])
        last_name_entry.pack(pady=5)

        email_entry = ctk.CTkEntry(modal, placeholder_text="Email")
        email_entry.insert(0, user[2])
        email_entry.pack(pady=5)

        designation_entry = ctk.CTkEntry(modal, placeholder_text="Designation")
        designation_entry.insert(0, emp[0])
        designation_entry.pack(pady=5)

        def update_employee():
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET first_name=%s, last_name=%s, email=%s WHERE id=%s
            """, (first_name_entry.get(), last_name_entry.get(), email_entry.get(), user_id))
            cursor.execute("UPDATE employees SET designation=%s WHERE user_id=%s", (designation_entry.get(), user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Employee updated!")
            modal.destroy()
            show_employee_details()

        ctk.CTkButton(modal, text="Update", command=update_employee).pack(pady=15)

    nav = ctk.CTkFrame(app, height=60, fg_color="black")
    nav.pack(fill="x")

    ctk.CTkLabel(nav, text="Admin Dashboard", font=("Arial", 22, "bold"), text_color="white").place(x=30, y=15)
    ctk.CTkButton(nav, text="Employee Attendance", command=lambda: switch_view("attendance"), fg_color="transparent", text_color="white", hover_color="#333").place(x=800, y=15)
    ctk.CTkButton(nav, text="Employee Details", command=lambda: switch_view("details"), fg_color="transparent", text_color="white", hover_color="#333").place(x=970, y=15)
    ctk.CTkButton(nav, text="Logout", command=logout, fg_color="red", text_color="white").place(x=1140, y=15)

    card = ctk.CTkFrame(app, width=1000, height=170, corner_radius=15, fg_color="#F4F4F4")
    card.place(relx=0.5, y=150, anchor="center")

    content_frame = ctk.CTkFrame(app, width=1100, height=400, fg_color="transparent")
    content_frame.place(x=70, y=250)

    ctk.CTkLabel(card, text="Admin Overview", font=("Arial", 18, "bold"), text_color="black").place(x=30, y=10)

    box1 = ctk.CTkFrame(card, width=250, height=100, corner_radius=10)
    box1.place(x=30, y=50)
    ctk.CTkLabel(box1, text="Admin Info", font=("Arial", 14, "bold")).place(x=10, y=10)
    ctk.CTkLabel(box1, text="Name: Admin", font=("Arial", 12)).place(x=10, y=40)
    ctk.CTkLabel(box1, text="Department: HR", font=("Arial", 12)).place(x=10, y=65)

    conn = get_connection()
    cursor = conn.cursor(buffered=True)
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
    total_employees = cursor.fetchone()[0]

    box2 = ctk.CTkFrame(card, width=250, height=100, corner_radius=10)
    box2.place(x=310, y=50)
    ctk.CTkLabel(box2, text="Employees", font=("Arial", 14, "bold")).place(x=10, y=10)
    ctk.CTkLabel(box2, text=f"Total Employees: {total_employees}", font=("Arial", 12)).place(x=10, y=50)

    cursor.execute("SELECT COUNT(DISTINCT employee_id) FROM attendance WHERE DATE(check_in) = CURDATE()")
    present_today = cursor.fetchone()[0]

    box3 = ctk.CTkFrame(card, width=250, height=100, corner_radius=10)
    box3.place(x=590, y=50)
    ctk.CTkLabel(box3, text="Today's Attendance", font=("Arial", 14, "bold")).place(x=10, y=10)
    ctk.CTkLabel(box3, text=f"Employees Present: {present_today}", font=("Arial", 12)).place(x=10, y=50)

    cursor.close()
    conn.close()

    show_todays_activity()
    app.mainloop()
