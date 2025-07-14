import sqlite3
from datetime import datetime
import pandas as pd
from tabulate import tabulate
import os 
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL
    )
    """)

conn.commit()
conn.close()

def add_Transaction():
    print("Add an Transaction: ")
    while True:
        t_type=input("Enter Transaction Type (income/expense): ").strip().lower()
        if t_type in ['income','expense']:
            break
        print("Invalid Input Please Enter income or expense")
    while True:
        try:
            amount=float(input("Enter Amount: "))
            if amount<=0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number.")
    
    category = input("Enter category (e.g. Food, Rent, Salary): ").strip()
    description = input("Enter description (optional): ").strip()

    date_input = input("Enter date (YYYY-MM-DD) [Leave empty for today]: ").strip()
    if not date_input:
        date= datetime.today().strftime('%Y-%m-%d')
    else:
        try:
            datetime.strptime(date_input, '%Y-%m-%d')
            date = date_input
        except :
            print("Invalid date format. Using today’s date.")
            date = datetime.today().strftime('%Y-%m-%d')
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (type, amount, category, description, date) VALUES (?, ?, ?, ?, ?)""", (t_type, amount, category, description, date))
    conn.commit()
    conn.close()
    print("Transaction added successfully!")

def view_transactions():
    print("\nAll Transactions:")
    conn=sqlite3.connect("expenses.db")
    df=pd.read_sql_query("select * from transactions order by date desc",conn)    
    conn.close()
    if df.empty:
        print("\nNo Transaction Found")
        return
    df['amount'] = df['amount'].map(lambda x: f"₹{x:.2f}")
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))

def monthly_summary():
    print("\nMonthly Summary: ")
    month = input("Enter month (YYYY-MM): ").strip()
    conn = sqlite3.connect("expenses.db")
    query = """SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC"""
    df = pd.read_sql_query(query, conn, params=(month,))
    cursor=conn.cursor()
    cursor.execute("SELECT amount FROM budgets WHERE month = ?", (month,))
    result=cursor.fetchone()
    conn.close()
    if df.empty:
        print("\nNo transactions found for this month.")
        return
    income_total=df[df['type']=='income']['amount'].sum()
    expense_total=df[df['type']=='expense']['amount'].sum()
    savings=income_total-expense_total
    print(f"\nTotal Income:  ₹{income_total:.2f}")
    print(f"Total Expense: ₹{expense_total:.2f}")
    print(f"Net Savings:   ₹{savings:.2f}")
    if result:
        budget = result[0]
        print(f"Budget Set:    ₹{budget:.2f}")
        if expense_total > budget:
            print("Overspending Alert! You've exceeded the monthly budget.")
        else:
            remaining = budget - expense_total
            print(f"Remaining Budget: ₹{remaining:.2f}")
    else:
        print("No budget set for this month.")
    summary=df[df['type']=='expense'].groupby('category')['amount'].sum().reset_index()
    if not summary.empty:
        summary['amount'] = summary['amount'].map(lambda x: f"₹{x:.2f}")
        print("\nExpense by Category:")
        print(tabulate(summary, headers='keys', tablefmt='grid', showindex=False))

def export_to_csv():
    print("\nExport Transactions to CSV")
    month = input("Enter month to export (YYYY-MM): ").strip()
    conn = sqlite3.connect("expenses.db")
    query = """SELECT * FROM transactions WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC"""
    df = pd.read_sql_query(query, conn, params=(month,))
    conn.close()
    df['amount'] = df['amount'].map(lambda x: round(x, 2))
    filename = f"transactions_{month}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    df.to_csv(filepath, index=False)
    print(f"Transactions exported successfully to: {filename}")

def create_budget_table():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        month TEXT PRIMARY KEY,
        amount REAL NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def set_budget():
    print("\nSet Monthly Budget")
    month=input("Enter Month (YYYY-MM): ").strip()
    try:
        amount=float(input("Enter a budget amount: ").strip())
        if amount<=0:
            raise ValueError
    except ValueError:
        print("Invalid error! Try again")
        return
    conn=sqlite3.connect('expenses.db')
    cursor=conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (month, amount)
        VALUES (?, ?)
        ON CONFLICT(month) DO UPDATE SET amount = excluded.amount
    """, (month, amount))
    conn.commit()
    conn.close()
    print(f"Budget of ₹{amount:.2f} set for {month}.")
def main():
    create_budget_table()  # Ensure budget table exists

    while True:
        print("\nPERSONAL EXPENSE & BUDGET TRACKER")
        print("1. Add Transaction")
        print("2. View All Transactions")
        print("3. Monthly Summary")
        print("4. Set Monthly Budget")
        print("5. Export Monthly Data to CSV")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            add_Transaction()
        elif choice == '2':
            view_transactions()
        elif choice == '3':
            monthly_summary()
        elif choice == '4':
            set_budget()
        elif choice == '5':
            export_to_csv()
        elif choice == '6':
            print("Exiting... See you next time!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()




    