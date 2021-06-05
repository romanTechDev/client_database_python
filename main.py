from tkinter import *
from tkinter import messagebox, Tk
import pymysql.connections
import hashlib
from threading import *

root = Tk()
root['bg'] = '#fafafa'
root.title('Фотоцентр Клиент')
root.wm_attributes('-alpha', 1)
root.geometry('1900x1000')
root.resizable(width=False, height=False)
DATABASENAME = 'photocenter'
dataBaseNetworkInfo = ('root', 'root', 'localhost', DATABASENAME)


class All_Objects:
    canvas_left = Canvas(root, width=400, bg='white')

    frame_left = Frame(canvas_left, bg='#00A383', height=800, width=400)

    title_database_name = Label(frame_left, text=f'База Данных: {DATABASENAME}', bg='white', font=40)

    label_login = Label(frame_left, text='Логин', bg='white', font=20)
    label_password = Label(frame_left, text='Пароль', bg='white', font=20)

    input_login = Entry(frame_left, bg='white', font=20)
    input_password = Entry(frame_left, bg='white', font=20, show='*')

    authentication_button = Button(frame_left, text='Войти', bg='White', font=40)

    canvas_right = Canvas(root, bg='white')
    frame_middle = Frame(canvas_right, bg='#009999')

    listbox_all_tables = Listbox(frame_left, height=50, width=50)
    scroll = Scrollbar(command=listbox_all_tables.yview)

    frame_right = Frame(canvas_right, bg='#009999')
    title_table = Label(frame_middle, text='Таблица: Не выбрана !', bg='white', font=60)
    listbox_view_table = Listbox(frame_middle, font=10)

    listbox_all_tables.config(yscrollcommand=scroll.set)

    listbox_all_tables = Listbox(frame_left, height=50, width=50)
    scroll = Scrollbar(command=listbox_all_tables.yview)

    add_row_button = Button(frame_middle, name='add_row_button', text='Добавить запись', bg='White', font=40)
    modify_row_button = Button(frame_middle, name='modify_row_button', text='Изменить запись', bg='White', font=40)
    delete_row_button = Button(frame_middle, name='delete_row_button', text='Удалить запись', bg='White', font=40)


class Note:
    buttons_created = False
    table = None


def connect_to_base():
    try:
        connected_data_base = pymysql.connect(user='root', password='root', host='localhost', database=DATABASENAME)
        return connected_data_base
    except pymysql.Error:
        messagebox.showerror('connect_to_base',
                             'Данные в подключении не верны/ Не подключен веб сервер !')


class DataBaseNetwork:  # Работа с данными в базе данных

    def __init__(self):
        self.connected_data_base = connect_to_base()
        self.cursor = self.connected_data_base.cursor()

    def execute_to_base(self, sql_request):
        try:
            self.cursor.execute(sql_request)
            self.connected_data_base.commit()
        except pymysql.Error:
            messagebox.showerror('execute_to_base', 'Данные в запросе не вверны !')

    def get_rows_from_base(self, sql_request):
        try:
            self.cursor.execute(sql_request)
            rows = self.cursor.fetchall()
            return rows
        except pymysql.Error:
            messagebox.showerror('get_rows_from_base',
                                 f'Данные в запросе не вверны !{sql_request}')

    def get_columns_table(self, table):

        columns_dirty = self.get_rows_from_base(f'show columns from {table}')

        columns = [columns[0] for columns in columns_dirty]

        return columns

    def get_rows_table(self, table):

        rows = self.get_rows_from_base(f'select * from {table}')

        return rows

    def add_row(self, table, columns_array, values_array):

        columns = ','.join(columns_array)
        values = "'" + "','".join(values_array) + "'"

        self.execute_to_base(f'INSERT INTO {table}({columns}) VALUES({values})')
        messagebox.showinfo(f'db_add_row', f'УСПЕШНАЯ ЗАПИСЬ !\nINSERT INTO {table}({columns}) VALUES({values})')

    def add_row_hash(self, table, columns_array, hash_sums_array):

        columns = ','.join(columns_array)
        hash_sums = "'" + "','".join(hash_sums_array) + "'"

        self.execute_to_base(f'INSERT INTO {table}({columns}) VALUES({hash_sums})')

    def modify_row(self, table, columns_values_array, id_row):

        data = ''
        counter = 0
        while counter != len(columns_values_array):
            data += f"{columns_values_array[counter]}="
            counter += 1
            data += f"'{columns_values_array[counter]}',"
            counter += 1

        self.execute_to_base(f'UPDATE {table} SET {data[0:-1]} WHERE ID_{table} = "{id_row}"')

        messagebox.showinfo(f'db_modify_row', f'УСПЕШНАЯ ЗАПИСЬ !\nUPDATE {table} SET {data[0:-1]} '
                                              f'WHERE ID_{table} = "{id_row}"')

    def delete_row(self, table, id_row):

        self.execute_to_base(f'DELETE FROM {table} WHERE ID_{table} = "{id_row}"')
        messagebox.showinfo(f'db_delete_row', f'УСПЕШНОЕ УДАЛЕНИЕ !\nDELETE FROM {table} WHERE ID_{table} = "{id_row}"')

    def __del__(self):
        self.connected_data_base.close()


class CreateWorkspace:

    def __init__(self):
        all_objects = All_Objects()
        db_network = DataBaseNetwork()

        all_objects.listbox_all_tables.pack(padx=1, pady=5)  # canvas left
        all_objects.scroll.pack(side=LEFT, fill=Y)

        all_objects.canvas_right.place(relx=0.21, rely=0, relwidth=1, relheight=1)  # canvas right
        all_objects.frame_middle.place(relx=0, rely=0, width=600, relwidth=0.5, relheight=1)
        all_objects.frame_right.place(relx=0.3, rely=0, width=500, relwidth=0.5, relheight=1)
        all_objects.title_table.place(relx=0.05, rely=0.005)
        all_objects.listbox_view_table.place(height=400, width=500, relx=0.03, rely=0.05)

        all_objects.listbox_all_tables.bind('<<ListboxSelect>>', listbox_all_tables_row_selected)

        for row in db_network.get_rows_from_base('show tables'):
            all_objects.listbox_all_tables.insert(END, row)


def listbox_all_tables_row_selected(event):
    note.table = all_objects.listbox_all_tables.get(all_objects.listbox_all_tables.curselection())[0]
    table = note.table

    print(table)

    if table is not None:
        for widget in all_objects.frame_right.winfo_children():
            widget.destroy()

        all_objects.listbox_view_table.delete(0, END)
        all_objects.title_table.config(text=f'Таблица: {table}')

        rely_var = 0.08
        id_input = 0
        counter = 0

        for row in db_network.get_rows_table(table):
            all_objects.listbox_view_table.insert(END, row)

        for column in db_network.get_columns_table(table):
            if counter == 0:
                counter += 1
                continue

            column_name = Label(all_objects.frame_right, name=f'columnName{id_input}', text=column, bg='white',
                                font=30)
            row_input = Entry(all_objects.frame_right, name=f'row_input{id_input}', bg='white', font=30)

            column_name.place(relx=0.03, rely=rely_var)
            row_input.place(relx=0.15, rely=rely_var)

            rely_var += 0.05
            id_input += 1

        if note.buttons_created:
            return

        thread_modify_button = Thread(target=all_objects.modify_row_button.place(relx=0.04, rely=0.5), args=(1,))
        thread_delete_button = Thread(target=all_objects.delete_row_button.place(relx=0.15, rely=0.5), args=(1,))
        thread_add_button = Thread(target=all_objects.add_row_button.place(relx=0.25, rely=0.5), args=(1,))

        thread_modify_button.start()
        thread_delete_button.start()
        thread_add_button.start()

        thread_modify_button.join()
        thread_delete_button.join()
        thread_add_button.join()

        all_objects.modify_row_button.bind('<Button-1>', table_works.modify_row)
        all_objects.delete_row_button.bind('<Button-1>', table_works.delete_row)
        all_objects.add_row_button.bind('<Button-1>', table_works.add_row)

        note.buttons_created = True


class TableWorks:  # Работа с данными в приложении

    def __init__(self, obj_all_objects):
        self.all_objects = obj_all_objects

    def add_row(self, event=None):
        table = note.table

        all_columns = db_network.get_columns_table(table)[1:]
        id_input = 0

        if table == 'clientauth':
            hash_data_to_request = []
            while id_input != len(all_columns):
                row_input = self.all_objects.frame_right.children[f'row_input{id_input}']
                row_input_data = row_input.get().encode('utf-8')
                hash_obj = hashlib.sha256(row_input_data).hexdigest()

                hash_data_to_request.append(hash_obj)
                id_input += 1
                print(hash_obj)

            db_network.add_row_hash(table, all_columns[:-1], hash_data_to_request)
        else:
            data_to_request = []
            while id_input != len(all_columns):
                row_input = self.all_objects.frame_right.children[f'row_input{id_input}']
                data_to_request.append(row_input.get())
                id_input += 1
            db_network.add_row(table, all_columns, data_to_request)

    def delete_row(self, event=None):
        id_row = self.all_objects.listbox_view_table.get(self.all_objects.listbox_view_table.curselection())[0]

        table = note.table

        db_network.delete_row(table, id_row)

    def modify_row(self, event=None):
        data_to_request = []
        selected_row = self.all_objects.listbox_view_table.get(self.all_objects.listbox_view_table.curselection())
        id_row = selected_row[0]
        id_input = 0
        counter = 0

        table = note.table

        for column in db_network.get_columns_table(table):
            if counter == 0:
                counter += 1
                continue
            data_to_request.append(column)
            while id_input != len(selected_row) - 1:
                row_input = self.all_objects.frame_right.children[f'row_input{id_input}']
                data_to_request.append(row_input.get())
                id_input += 1
                break

        print(data_to_request)
        db_network.modify_row(table, data_to_request, id_row)

    def __del__(self):
        buttons = ['modify_row_button', 'delete_row_button', 'add_row_button']
        note.buttons_created = False

        for i in buttons:
            self.all_objects.frame_middle.children[i].destroy()

        self.all_objects.listbox_view_table.delete(0, END)

        for widget in self.all_objects.frame_right.winfo_children():
            widget.destroy()


def authentication(event):
    all_objects = All_Objects()

    login = all_objects.input_login.get()
    login_byte = login.encode('utf-8')
    login_hash = hashlib.sha256(login_byte).hexdigest()

    password = all_objects.input_password.get()
    password_byte = password.encode('utf-8')
    password_hash = hashlib.sha256(password_byte).hexdigest()

    access_data = 0

    if db_network.get_rows_from_base(f"select clientlogin from clientauth where clientlogin = '{login_hash}'"):
        access_data += 1
        if db_network.get_rows_from_base(f"select clientpass from clientauth where clientpass = '{password_hash}'"):
            access_data += 1

    if access_data == 2:
        messagebox.showinfo('Аутентификация', 'Доступ открыт')
        all_objects.label_login.destroy()
        all_objects.label_password.destroy()
        all_objects.input_login.destroy()
        all_objects.input_password.destroy()
        all_objects.authentication_button.destroy()

        create_workspace = CreateWorkspace()
    else:
        messagebox.showerror('Аутентификация', 'Данные не правильные')


# Начало программы
all_objects = All_Objects()
note = Note()

all_objects.canvas_left.pack(side=LEFT, fill=Y)
all_objects.frame_left.place(relx=0, rely=0, relwidth=1, relheight=1)
all_objects.title_database_name.pack(pady=5)
all_objects.label_login.place(relx=0.05, rely=0.1)
all_objects.label_password.place(relx=0.05, rely=0.14)
all_objects.input_login.place(relx=0.3, rely=0.1)
all_objects.input_password.place(relx=0.3, rely=0.14)
all_objects.authentication_button.place(relx=0.41, rely=0.2)

all_objects.authentication_button.bind('<space>', authentication)
all_objects.authentication_button.bind('<Button-1>', authentication)

db_network = DataBaseNetwork()
table_works = TableWorks(all_objects)

root.mainloop()
