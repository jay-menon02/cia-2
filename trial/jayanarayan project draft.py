from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
import mysql.connector

db = mysql.connector.connect(host="localhost",user="root",password="root")
cursor = db.cursor()
cursor.execute("create database if not exists central")
cursor.execute("use central")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_no BIGINT NOT NULL,
        customer_name VARCHAR(255) NOT NULL,
        mobile BIGINT NOT NULL,
        branch_code VARCHAR(10) NOT NULL,
        address VARCHAR(255) NOT NULL,
        balance INT DEFAULT '0',
        dob DATE DEFAULT NULL,
        email VARCHAR(100) DEFAULT NULL,
        PRIMARY KEY (account_no),
        UNIQUE KEY email (email)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS pass (
        username VARCHAR(18) NOT NULL,
        password VARCHAR(255) DEFAULT NULL,
        account_no BIGINT DEFAULT NULL,
        security_question VARCHAR(255) DEFAULT NULL,
        security_answer VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (username),
        UNIQUE KEY unique_account_no (account_no),
        CONSTRAINT pass_ibfk_1 FOREIGN KEY (account_no) REFERENCES accounts (account_no)
    )
""")
cursor.execute("""
    CREATE TABLE if not exists transactions (
        transaction_id int NOT NULL AUTO_INCREMENT,
        account_no bigint DEFAULT NULL,
        transaction_type varchar(10) DEFAULT NULL,
        amount int DEFAULT NULL,
        transaction_date timestamp NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (transaction_id),
        KEY account_no (account_no),
        CONSTRAINT transactions_ibfk_1 FOREIGN KEY (account_no) REFERENCES accounts (account_no)
    )
""")

def login():
    def account_page(username, account_data):
        global account_window
        account_window = Toplevel(root)
        account_window.title("Account Page")
        account_window.geometry("300x500")
        account_window.configure(bg="#ADD8E6")
        

        cursor.execute("SELECT account_no FROM pass WHERE username='{}'".format(username))
        account_info = cursor.fetchone()

        if account_info and account_info[0] is not None:
            account_no_label = Label(account_window, text="Account Number: {}".format(account_info[0]), bg="#ADD8E6")
            account_no_label.pack()
        else:
            messagebox.showerror("Account Information Error", "Failed to retrieve account information.")
            account_window.destroy()  
            return

        customer_name_label = Label(account_window, text="Customer Name: {}".format(account_data[1]), bg="#ADD8E6")
        customer_name_label.pack()

        button_width = 20
        button_height = 2


        view_balance_button = Button(account_window, text="View Balance", command=view_balance, bg="#FFD700", width=button_width, height=button_height)
        deposit_button = Button(account_window, text="Deposit", command=lambda: deposit(account_data), bg="#FFD700", width=button_width, height=button_height)
        withdraw_button = Button(account_window, text="Withdraw", command=lambda: withdraw(account_data), bg="#FFD700", width=button_width, height=button_height)
        transaction_history_button = Button(account_window, text="Transaction History", command=lambda: transaction_history(account_data[0]), bg="#FFD700", width=button_width, height=button_height)
        update_user_info_button = Button(account_window, text="Update User Info", command=lambda: update_user_info(account_data[0]), bg="#FFD700", width=button_width, height=button_height)
        display_details_button = Button(account_window, text="Display User Details", command=lambda: display_user_details(account_data[0]), bg="#FFD700", width=button_width, height=button_height)
        loan_enquiry_button = Button(account_window, text="Loan Enquiry", command=loan_enquiry, bg="#FFD700", width=button_width, height=button_height)
        hb=Button(account_window,text='GO TO MAIN PAGE',command=gtmp,bg='#FFD700',width=button_width, height=button_height)
        # Button placement
        view_balance_button.place(x=50, y=100)
        deposit_button.place(x=50, y=150)
        withdraw_button.place(x=50, y=200)
        transaction_history_button.place(x=50, y=250)
        update_user_info_button.place(x=50, y=300)
        display_details_button.place(x=50, y=350)
        loan_enquiry_button.place(x=50, y=400)
        hb.place(x=50,y=450)
    def gtmp():
        account_window.iconify()
        root.deiconify()

    def view_balance():
        cursor.execute("SELECT balance FROM accounts WHERE account_no={}".format(account_data[0]))
        balance = cursor.fetchone()

        if balance is not None:
            messagebox.showinfo("View Balance", "Your current balance: ${}".format(balance[0]))
        else:
            messagebox.showerror("Error", "Failed to retrieve balance information.")
    def perform_transaction(transaction_type, amount, account_data):
        cursor.execute("SELECT * FROM accounts WHERE account_no=%s", (account_data[0],))
        updated_account_data = cursor.fetchone()

        if transaction_type == "deposit":
            new_balance = updated_account_data[5] + amount
        elif transaction_type == "withdrawal" and updated_account_data[5] >= amount:
            new_balance = updated_account_data[5] - amount
        else:
            messagebox.showerror("Transaction Failed", "Insufficient funds for withdrawal")
            return

        cursor.execute("UPDATE accounts SET balance=%s WHERE account_no=%s", (new_balance, account_data[0]))
        cursor.execute("INSERT INTO transactions (account_no, transaction_type, amount) VALUES (%s, %s, %s)",
                       (account_data[0], transaction_type, amount))
        db.commit()
        messagebox.showinfo(transaction_type.capitalize(), f"{transaction_type.capitalize()} successful. New balance: ${new_balance}")

    def deposit(account_data):
        deposit_window = Toplevel(root)
        deposit_window.title("Deposit")
        deposit_window.geometry("300x150")
        deposit_window.configure(bg="#00CED1")

        deposit_label = Label(deposit_window, text="Enter deposit amount:", bg="#00CED1")
        deposit_label.pack()

        deposit_amount_var = StringVar()
        deposit_entry = Entry(deposit_window, textvariable=deposit_amount_var)
        deposit_entry.pack()

        def perform_deposit():
            try:
                deposit_amount = int(deposit_amount_var.get())
                if deposit_amount > 0:
                    perform_transaction("deposit", deposit_amount, account_data)
                    deposit_window.destroy()
                else:
                    messagebox.showerror("Invalid Amount", "Please enter a valid deposit amount.")
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number.")

        deposit_button = Button(deposit_window, text="Deposit", command=perform_deposit)
        deposit_button.pack()

    def withdraw(account_data):
        withdraw_window = Toplevel(root)
        withdraw_window.title("Withdraw")
        withdraw_window.geometry("300x150")
        withdraw_window.configure(bg="#00CED1")

        withdraw_label = Label(withdraw_window, text="Enter withdrawal amount:", bg="#00CED1")
        withdraw_label.pack()

        withdraw_amount_var = StringVar()
        withdraw_entry = Entry(withdraw_window, textvariable=withdraw_amount_var)
        withdraw_entry.pack()

        def perform_withdrawal():
            try:
                withdraw_amount = int(withdraw_amount_var.get())
                if withdraw_amount > 0:
                    perform_transaction("withdrawal", withdraw_amount, account_data)
                    withdraw_window.destroy()
                else:
                    messagebox.showerror("Invalid Amount", "Please enter a valid withdrawal amount.")
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number.")

        withdraw_button = Button(withdraw_window, text="Withdraw", command=perform_withdrawal)
        withdraw_button.pack()
            
               
    def display_user_details(account_no):
        global details_text
        details_window = Toplevel(root)
        details_window.title("User Details")
        details_window.geometry("800x500")

        details_text = scrolledtext.ScrolledText(details_window, wrap=WORD)
        details_text.pack(expand=YES, fill=BOTH)

        # Fetch and display user details
        cursor.execute("SELECT * FROM accounts WHERE account_no={}".format(account_no))
        account_details = cursor.fetchone()

        cursor.execute("SELECT * FROM pass WHERE account_no={}".format(account_no))
        pass_details = cursor.fetchone()

        if account_details and pass_details:
            details_text.insert(END, f"Account Number: {account_details[0]}\n")
            details_text.insert(END, f"Customer Name: {account_details[1]}\n")
            details_text.insert(END, f"Mobile: {account_details[2]}\n")
            details_text.insert(END, f"Branch Code: {account_details[3]}\n")
            details_text.insert(END, f"Address: {account_details[4]}\n")
            details_text.insert(END, f"Balance: {account_details[5]}\n")
            details_text.insert(END, f"Date of Birth: {account_details[6]}\n")
            details_text.insert(END, f"Email: {account_details[7]}\n\n")
            details_text.insert(END, f"Username: {pass_details[0]}\n")
            details_text.insert(END, f"Password: {pass_details[1]}\n")
            details_text.insert(END, f"Security Question: {pass_details[3]}\n")
            details_text.insert(END, f"Security Answer: {pass_details[4]}\n")
        else:
            details_text.insert(END, "No user details available.")
        details_text.config(state='disabled')
                
    def transaction_history(account_no):
        global history_text 
        history_window = Toplevel(root)
        history_window.title("Transaction History")
        history_window.geometry("800x500")
        history_text = scrolledtext.ScrolledText(history_window, wrap=WORD)
        history_text.pack(expand=YES, fill=BOTH)  
        cursor.execute("SELECT * FROM transactions WHERE account_no={} ORDER BY transaction_date DESC LIMIT 10".format(account_no))
        transactions = cursor.fetchall()
        if transactions:
            for transaction in transactions:
                history_text.insert(END, f"Transaction ID: {transaction[0]}\n")
                history_text.insert(END, f"Account Number: {transaction[1]}\n")
                history_text.insert(END, f"Transaction Type: {transaction[2]}\n")
                history_text.insert(END, f"Amount: {transaction[3]}\n")
                history_text.insert(END, f"Transaction Date: {transaction[4]}\n")
                history_text.insert(END, "\n" + "-"*50 + "\n")
        else:
            history_text.insert(END, "No transaction history available.")
        history_text.config(state='disabled')

    def update_user_info(account_no):
        def get_user_info():
            cursor.execute("SELECT * FROM accounts WHERE account_no=%s", (account_no,))
            account_data = cursor.fetchone()
            name_var.set(account_data[1])
            email_var.set(account_data[7])
            mobile_var.set(account_data[2])
            branch_code_var.set(account_data[3])
            address_var.set(account_data[4])
            cursor.execute("SELECT * FROM pass WHERE account_no=%s", (account_no,))
            pass_data = cursor.fetchone()
            username_var.set(pass_data[0])
            password_var.set(pass_data[1])
            security_question_var.set(pass_data[3])
            security_answer_var.set(pass_data[4])

        update_info_window = Toplevel(root)
        update_info_window.title("Update User Info")
        update_info_window.geometry("500x500")
        update_info_window.configure(bg="#00CED1") 

        name_var = StringVar()
        email_var = StringVar()
        mobile_var = StringVar()
        branch_code_var = StringVar()
        address_var = StringVar()
        username_var = StringVar()
        password_var = StringVar()
        security_question_var = StringVar()
        security_answer_var = StringVar()

        get_user_info()

        name_label = Label(update_info_window, text="Name:", bg="#00CED1")
        name_entry = Entry(update_info_window, textvariable=name_var)
        name_label.pack()
        name_entry.pack()

        email_label = Label(update_info_window, text="Email:", bg="#00CED1")
        email_entry = Entry(update_info_window, textvariable=email_var)
        email_label.pack()
        email_entry.pack()

        mobile_label = Label(update_info_window, text="Mobile:", bg="#00CED1")
        mobile_entry = Entry(update_info_window, textvariable=mobile_var)
        mobile_label.pack()
        mobile_entry.pack()

        branch_code_label = Label(update_info_window, text="Branch Code:", bg="#00CED1")
        branch_code_entry = Entry(update_info_window, textvariable=branch_code_var)
        branch_code_label.pack()
        branch_code_entry.pack()

        address_label = Label(update_info_window, text="Address:", bg="#00CED1")
        address_entry = Entry(update_info_window, textvariable=address_var)
        address_label.pack()
        address_entry.pack()

        username_label = Label(update_info_window, text="Username:", bg="#00CED1")
        username_entry = Entry(update_info_window, textvariable=username_var, state='disabled')
        username_label.pack()
        username_entry.pack()

        password_label = Label(update_info_window, text="Password:", bg="#00CED1")
        password_entry = Entry(update_info_window, textvariable=password_var)
        password_label.pack()
        password_entry.pack()

        security_question_label = Label(update_info_window, text="Security Question:", bg="#00CED1")
        security_question_entry = Entry(update_info_window, textvariable=security_question_var)
        security_question_label.pack()
        security_question_entry.pack()

        security_answer_label = Label(update_info_window, text="Security Answer:", bg="#00CED1")
        security_answer_entry = Entry(update_info_window, textvariable=security_answer_var)
        security_answer_label.pack()
        security_answer_entry.pack()

        def save_updated_info():
            name = name_var.get()
            email = email_var.get()
            mobile = mobile_var.get()
            branch_code = branch_code_var.get()
            address = address_var.get()
            username = username_var.get()
            password = password_var.get()
            security_question = security_question_var.get()
            security_answer = security_answer_var.get()

            if not name or not email or not mobile or not branch_code or not address or not username or not password or not security_question or not security_answer:
                messagebox.showerror("Error", "All fields are mandatory")
                return
            cursor.execute("UPDATE accounts SET customer_name=%s, email=%s, mobile=%s, branch_code=%s, address=%s WHERE account_no=%s",(name, email, mobile, branch_code, address, account_no))
            db.commit()
            cursor.execute("UPDATE pass SET username=%s, password=%s, security_question=%s, security_answer=%s WHERE account_no=%s",(username, password, security_question, security_answer, account_no))
            db.commit()
            messagebox.showinfo("Update Successful", "Account information updated successfully.")
            update_info_window.destroy()

        save_button = Button(update_info_window, text="Save", command=save_updated_info)
        save_button.pack()
    def loan_enquiry():
        messagebox.showinfo("Loan Enquiry", "For loan enquiries, please contact the bank manager, Mr. Jayanarayan Menon Nettath, at 6238633800.")

    root.iconify()  
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Login Failed", "Username or password cannot be empty")
        root.deiconify()  
        return

    cursor.execute("SELECT * FROM pass WHERE username='{}'".format(username))
    user_data = cursor.fetchone()

    if user_data and password == user_data[1]:
        messagebox.showinfo("Login Successful", "Welcome to Central Bank of Wakanda, {}".format(username))
        cursor.execute("SELECT * FROM accounts WHERE account_no=%s", (user_data[2],))
        account_data = cursor.fetchone()
        account_page(username, account_data)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")
        root.deiconify()  

def forgot_password():
    root.iconify()  
    
    def check_account_info():
        forgot_password_window.iconify()  
        account_number_input = account_number_entry.get()

        cursor.execute("SELECT security_question FROM pass WHERE account_no={}".format(account_number_input))
        security_question_data = cursor.fetchone()

        if security_question_data:
            security_question = security_question_data[0]

            security_answer_window = Toplevel(forgot_password_window)
            security_answer_window.title("Security Answer Verification")
            security_answer_window.geometry("400x200")
            security_answer_window.configure(bg="#FFD700")  

            security_question_label = Label(security_answer_window, text="Security Question: {}".format(security_question), bg="#FFD700")
            security_question_label.pack()

            security_answer_label = Label(security_answer_window, text="Security Answer:", bg="#FFD700")
            security_answer_entry = Entry(security_answer_window, show="*", width=30)
            security_answer_label.pack()
            security_answer_entry.pack()

            def verify_security_answer():
                entered_security_answer = security_answer_entry.get()

                cursor.execute("SELECT * FROM pass WHERE account_no={} AND security_answer='{}'".format(account_number_input, entered_security_answer))
                result = cursor.fetchone()

                if result:
                    messagebox.showinfo("Password Recovery", "Your password is: {}".format(result[1]))
                    security_answer_window.destroy()
                    root.deiconify()  
                else:
                    messagebox.showerror("Security Answer Verification Failed", "Incorrect security answer")

            verify_button = Button(security_answer_window, text="Verify", command=verify_security_answer)
            verify_button.pack()

        else:
            messagebox.showerror("Account Information Verification Failed", "Invalid account number")
            root.deiconify()  

    forgot_password_window = Toplevel(root)
    forgot_password_window.title("Forgot Password")
    forgot_password_window.geometry("400x200")
    forgot_password_window.configure(bg="#00CED1") 

    account_number_label = Label(forgot_password_window, text="Account Number:", bg="#00CED1")
    account_number_entry = Entry(forgot_password_window)
    account_number_label.pack()
    account_number_entry.pack()

    continue_button = Button(forgot_password_window, text="Continue", command=check_account_info)
    continue_button.pack()

def create_account():
    root.iconify()  
    def add_account():
        root.iconify()
        account_no = account_no_entry.get()
        customer_name = customer_name_entry.get()
        mobile = mobile_entry.get()
        branch_code = branch_code_entry.get()
        address = address_entry.get()
        balance = balance_entry.get()
        dob = dob_entry.get()
        email = email_entry.get()

        if not account_no or not customer_name or not mobile or not branch_code or not address or not dob or not email:
            messagebox.showerror("Error", "All fields are mandatory")
            create_account_window.deiconify()  
            return
        
        cursor.execute("SELECT * FROM accounts WHERE account_no=%s", (account_no,))
        account_data = cursor.fetchone()

        if account_data:
            messagebox.showerror("Account Creation Failed", "Account number already exists. Please choose another.")
            create_account_window.deiconify()  
        else:
            cursor.execute("INSERT INTO accounts VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (account_no, customer_name, mobile, branch_code, address, balance, dob, email))

            db.commit()
            messagebox.showinfo("Account Created", "Account created successfully")
            get_security_info_window(account_no)
            create_account_window.destroy()
            root.deiconify()  

    create_account_window = Toplevel(root)
    create_account_window.title("Create Account")
    create_account_window.geometry("1000x1000")
    create_account_window.configure(bg="#FFD700")  

    heading_label = Label(create_account_window, text="CBW Create Account Page", font=("Helvetica", 16, "bold"), bg="#FFD700", fg="black")
    heading_label.pack()

    space_label = Label(create_account_window, text="", bg="#FFD700")
    space_label.pack()

    account_no_label = Label(create_account_window, text="Account Number:", bg="#FFD700")
    account_no_entry = Entry(create_account_window)
    account_no_label.pack()
    account_no_entry.pack()

    customer_name_label = Label(create_account_window, text="Customer Name:", bg="#FFD700")
    customer_name_entry = Entry(create_account_window)
    customer_name_label.pack()
    customer_name_entry.pack()

    mobile_label = Label(create_account_window, text="Mobile:", bg="#FFD700")
    mobile_entry = Entry(create_account_window)
    mobile_label.pack()
    mobile_entry.pack()

    branch_code_label = Label(create_account_window, text="Branch Code:", bg="#FFD700")
    branch_code_entry = Entry(create_account_window)
    branch_code_label.pack()
    branch_code_entry.pack()

    address_label = Label(create_account_window, text="Address:", bg="#FFD700")
    address_entry = Entry(create_account_window)
    address_label.pack()
    address_entry.pack()

    balance_label = Label(create_account_window, text="Balance:", bg="#FFD700")
    balance_entry = Entry(create_account_window)
    balance_entry.insert(0, "5000") 
    balance_entry.config(state='disabled')
    balance_label.pack()
    balance_entry.pack()

    dob_label = Label(create_account_window, text="Date of Birth:", bg="#FFD700")
    dob_entry = Entry(create_account_window)
    dob_label.pack()
    dob_entry.pack()

    email_label = Label(create_account_window, text="Email:", bg="#FFD700")
    email_entry = Entry(create_account_window)
    email_label.pack()
    email_entry.pack()

    add_account_button = Button(create_account_window, text="Create Account", command=add_account)
    add_account_button.pack()

    def get_security_info_window(account_no):
        def save_security_info():
            username = username_entry.get()
            password = password_entry.get()
            security_question = security_question_entry.get()
            security_answer = security_answer_entry.get()
            if not username or not password or not security_question or not security_answer:
                messagebox.showerror("Error", "All fields are mandatory")
                return

            cursor.execute("INSERT INTO pass (username, password, account_no, security_question, security_answer) VALUES (%s, %s, %s, %s, %s)",
                           (username, password, account_no, security_question, security_answer))

            db.commit()
            messagebox.showinfo("Security Information Saved", "Security information saved successfully")
            security_info_window.destroy()

        root.iconify()
        security_info_window = Toplevel(root)
        security_info_window.title("Get Security Information")
        security_info_window.geometry("500x300")
        security_info_window.configure(bg="#00CED1")  

        username_label = Label(security_info_window, text="Username:", bg="#00CED1")
        username_entry = Entry(security_info_window)
        username_label.pack()
        username_entry.pack()

        password_label = Label(security_info_window, text="Password:", bg="#00CED1")
        password_entry = Entry(security_info_window, show="*")
        password_label.pack()
        password_entry.pack()

        security_question_label = Label(security_info_window, text="Security Question:", bg="#00CED1")
        security_question_entry = Entry(security_info_window)
        security_question_label.pack()
        security_question_entry.pack()

        security_answer_label = Label(security_info_window, text="Security Answer:", bg="#00CED1")
        security_answer_entry = Entry(security_info_window)
        security_answer_label.pack()
        security_answer_entry.pack()

        save_button = Button(security_info_window, text="Save", command=save_security_info)
        save_button.pack()

# GUI setup
root = Tk()
root.title("Central Bank of Wakanda")
root.geometry("850x550")
root.configure(bg="#008080")  

welcome_label = Label(root, text="Welcome to Central Bank of Wakanda", font=("Helvetica", 26), bg="#008080", fg="white")
welcome_label.place(x=200, y=20)  

username_label = Label(root, text="Username:", font=("Helvetica", 14), bg="#008080", fg="white")
username_entry = Entry(root, width=30)
password_label = Label(root, text="Password:", font=("Helvetica", 14), bg="#008080", fg="white")
password_entry = Entry(root, show="*", width=30)
password_label = Label(root, text="Password:", font=("Helvetica", 14), bg="#008080", fg="white")
password_entry = Entry(root, show="*", width=30)

login_button = Button(root, text="Login", command=login)

forgot_password_button = Button(root, text="Forgot Password", command=forgot_password)

create_account_button = Button(root, text="Create Account", command=create_account)

username_label.place(x=230, y=150)
username_entry.place(x=330, y=150)
password_label.place(x=230, y=190)
password_entry.place(x=330, y=190)
login_button.place(x=330, y=230)
forgot_password_button.place(x=330, y=270)
create_account_button.place(x=330, y=310)

root.mainloop()

cursor.close()
db.close()
