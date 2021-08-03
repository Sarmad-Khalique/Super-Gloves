import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter.constants import S
import pdfkit
import jinja2
import sqlite3
import tkinter.messagebox


class LabelInput(tk.Frame):
    """A widget containing a label and input together."""

    def __init__(self, parent, label='', input_var=None):
        super().__init__(parent)
        self.variable = input_var

        self.label = tk.Label(self, text=label)
        self.label.grid(row=0, column=0, sticky=(
            tk.W + tk.E), padx=10, pady=(5, 0))

        self.input = tk.Entry(self, textvariable=self.variable,font=("Arial",12),relief = tk.RIDGE,bd=5,justify=tk.CENTER)
        self.input.grid(row=1, column=0, sticky=(
            tk.W + tk.E), padx=10, pady=(0, 5))

    def set(self, value):
        self.input.delete(0, tk.END)
        self.input.insert(0, value)

    def get(self):
        return self.input.get()


class DataForm(tk.Frame):
    """The input form for our widgets"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.inputs = {}

        self.po = []
        self.desc = []

        ID = tk.IntVar()

        search_frame = tk.LabelFrame(self)
        tk.Label(search_frame,text="Enter Gatepass ID to Search: ").grid(row=0,column=0,pady=5,padx=(10,0))
        tk.Entry(search_frame,textvariable=ID,font=("Arial",12),justify=tk.CENTER).grid(row=0,column=1,padx=10,pady=5)
        tk.Button(search_frame,text="Search",command=lambda:self.search(ID.get())).grid(row=0,column=2,padx=(0,10))
        search_frame.pack(pady=15)

    

        frame_1 = tk.LabelFrame(self)
        self.inputs["Date"] = LabelInput(
            frame_1, label="Date", input_var=tk.StringVar)
        self.inputs["Date"].grid(row=0, column=0)
        value = datetime.now().strftime("%d - %M - %y")
        self.inputs["Date"].set(value)

        self.inputs["Time"] = LabelInput(
            frame_1, label="Time", input_var=tk.StringVar)
        self.inputs["Time"].grid(row=0, column=1)
        value = datetime.now().strftime("%H : %M : %S")
        self.inputs["Time"].set(value)

        self.inputs["To"] = LabelInput(
            frame_1, label="To", input_var=tk.StringVar)
        self.inputs["To"].grid(row=0, column=2)

        self.inputs["Carrier"] = LabelInput(
            frame_1, label="Carrier", input_var=tk.StringVar)
        self.inputs["Carrier"].grid(row=0, column=3)
        frame_1.pack()

        self.frame_2 = tk.LabelFrame(self)
        tk.Label(self.frame_2, text="Enter Number of Items: ").grid(
            row=0, column=0, padx=5, pady=5)
        rows = tk.StringVar()
        tk.Entry(self.frame_2, textvariable=rows,justify=tk.CENTER,relief= tk.GROOVE,bd=5).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(self.frame_2, text="Submit", command=lambda: self.add(rows.get())).grid(
            row=0, column=2, padx=5, pady=5)
        self.frame_2.pack(pady=5)

        self.frame_3 = tk.LabelFrame(self)
        self.frame_3.pack(pady=5)
    def clear_frame(self):
        for widgets in self.frame_3.winfo_children():
            widgets.destroy()
        self.inputs["Time"].set(datetime.now().strftime("%H : %M : %S"))
    def search(self,id):
        conn = sqlite3.connect('./Database//database.db')
        query = f'''SELECT * FROM "General" WhERE ID={id}'''
        g_record = [row for row in conn.execute(query)]
        if len(g_record) == 0:
            tkinter.messagebox.showerror("Invalid Record ID value",f"ID with value {id} not exist")
            return
        else:
            query = f'''SELECT po,desc FROM "PO" WhERE ID in (SELECT po_id FROM JOINT WHERE general_id = {id})'''
            po_record = [row for row in conn.execute(query)]
            rows = len(po_record)
            self.add(rows,po_record)
            for i,w in enumerate(self.inputs.values()):
                w.set(g_record[0][i+1])
            po_id_query = f'''SELECT id FROM "PO" WhERE ID in (SELECT po_id FROM JOINT WHERE general_id = {id})'''
            # add update button instead of submit at this point and define update funstion
            po_id = [id[0] for id in conn.execute(po_id_query)]
            ttk.Button(self.frame_3, text="Update", command=lambda:self.update(id,po_id)).grid(
                        row=int(rows)+3, column=0, columnspan=2, sticky="WE")
    def update(self,id,*args):
        try:
            conn = sqlite3.connect('./Database//database.db')
            c = conn.cursor()
            date, time, reciever, carrier = [w.get() for w in self.inputs.values()]
            query = f'''UPDATE General SET reciever = "{reciever}",carrier = "{carrier}", date = {date}, time = {time} WHERE id={id}'''
            c.execute(query)
            i = 0
            for p,d in zip(self.po, self.desc):
                if args:
                    query = f'''UPDATE PO SET po = "{p.get()}",desc = "{d.get()}" WHERE id={args[0][i]}'''
                    c.execute(query)
                    i+=1
            conn.commit()
            tkinter.messagebox.showinfo("Records Update","Records Updated Successfully")
            c.close()
            self.clear_frame()
        except:
            tkinter.messagebox.showerror("Records Update","Records Can't be Updated")
        
    def add(self, rows,*args):
        self.clear_frame()
        if rows != "":
            if int(rows)<=10:
                tk.Label(self.frame_3, text="Purchase Order").grid(
                    row=0, column=0, pady=5)
                tk.Label(self.frame_3, text="Description").grid(row=0, column=1, pady=5)
                for i in range(int(rows)):
                    po = tk.StringVar()
                    po_entry = tk.Entry(self.frame_3, textvariable=po,font=("Arial",12),justify=tk.CENTER)
                    po_entry.grid(row=i+1, column=0, padx=5, pady=(0, 5))
                    self.po.append(po_entry)
                    desc = tk.StringVar()
                    desc_entry = tk.Entry(self.frame_3, textvariable=desc, width=70,font=("Arial",12),justify=tk.CENTER)
                    desc_entry.grid(row=i+1, column=1, padx=(0, 5), pady=(0, 5))
                    self.desc.append(desc_entry)
                    if args:
                        po.set(args[0][i][0])
                        desc.set(args[0][i][1])
                ttk.Button(self.frame_3, text="Submit", command=self.get_data).grid(
                    row=int(rows)+3, column=0, columnspan=2, sticky="WE")
            else:
                tkinter.messagebox.showerror("Wrong Input","Max Range is 10")
        else:
            tkinter.messagebox.showerror("Wrong Input", "Enter a number")

    def get_data(self):
        try:
            data = {}
            records = []
            for k, w in self.inputs.items():
                data[k] = w.get()
            for p, d in zip(self.po, self.desc):
                records.append({"po": p.get(), "desc": d.get()})

            no = self.write_data()

            templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
            templateEnv = jinja2.Environment(loader=templateLoader)
            template = templateEnv.get_template("pdf.html")
            params = {
                "data": data,
                "records": records
            }
            html = template.render(params)
            pdfkit.from_string(html, f"./Gatepasses//Gatepass {no}.pdf")
            tkinter.messagebox.showinfo("PDF File Creation","PDF File Created Successfully!")
            self.po = []
            self.desc = []
            self.clear_frame()
        except:
            tkinter.messagebox.showerror("PDF File Creation","PDF File not Created")
    def write_data(self):
        conn = sqlite3.connect('./Database//database.db')
        c = conn.cursor()
        date, time, reciever, carrier = [w.get() for w in self.inputs.values()]
        query = f'''INSERT INTO "General" (date,time,reciever,carrier) \
            VALUES ("{date}","{time}","{reciever}","{carrier}")'''
        c.execute(query)
        g_id = c.lastrowid
        for p, d in zip(self.po, self.desc):
            query = f'''INSERT INTO "PO" (po,desc) \
                VALUES ("{p.get()}","{d.get()}")'''
            c.execute(query)
            p_id = c.lastrowid
            query_2 = f'''INSERT INTO "Joint" (general_id,po_id) \
            VALUES ("{g_id}","{p_id}")'''
            c.execute(query_2)

        conn.commit()
        c.close()
        return g_id

    def view(self):
        view_win = tk.Toplevel()
        view_win.geometry("1200x600")
        view_win.title("Super Gloves - Data Query")
        view_win.resizable(0, 0)

        conn = sqlite3.connect('./Database//database.db')
        c = conn.cursor()
        query = '''SELECT * FROM "General"'''
        c.execute(query)

        tk.Label(view_win, text="Super Gloves Industries", font=(
            "Arial", 18, ("bold", "italic")),relief=tk.RIDGE,bd=5).pack(pady=10,fill=tk.X,side=tk.TOP,ipady=10)
        tk.Label(view_win, text="Outward Gatepass Record", font=(
                "Arial", 12, "bold"),bd=3,relief=tk.GROOVE).pack(pady=(0, 5))

        data_frame = tk.LabelFrame(view_win)
        data_frame.pack(padx=10)
        # columns
        columns = ('#1', '#2', '#3','#4','#5')

        tree = ttk.Treeview(data_frame, columns=columns, show='headings')

        # define headings
        tree.heading('#1', text='ID')
        tree.heading('#2', text='Date')
        tree.heading('#3', text='Time')
        tree.heading('#4', text='Reciever')
        tree.heading('#5', text='Carrier')

        for row in c:
            tree.insert('', tk.END, values=row)

        tree.grid(row=0, column=0, sticky='nsew')

        # add a scrollbar
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        tk.Label(view_win,text="Created By Muhammad Sarmad Khalique",justify=tk.CENTER,font=("Arial",10,"bold"),bd=4,relief=tk.SUNKEN).pack(fill=tk.X,side=tk.BOTTOM)

        c.close()

class MyApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Super Gloves")
        self.geometry("1000x650")
        self.resizable(0, 0)
        self.iconbitmap("./icon//img.ico")

        tk.Label(self, text="Super Gloves Industries", font=(
            "Arial", 18, ("bold", "italic")),relief=tk.RIDGE,bd=5).pack(pady=10,fill=tk.X,side=tk.TOP,ipady=10)

        data_form = DataForm(self)
        data_form.pack()

        menubar = tk.Menu(self)
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Data Record",command=data_form.view)
        menubar.add_cascade(label="View", menu=viewmenu)

        tk.Label(self,text="Created By Muhammad Sarmad Khalique",justify=tk.CENTER,font=("Arial",10,"bold"),bd=4,relief=tk.SUNKEN).pack(fill=tk.X,side=tk.BOTTOM)

        self.config(menu=menubar)
if __name__ == '__main__':
    app = MyApplication()
    app.mainloop()
