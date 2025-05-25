import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime, timedelta

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="white")

        self.setup_ui()
        self.load_expenses()
        self.calculate_monthly_total()

    def setup_ui(self):
        title = tk.Label(self.root, text="Expense Tracker", font=("Helvetica", 20, "bold"), bg="white", fg="#333")
        title.pack(pady=10)

        form_frame = tk.Frame(self.root, bg="white")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Amount:", bg="white", fg="#333").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Category:", bg="white", fg="#333").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, values=["Food", "Transport", "Entertainment", "Bills", "Other"])
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.check_other_category)

        tk.Label(form_frame, text="Description (optional):", bg="white", fg="#333").grid(row=1, column=0, padx=5, pady=5)
        self.description_entry = tk.Entry(form_frame)
        self.description_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        tk.Label(form_frame, text="Date (YYYY-MM-DD):", bg="white", fg="#333").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(form_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        add_button = tk.Button(self.root, text="Add Expense", command=self.add_expense, bg="#4CAF50", fg="white")
        add_button.pack(pady=10)

        refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_table, bg="#2196F3", fg="white")
        refresh_button.pack(pady=5)

        self.tree = ttk.Treeview(self.root, columns=("Amount", "Category", "Description", "Date"), show="headings")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Date", text="Date")
        self.tree.pack(fill="both", expand=True)

        delete_button = tk.Button(self.root, text="Delete Selected", command=self.delete_expense, bg="#f44336", fg="white")
        delete_button.pack(pady=10)

    def check_other_category(self, event):
        if self.category_var.get() == "Other":
            other = tk.simpledialog.askstring("Other Category", "Please enter the category:")
            if other:
                self.category_var.set(other)

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()
        date = self.date_entry.get()

        if not amount or not category:
            messagebox.showerror("Input Error", "Amount and category are required!")
            return

        with open("expenses.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if os.path.getsize("expenses.csv") == 0:
                writer.writerow(["Amount", "Category", "Description", "Date"])
            writer.writerow([amount, category, description, date])

        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.refresh_table()
        self.calculate_monthly_total()

    def load_expenses(self):
        if not os.path.exists("expenses.csv"):
            return
        with open("expenses.csv", "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                self.tree.insert("", tk.END, values=row)

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.load_expenses()
        self.calculate_monthly_total()

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "Please select an entry to delete.")
            return

        values_to_delete = [self.tree.item(item)["values"] for item in selected]
        self.tree.delete(*selected)

        with open("expenses.csv", "r", newline="") as file:
            reader = list(csv.reader(file))
            header, data = reader[0], reader[1:]

        new_data = []
        for row in data:
            if row not in [list(map(str, v)) for v in values_to_delete]:
                new_data.append(row)

        with open("expenses.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(new_data)

    def is_last_day_of_month(self, date):
        next_day = date + timedelta(days=1)
        return next_day.month != date.month

    def calculate_monthly_total(self):
        today = datetime.now()
        if self.is_last_day_of_month(today):
            current_month = today.strftime("%Y-%m")
            total = 0
            if os.path.exists("expenses.csv"):
                with open("expenses.csv", "r") as file:
                    reader = csv.reader(file)
                    next(reader, None)
                    for row in reader:
                        date_str, amount = row[3], row[0]
                        if date_str.startswith(current_month):
                            total += float(amount)
            messagebox.showinfo("Monthly Total", f"Total expenses for {current_month}: ₹{total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
