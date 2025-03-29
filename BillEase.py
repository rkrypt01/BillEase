#  ==================================-Libraries-=================================================
from tkinter import*
from tkinter import messagebox
from tkinter.ttk import Progressbar
import random
import csv
from datetime import datetime
import math
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#  ===================-Email_credentials-=====================
EMAIL_ADDRESS = "enter email here"
EMAIL_PASSWORD = "enter password here"

# ====================-window_title_GUI-======================

root = Tk()
root.geometry("1500x800+10+10")
root.resizable(False,False)
root.title("BillEase")
title = Label(root, text="BillEase", font=('times new roman', 30, 'bold'), pady=2, bd=12, bg="#2cc1b6", fg="Black", relief=GROOVE)
title.pack(fill=X)
# 2cc1b6
# ================variables=======================

c_name = StringVar()
c_email = StringVar()
bill_no = StringVar()
x = random.randint(10001, 99999)
bill_no.set(str(x))

qty = []
items = []
price = []
item_qty = []
details = []
calc = []
state = IntVar()
state.set(0)

pymnt_method = StringVar()
pymnt_method.set('Cash')
discount = StringVar()
now = datetime.now()
date_t = now.strftime("%d/%m/%Y %H:%M")
date = now.strftime("%d/%m/%Y")
check = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


with open('Admin/Items_PriceList.csv', 'r', newline='') as f1:
    in_file = csv.reader(f1)
    next(in_file)
    for row in in_file:
        items.append(row[1])
        price.append(row[2])

with open('Admin/Shop_Details.csv', 'r', newline='') as f2:
    in_file = csv.reader(f2)
    next(in_file)
    for row in in_file:
        details.extend(row)

# ==================functions==========================

def total():   # calculates the total cost, tax, discount amt
    if state.get() != 3:
        total_c = 0
        d = 0
        for p, q in zip(price, item_qty):
            try:
                p_value = float(p)
                q_value = float(q.get())
                total_c += p_value * q_value
            except ValueError:
                pass

        try:
            d = (float(discount.get())/100.0*total_c)
        except ValueError:
            pass

        sgst = (float(details[3]) / 100.0) * (total_c - d)
        cgst = (float(details[4]) / 100.0) * (total_c - d)
        total_t = sgst + cgst
        total_a = total_c - d + total_t
        calc.clear()
        calc.extend([total_c, d, sgst, cgst, total_t, total_a])

        disc_amt.config(text=f": ₹{d:.2f}")
        sgst_amt.config(text=f": ₹{sgst:.2f}")
        cgst_amt.config(text=f": ₹{cgst:.2f}")
        total_tax.config(text=f": ₹{total_t:.2f}")
        total_amt.config(text=f": ₹{total_a:.2f}")

        state.set(1)
    else:
        messagebox.showerror("error", "Please clear data before billing for next customer")


def gen_bill():   # generates the bill and displays in a neat format
    txtarea.delete('1.0', END)
    if state.get() == 1:
        if calc[0] == 0:
            messagebox.showerror("Error", "No Product Purchased")
        elif c_name.get() == "" or c_email.get() == "":
            messagebox.showerror("Error", "Customer Details Are Mandatory")
        elif not (re.fullmatch(check, c_email.get())):
            messagebox.showerror("error", "Please enter a valid email address")
        else:
            txtarea.insert(END, f"\n{details[0] : ^52}")
            txtarea.insert(END, f"\n{details[1] : ^52}")
            txtarea.insert(END, f"\n{'PH '+details[2] : ^52}")
            txtarea.insert(END, f"\n\nBill No. : {bill_no.get():<15}{'Date : '+date_t : ^15}")
            txtarea.insert(END, f"\nCustomer Name  : {c_name.get()}")
            txtarea.insert(END, f"\nCustomer Email : {c_email.get()}")
            txtarea.insert(END, "\n\n---------------------------------------------------")
            txtarea.insert(END, f"\n{'Item Name':<23}{'Qty':^9}{'Rate':^9}{'Amount':>9}")
            txtarea.insert(END, "\n---------------------------------------------------")
            for i in range(len(items)):
                try:
                    if float(item_qty[i].get()) > 0:
                        a = float(price[i])*float(item_qty[i].get())
                        txtarea.insert(END, f"\n{items[i]:<23}{item_qty[i].get():^9}{round(float(price[i]),2):^9}{a:>9}")
                except ValueError:
                    pass

            txtarea.insert(END, "\n\n---------------------------------------------------")
            txtarea.insert(END, f"\nTotal{round(calc[0],2):>45}")

            try:
                if float(discount.get()) > 0:
                    txtarea.insert(END, f"\nDiscount @{discount.get()+'%':<15}{-round(calc[1],2):>25}")
            except ValueError:
                pass

            txtarea.insert(END, f"\nSGST @{details[3]+'%':<15}{round(calc[2],2):>29}")
            txtarea.insert(END, f"\nCGST @{details[4]+'%':<15}{round(calc[3],2):>29}")
            txtarea.insert(END, f"\n{'Total Tax':<15}{round(calc[4],2):>35}")
            txtarea.insert(END, "\n\n---------------------------------------------------")
            rupee = '\u20B9'
            txtarea.insert(END, f"\n{'Total Bill Amount : '+rupee+str(round(calc[5],2)):^52}")
            txtarea.insert(END, f"\n{'Paid '+pymnt_method.get():^52}")
            txtarea.insert(END, "\n\n---------------------------------------------------")
            txtarea.insert(END, f"\n\n{'Thank You.':^52}\n{'Visit Again!':^52}")
            txtarea.insert(END, "\n\n---------------------------------------------------")

            state.set(2)
    else:
        messagebox.showerror("Error", "total not computed")


def send_bill():   # sends the bill to the customer by email
    to_email = c_email.get()
    body = f"Dear {c_name.get()},\n\nThank You for shopping at {details[0]}. We hope you had a pleasant shopping experience" \
              f"\n\nAttached to this email, you will find the digital invoice for your purchase." \
              f" If you have any queries or grievance, please don't hesitate to reach out to our customer support team at {details[5]}." \
              f"\n\nWe look forward to Welcome you again. Have a Great Day." \
              f"\n\nBest Regards,\n{details[0]}\n{details[1]}"
    subject = f"{details[0]} - Digital Invoice"
    attachment_path = 'Bills/'+str(bill_no.get())+'.txt'

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(attachment_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={attachment_path}')
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
    server.quit()
    messagebox.showinfo("Bill Sent", f"Bill has been successfully sent to\n{c_email.get()}")


def save_bill():   # saves the bill in computer and records data in csv file
    if state.get() == 2:
        op = messagebox.askyesno("Save Bill", "Do you want to save the bill?")
        if op > 0:
            bill_data = txtarea.get('1.0', END)
            with open('Bills/'+str(bill_no.get())+'.txt', mode='w', encoding='utf-8') as f3:
                f3.write(bill_data)
            with open('Admin/Customer_Sales_Data.csv', 'a', newline='') as f_out:
                out_file = csv.writer(f_out)
                out_file.writerow([bill_no.get(), c_name.get(), c_email.get(), date, calc[5], pymnt_method.get()])
            state.set(3)

            op1 = messagebox.askyesno("Saved  |  send bill?", f"Bill no:{bill_no.get()} Saved Successfully\nDo you want to send Bill to customer?")
            if op1 > 0:
                send_bill()

        else:
            return
    else:
        messagebox.showerror("Error", "Bill not generated\nPlease generate bill")


def docs():     # app usage manual for use reference
    with open('User_Manual.txt', 'r') as f4:
        doc = f4.read()
    top = Toplevel()
    top.geometry('1000x500+150+150')
    manual = Label(top, text="User Manual", font='arial 17 bold', bd=7, relief=GROOVE)
    manual.pack(fill=X)
    yscroll = Scrollbar(top, orient=VERTICAL)
    txt = Text(top, yscrollcommand=yscroll.set, font='arial 13')
    yscroll.pack(side=RIGHT, fill=Y)
    yscroll.config(command=txt.yview)
    txt.place(x=5, y=40, width=990, height=430)
    txt.insert(END, doc)
    exit_b = Button(top, command=top.destroy, text="Exit", activebackground='red', bd=2, bg="#535C68", fg="white",
                    pady=2, width=12, font='arial 10 bold')
    exit_b.place(x=400, y=470)


def clear_data():  # clears all the entries and bills and reset to default values
    op = messagebox.askyesno("Clear", "Do you want to Clear?")
    if op > 0:
        c_name.set('')
        c_email.set('')
        bill_no.set('')
        pymnt_method.set('Cash')
        discount.set('')
        txtarea.delete('1.0', END)
        for entry in item_qty:
            entry.delete(0, END)

        disc_amt.config(text=f": ₹0.00")
        sgst_amt.config(text=f": ₹0.00")
        cgst_amt.config(text=f": ₹0.00")
        total_tax.config(text=f": ₹0.00")
        total_amt.config(text=f": ₹0.00")

        calc.clear()

        x = random.randint(10001, 99999)
        bill_no.set(str(x))
        state.set(0)


def exit_app():   # exits the tkinter window and terminates the program
    op = messagebox.askyesno("Exit", "Do you want to exit the app?")
    if op > 0:
        root.destroy()

# ====================================-customer_details_GUI-=============================================


F1 = LabelFrame(root, text="Customer Details", font=('times new roman', 17, 'bold'), bd=10, fg="Black", bg="#60ede3")
F1.place(x=0, y=78, width=1040)

cname_lbl = Label(F1, text="Customer Name:", bg="#17bb9d", font=('times new roman', 16, 'bold'))
cname_lbl.grid(row=0, column=0, padx=20, pady=5)
cname_txt = Entry(F1, width=18, textvariable=c_name, font='arial 15 bold', bd=7, relief=GROOVE)
cname_txt.grid(row=0, column=1, pady=5, padx=10)

cemail_lbl = Label(F1, text="Customer Email:", bg="#17bb9d", font=('times new roman', 16, 'bold'))
cemail_lbl.grid(row=0, column=2, padx=20, pady=5)
cemail_txt = Entry(F1, width=30, textvariable=c_email, font='arial 15 bold', bd=7, relief=GROOVE)
cemail_txt.grid(row=0, column=3, pady=5, padx=10)


# ======================================-items_list_GUI-============================================

F2 = LabelFrame(root, labelanchor='n', text="ITEMS", font=('times new roman', 22, 'bold') ,bd=10, fg="Black", bg="#c8f9f5")
F2.place(x=2, y=169, width=1040, height=487)

for i in range(0, len(items)):
    if i < 13:
        col = 0
        a = ''
    elif 13 <= i < 26:
        col = 2
        a = '    |    '
    elif 26 <= i < 39:
        col = 4
        a = '    |    '

    item_label = Label(F2, text=a + items[i], font=('times new roman', 14), bg="#c8f9f5", fg="black")
    item_label.grid(row=i % 13, column=col, sticky='W')
    qty_entry = Entry(F2, width=5, font=('times new roman', 14, 'bold'))
    qty_entry.grid(row=i % 13, column=col + 1, padx=10, pady=3)
    item_qty.append(qty_entry)


# ==========================-Bill_GUI-==================================================
F3 = Frame(root, bd=10, relief=GROOVE)
F3.place(x=1045, y=78, width=450, height=578)

bill_title = Label(F3, text="BILL", font='arial 17 bold', bd=7, relief=GROOVE)
bill_title.pack(fill=X)
scroll_y = Scrollbar(F3, orient=VERTICAL)
txtarea = Text(F3, yscrollcommand=scroll_y.set)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_y.config(command=txtarea.yview)
txtarea.pack(fill=BOTH, expand=1)

# ============================-Bill_Details_GUI-===============================================
F4 = LabelFrame(root, text="Bill Details", font=('times new roman', 16, 'bold'), bd=10, bg="#60ede3")
F4.place(x=0, y=660,width=1040, height=140)

m1_lbl = Label(F4, text="Discount %", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="black")
m1_lbl.grid(row=0, column=0, padx=20, pady=1, sticky='W')
disc = Entry(F4, width=5, textvariable=discount, font='arial 12 bold', bd=7, relief=GROOVE, fg='red')
disc.grid(row=0, column=1, padx=20, pady=1)

m2_lbl = Label(F4, text="SGST @"+str(details[3])+"%", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="black")
m2_lbl.grid(row=1, column=0, padx=20, pady=1, sticky='W')
sgst_amt = Label(F4, text=": ₹0.00", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="red")
sgst_amt.grid(row=1, column=1, padx=20, pady=1, sticky='W')


m3_lbl = Label(F4, text="Total Tax", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="black")
m3_lbl.grid(row=2, column=0, padx=20, pady=1, sticky='W')
total_tax = Label(F4, text=": ₹0.00", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="red")
total_tax.grid(row=2, column=1, padx=20, pady=1, sticky='W')


m4_lbl = Label(F4, text="Dicount Amt", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="black")
m4_lbl.grid(row=0, column=2, padx=20, pady=1, sticky='W')
disc_amt = Label(F4, text=": ₹0.00", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="red")
disc_amt.grid(row=0, column=3, padx=20, pady=1, sticky='W')


m5_lbl = Label(F4, text="CGST @"+str(details[4])+"%", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="black")
m5_lbl.grid(row=1, column=2, padx=20, pady=1, sticky='W')
cgst_amt = Label(F4, text=": ₹0.00", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="red")
cgst_amt.grid(row=1, column=3, padx=20, pady=1, sticky='W')


m6_lbl = Label(F4, text="Total Bill Amt", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="black")
m6_lbl.grid(row=2, column=2, padx=20, pady=1, sticky='W')
total_amt = Label(F4, text=": ₹0.00", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="red")
total_amt.grid(row=2, column=3, padx=20, pady=1, sticky='W')

pymnt_lbl = Label(F4, text="Payment Method : ", font=('times new roman', 16, 'bold'), bg="#60ede3", fg="black")
pymnt_lbl.grid(row=0, column=4, padx=20, pady=1, sticky='W')
dropdown = OptionMenu(F4, pymnt_method, "Cash", "Credit Card", "Debit Card", "UPI")
dropdown.grid(row=0, column=5)
dropdown.config(font=('times new roman', 13, 'bold'), fg="red")


# ==================================-Control_Buttons_GUI-======================================

F5 = LabelFrame(root, bd=10, bg="#60ede3")
F5.place(x=1045, y=660, width=450, height=140)

total_btn = Button(F5, command=total, text="Total", activebackground='green', bg="#535C68", bd=2, fg="white", pady=5, width=8, font='arial 14 bold')
total_btn.grid(row=0, column=0, padx=5, pady=5)

genBill_btn = Button(F5, command=gen_bill, text="Generate Bill", activebackground='green', bd=2, bg="#535C68", fg="white", pady=5, width=11, font='arial 14 bold')
genBill_btn.grid(row=0, column=1, padx=5, pady=5)

saveSend_btn = Button(F5, command=save_bill, text="Save/Send Bill", activebackground='green', bd=2, bg="#535C68", fg="white", pady=5, width=12, font='arial 14 bold')
saveSend_btn.grid(row=0, column=2, padx=5, pady=5)

docs_btn = Button(F5, command=docs, text="Docs", activebackground='yellow', bg="#535C68", bd=2, fg="white", pady=5, width=8, font='arial 14 bold')
docs_btn.grid(row=1, column=0, padx=5, pady=5)

clear_btn = Button(F5, command=clear_data, text="Clear", bg="#535C68", bd=2, fg="white", pady=5, width=11, font='arial 14 bold')
clear_btn.grid(row=1, column=1, padx=5, pady=5)

exit_btn = Button(F5, command=exit_app, text="Exit", activebackground='red', bd=2, bg="#535C68", fg="white", pady=5, width=12, font='arial 14 bold')
exit_btn.grid(row=1, column=2, padx=5, pady=5)

root.mainloop()