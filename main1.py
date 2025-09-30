import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox, simpledialog, filedialog
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import csv
from collections import defaultdict

# -------------------- Files -------------------- #
DATA_FILE = "expenses.json"
BUDGET_FILE = "budget.json"

# -------------------- Load/Save -------------------- #
def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            for exp in data:
                exp["category"] = exp["category"].strip().title()
            return data
    return []

def save_expenses(expenses):
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)

def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as file:
            return json.load(file)
    return {}

def save_budget(budget_dict):
    with open(BUDGET_FILE, "w") as file:
        json.dump(budget_dict, file)

# -------------------- Expense Operations -------------------- #
def calculate_monthly_total(month=None, year=None):
    total = 0
    if month is None or year is None:
        now = datetime.now()
        month = now.month
        year = now.year
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        if exp_date.year == year and exp_date.month == month:
            total += exp["amount"]
    return total

def add_expense():
    amount = amount_entry.get()
    category = category_entry.get()
    description = description_entry.get()
    date = date_entry.get_date().strftime("%Y-%m-%d")

    if not amount:
        messagebox.showerror("Error", "Please enter amount!")
        return
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return
    if amount <= 0:
        messagebox.showerror("Error", "Amount must be greater than 0!")
        return

    if not category or category.strip() == "":
        messagebox.showerror("Error", "Please select a category!")
        return

    if not description or not description.replace(" ", "").isalnum():
        messagebox.showerror("Error", "Description should contain only letters and numbers!")
        return

    category = category.strip().title()

    new_expense = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    }

    expenses.append(new_expense)
    save_expenses(expenses)
    update_expense_list()
    update_monthly_summary()

    # Budget warning
    exp_date = datetime.strptime(date, "%Y-%m-%d")
    month_key = f"{exp_date.year}-{exp_date.month}"
    if month_key in budget and calculate_monthly_total(exp_date.month, exp_date.year) > budget[month_key]:
        messagebox.showwarning("Budget Alert", f"Your monthly expenses have exceeded the budget of ₹{budget[month_key]}!")

    # Reset input fields
    amount_entry.delete(0, "end")
    description_entry.delete(0, "end")
    category_entry.current(0)
    date_entry.set_date(datetime.now())

    messagebox.showinfo("Success", "Expense added!")

def edit_expense():
    selected = expense_listbox.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an expense to edit!")
        return
    index = int(selected[0])
    exp = expenses[index]

    amount_entry.delete(0, "end")
    amount_entry.insert(0, exp["amount"])
    category_entry.set(exp["category"])
    description_entry.delete(0, "end")
    description_entry.insert(0, exp["description"])
    date_entry.set_date(datetime.strptime(exp["date"], "%Y-%m-%d"))

    add_button.config(text="Save Edit", bootstyle=INFO, command=lambda: save_edit(index))

def save_edit(index):
    amount = amount_entry.get()
    category = category_entry.get()
    description = description_entry.get()
    date = date_entry.get_date().strftime("%Y-%m-%d")

    if not amount:
        messagebox.showerror("Error", "Please enter amount!")
        return
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number!")
        return
    if amount <= 0:
        messagebox.showerror("Error", "Amount must be greater than 0!")
        return

    if not category or category.strip() == "":
        messagebox.showerror("Error", "Please select a category!")
        return

    if not description or not description.replace(" ", "").isalnum():
        messagebox.showerror("Error", "Description should contain only letters and numbers!")
        return

    category = category.strip().title()

    expenses[index] = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    }

    save_expenses(expenses)
    update_expense_list()
    update_monthly_summary()

    amount_entry.delete(0, "end")
    description_entry.delete(0, "end")
    category_entry.current(0)
    date_entry.set_date(datetime.now())

    add_button.config(text="Add Expense", bootstyle=SUCCESS, command=add_expense)
    messagebox.showinfo("Success", "Expense updated!")

def delete_expense():
    selected = expense_listbox.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an expense to delete!")
        return
    index = int(selected[0])
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?")
    if confirm:
        expenses.pop(index)
        save_expenses(expenses)
        update_expense_list()
        update_monthly_summary()
        messagebox.showinfo("Success", "Expense deleted!")

# -------------------- Charts -------------------- #
def show_pie_chart():
    selected_month = month_var.get()
    selected_year = year_var.get()
    categories = {}
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        if exp_date.year == selected_year and exp_date.month == selected_month:
            cat = exp["category"].title()
            categories[cat] = categories.get(cat, 0) + exp["amount"]

    if not categories:
        messagebox.showinfo("Info", "No expenses for selected month/year.")
        return

    plt.figure(figsize=(6, 6))
    plt.pie(categories.values(), labels=categories.keys(), autopct="%1.1f%%", startangle=140)
    plt.title(f"Expenses by Category ({selected_month}/{selected_year})")
    plt.show()

def show_monthly_bar_chart():
    if not expenses:
        messagebox.showinfo("Info", "No expenses to show chart.")
        return
    monthly_totals = defaultdict(float)
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        key = f"{exp_date.year}-{exp_date.month}"
        monthly_totals[key] += exp["amount"]

    months = list(monthly_totals.keys())
    totals = list(monthly_totals.values())

    plt.figure(figsize=(10, 5))
    plt.bar(months, totals, color="skyblue")
    plt.xlabel("Month-Year")
    plt.ylabel("Total Expense (₹)")
    plt.title("Total Expenses by Month")
    plt.xticks(rotation=45)
    plt.show()

# -------------------- Budget & Export -------------------- #
def set_budget():
    selected_month = month_var.get()
    selected_year = year_var.get()
    month_key = f"{selected_year}-{selected_month}"
    b = simpledialog.askfloat("Set Budget", f"Enter budget for {selected_month}/{selected_year} (₹):", minvalue=0)
    if b is not None:
        budget[month_key] = b
        save_budget(budget)
        messagebox.showinfo("Budget Set", f"Budget for {selected_month}/{selected_year} set to ₹{b}")
        update_expense_list()
        update_monthly_summary()

def export_to_csv():
    if not expenses:
        messagebox.showinfo("Info", "No expenses to export.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if file_path:
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["S.No", "Date", "Category", "Description", "Amount"])
            for idx, exp in enumerate(expenses, start=1):
                writer.writerow([idx, exp["date"], exp["category"], exp["description"], f"{exp['amount']:.2f}"])
        messagebox.showinfo("Exported", f"Expenses exported to {file_path}")

# -------------------- Update List -------------------- #
sort_ascending = True
sort_column = None

def update_expense_list(search_text=""):
    global sort_ascending, sort_column
    expense_listbox.delete(*expense_listbox.get_children())
    total = 0
    filtered_expenses = []

    selected_month = month_var.get()
    selected_year = year_var.get()

    search_text_lower = search_text.lower()
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        if (search_text_lower in exp["category"].lower() or
            search_text_lower in exp["description"].lower() or
            search_text_lower in exp["date"]) and exp_date.month == selected_month and exp_date.year == selected_year:
            filtered_expenses.append(exp)

    if sort_column is not None:
        key_map = {0: lambda x: expenses.index(x),
                   1: lambda x: x["date"],
                   2: lambda x: x["category"],
                   3: lambda x: x["description"],
                   4: lambda x: x["amount"]}
        filtered_expenses.sort(key=key_map[sort_column], reverse=not sort_ascending)

    for idx, exp in enumerate(filtered_expenses, start=1):
        total += exp["amount"]
        expense_listbox.insert("", "end", iid=expenses.index(exp), values=(
            idx, exp["date"], exp["category"], exp["description"], f"{exp['amount']:.2f}"
        ))

    total_label.config(text=f"Total Expense: ₹{total:.2f}")
    monthly_label.config(text=f"Selected Month: ₹{total:.2f}")

# -------------------- Monthly Summary Table -------------------- #
def update_monthly_summary():
    monthly_summary_tree.delete(*monthly_summary_tree.get_children())
    monthly_totals = defaultdict(float)
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        key = f"{exp_date.year}-{exp_date.month}"
        monthly_totals[key] += exp["amount"]

    sorted_keys = sorted(monthly_totals.keys())
    for idx, key in enumerate(sorted_keys, start=1):
        y, m = key.split("-")
        budget_amount = budget.get(key, 0)
        monthly_summary_tree.insert("", "end", values=(idx, int(m), int(y), f"{monthly_totals[key]:.2f}", f"{budget_amount:.2f}"))

# -------------------- GUI -------------------- #
root = tb.Window(themename="flatly")
root.title("Modern Expense Tracker")
root.geometry("1000x800")
root.resizable(False, False)

# Input Frame
input_frame = tb.Frame(root, padding=15)
input_frame.pack(pady=10)

tb.Label(input_frame, text="Amount").grid(row=0, column=0, padx=10, pady=5, sticky=E)
amount_entry = tb.Entry(input_frame, width=25)
amount_entry.grid(row=0, column=1, padx=10, pady=5)

tb.Label(input_frame, text="Category").grid(row=1, column=0, padx=10, pady=5, sticky=E)
category_entry = tb.Combobox(input_frame, values=["Food", "Travel", "Shopping", "Bills", "Others"], width=22)
category_entry.grid(row=1, column=1, padx=10, pady=5)
category_entry.current(0)

tb.Label(input_frame, text="Description").grid(row=2, column=0, padx=10, pady=5, sticky=E)
description_entry = tb.Entry(input_frame, width=25)
description_entry.grid(row=2, column=1, padx=10, pady=5)

tb.Label(input_frame, text="Date").grid(row=3, column=0, padx=10, pady=5, sticky=E)
date_entry = DateEntry(input_frame, width=23, bootstyle="info")
date_entry.grid(row=3, column=1, padx=10, pady=5)
date_entry.set_date(datetime.now())

add_button = tb.Button(input_frame, text="Add Expense", bootstyle=SUCCESS, command=add_expense, width=20)
add_button.grid(row=4, column=0, columnspan=2, pady=10)

# Month/Year Selection for charts & budget
month_year_frame = tb.Frame(root, padding=10)
month_year_frame.pack()

tb.Label(month_year_frame, text="Month").pack(side=LEFT, padx=5)
month_var = tb.IntVar(value=datetime.now().month)
month_spin = tb.Spinbox(month_year_frame, from_=1, to=12, textvariable=month_var, width=5, command=lambda: update_expense_list())
month_spin.pack(side=LEFT, padx=5)

tb.Label(month_year_frame, text="Year").pack(side=LEFT, padx=5)
year_var = tb.IntVar(value=datetime.now().year)
year_spin = tb.Spinbox(month_year_frame, from_=2000, to=2100, textvariable=year_var, width=7, command=lambda: update_expense_list())
year_spin.pack(side=LEFT, padx=5)

# Search Frame
search_frame = tb.Frame(root, padding=10)
search_frame.pack(pady=5)
tb.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
search_entry = tb.Entry(search_frame, width=50)
search_entry.pack(side=LEFT, padx=5)
search_entry.bind("<KeyRelease>", lambda e: update_expense_list(search_entry.get()))

# Expense List
columns = ("S.No", "Date", "Category", "Description", "Amount")
expense_listbox = tb.Treeview(root, columns=columns, show="headings", height=10, bootstyle=INFO)
for idx, col in enumerate(columns):
    expense_listbox.heading(col, text=col)
    expense_listbox.column(col, width=150, anchor="center")
expense_listbox.pack(padx=20, pady=10)

# Buttons Frame
btn_frame = tb.Frame(root, padding=10)
btn_frame.pack()

edit_button = tb.Button(btn_frame, text="Edit", bootstyle=WARNING, command=edit_expense, width=12)
edit_button.pack(side=LEFT, padx=5)

delete_button = tb.Button(btn_frame, text="Delete", bootstyle=DANGER, command=delete_expense, width=12)
delete_button.pack(side=LEFT, padx=5)

chart_button1 = tb.Button(btn_frame, text="Monthly Pie", bootstyle=PRIMARY, command=show_pie_chart, width=12)
chart_button1.pack(side=LEFT, padx=5)

chart_button2 = tb.Button(btn_frame, text="All Months Bar", bootstyle=INFO, command=show_monthly_bar_chart, width=12)
chart_button2.pack(side=LEFT, padx=5)

budget_button = tb.Button(btn_frame, text="Set Budget", bootstyle=SUCCESS, command=set_budget, width=12)
budget_button.pack(side=LEFT, padx=5)

export_button = tb.Button(btn_frame, text="Export CSV", bootstyle=SECONDARY, command=export_to_csv, width=12)
export_button.pack(side=LEFT, padx=5)

# Total Labels
total_label = tb.Label(root, text="Total Expense: ₹0.00", font=("Arial", 14, "bold"))
total_label.pack(pady=5)

monthly_label = tb.Label(root, text="Selected Month: ₹0.00", font=("Arial", 12, "bold"))
monthly_label.pack(pady=2)

# Monthly Summary Table
monthly_summary_frame = tb.Frame(root, padding=10)
monthly_summary_frame.pack(pady=10)

summary_columns = ("S.No", "Month", "Year", "Total Expense", "Budget")
monthly_summary_tree = tb.Treeview(monthly_summary_frame, columns=summary_columns, show="headings", height=8, bootstyle=INFO)
for idx, col in enumerate(summary_columns):
    monthly_summary_tree.heading(col, text=col)
    monthly_summary_tree.column(col, width=120, anchor="center")
monthly_summary_tree.pack()

# Load data
expenses = load_expenses()
budget = load_budget()
update_expense_list()
update_monthly_summary()

root.mainloop()