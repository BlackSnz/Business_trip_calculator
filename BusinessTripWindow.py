import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo, askyesno
from idlelib.tooltip import Hovertip
#from dateutil.relativedelta import relativedelta
from random import randint
from datetime import datetime, timedelta
import re
import json
import os

# Проверка вводимых дат командирования на корректность
def date_verification(begin_date: str, end_date: str):

    bt_begin_date = begin_date
    bt_end_date = end_date
    # Check that entries fill
    if not bt_begin_date and not bt_end_date:
        showwarning(title="Предупреждение", message="Введите дату начала и окончания командирования")
        return False
    elif not bt_begin_date:
        showwarning(title="Предупреждение", message="Введите дату начала командирования")
        return False
    elif not bt_end_date:
        showwarning(title="Предупреждение", message="Введите дату окончания командирования")
        return False

    date_pattern = r'(?<!\d)(?:0?[1-9]|[12][0-9]|3[01]).(?:0?[1-9]|1[0-2]).(?:19[0-9][0-9]|20[0-9][0-9])(?!\d)'
    
    # Check valid date
    if not re.match(date_pattern, bt_begin_date):
        showwarning(title="Неверная дата", message="Введите правильную дату начала командирования")
        return False
    elif not re.match(date_pattern, bt_end_date):
        showwarning(title="Неверная дата", message="Введите правильную дату окончания командирования")
        return False

    # Converting str date to datetime
    bt_begin_date = tuple(int(item) for item in bt_begin_date.split('.'))
    bt_end_date = tuple(int(item) for item in bt_end_date.split('.'))
    bt_begin_date = datetime(bt_begin_date[2], bt_begin_date[1], bt_begin_date[0])
    bt_end_date = datetime(bt_end_date[2], bt_end_date[1], bt_end_date[0])
    bt_duration = bt_end_date - bt_begin_date

    if bt_end_date < bt_begin_date:
        showwarning(title="Неверная дата", message="Дата окончания командирование раньше начала командирования")
        return

    return True

# Класс реализующий создание окна с вкладками
# Вкладки "Основная информация", "Список командировок", "Редактирование командировок"
# Содержит логику взаимодействия с этими интерефейсами

class BusinessTripWindow(Tk):

    def __init__(self, root_window):
        super().__init__()
        
        # Get root window object
        self.root_window = root_window
        
        # Bt window parameters
        self.eval('tk::PlaceWindow . center')
        self.title("Мои командировки")

        # Interface of bt window 
        self.tab_control = ttk.Notebook(self)

        self.bt_main_info = ttk.Frame(self.tab_control)
        self.tab_control.add(self.bt_main_info, text='Основная информация')
        self.show_bt_main_info()

        self.bt_list_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.bt_list_tab, text='Список командировок')
        self.show_bt_list()

        self.bt_edit_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.bt_edit_tab, text='Редактирование командировок')
        self.bt_list_edit_add_bt_button = Button(self.bt_edit_tab, text='Добавить командировку', command=self.add_bt_button_click)
        self.bt_list_edit_add_bt_button.pack(anchor=NW, padx=10, pady=10)
        self.update_idletasks()
        self.bt_list_clear_button = Button(self.bt_edit_tab, text='Очистить список командировок')
        self.bt_list_clear_button.bind('<ButtonRelease-1>', self.bt_list_clear_click)
        self.bt_list_clear_button.pack(anchor=NW, padx=10, pady=10)

        # ==========
        #  ОТЛАДКА
        # ==========
        self.bt_list_label_debug = ttk.Label(self.bt_edit_tab, text='Функционал отладки (ВНИМАНИЕ: возможна потеря данных!)')
        self.bt_list_label_debug.pack(anchor=NW, padx=10, pady=10)
        self.bt_list_debug_button = Button(self.bt_edit_tab, text='Добавить командирования для отладки')
        self.bt_list_debug_button.bind('<ButtonRelease-1>', self.bt_add_debug_bt)
        self.bt_list_debug_button.pack(anchor=NW, padx=10, pady=10)

        self.tab_control.pack(expand=1, fill='both')

        def on_closing():

            self.destroy()
            self.root_window.deiconify()
            
        self.protocol("WM_DELETE_WINDOW", on_closing)

    def bt_add_debug_bt(self, event):

        countries = sorted(['Россия', 'Беларусь', 'Индия', 'Турция', 'Бангладеш', 'Иран'])
        try:
            os.remove('data.json')
        except:
            pass        

        # Наполнение списка командирований для отладки
        bt_id = 0
        data = {}
        data['bt'] = []
        bt_begin = datetime(2021, 6, 1)
        bt_end = datetime(2021, 6, 15)
        
        for i in range(15):
            bt_id += 1
            bt_duration = bt_end - bt_begin
            data['bt'].append({
                "btId" : bt_id,
                "bt_country" : countries[randint(0, len(countries)-1)],
                "bt_begin_date" : bt_begin.strftime('%d.%m.%Y'),
                "bt_end_date" : bt_end.strftime('%d.%m.%Y'),
                "bt_days_count" : bt_duration.days + 1
            })
            bt_begin = bt_end
            bt_end += timedelta(days=randint(1,50))
            
        with open('data.json', 'w') as write_file:
            json.dump(data, write_file, indent=2)

        self.update_bt_list()

    def add_bt_button_click(self):
        self.bt_list_edit_add_bt_button.config(state='disable')
        AddBtWindow(self)

    # Создание интерфейса вкладки "Основная информация"
    def show_bt_main_info(self):
        
        today_text_label = ttk.Label(self.bt_main_info, text='Текущая дата: ')
        today_date_label = ttk.Label(self.bt_main_info, text=f'{datetime.today().strftime("%d.%m.%y")}')

        resident_text_label = ttk.Label(self.bt_main_info, text='Дата начала отсчёта резиденства: ')
        # TO DO install relativedelta use relativedelta(years=1)!!!
        resident_date_label = ttk.Label(self.bt_main_info, text=f'{(datetime.today() - timedelta(days=365)).strftime("%d.%m.%y")}')

        bt_days_amount_tuple = self.bt_days_amount()
        bt_amount_text_label = ttk.Label(self.bt_main_info, text='Количество командировок: ')
        bt_amount_label = ttk.Label(self.bt_main_info, text=f'{bt_days_amount_tuple[0]}')
        bt_days_amount_text_label = ttk.Label(self.bt_main_info, text='Дней командирования: ')
        bt_days_amount_label = ttk.Label(self.bt_main_info, text=f'{bt_days_amount_tuple[1]}')

        today_text_label.grid(row=0, column=0)
        today_date_label.grid(row=0, column=1)

        resident_text_label.grid(row=1, column=0)
        resident_date_label.grid(row=1, column=1)

        bt_amount_text_label.grid(row=2, column=0)
        bt_amount_label.grid(row=2, column=1)
        bt_days_amount_text_label.grid(row=3,column=0)
        bt_days_amount_label.grid(row=3, column=1)
    # Создание интерфейса и логики вкладки "Список командировок"
    def show_bt_list(self):

        def sort(col, reverse):
            # получаем все значения столбцов в виде отдельного списка
            l = [(self.bt_list_table.set(k, col), k) for k in self.bt_list_table.get_children("")]

            # Сортировка для столбцов с датой
            if col == 2 or col == 3: # 2 - начало  командировки, 3 - конец командировкии
                l = sorted(l, key=lambda x: datetime.strptime(x[0], '%d.%m.%Y'), reverse=reverse)
            # Сортировка остальных столбцов
            else:
                l.sort(reverse=reverse)
            # переупорядочиваем значения в отсортированном порядке
            for index,  (_, k) in enumerate(l):
                self.bt_list_table.move(k, "", index)
            # в следующий раз выполняем сортировку в обратном порядке
            self.bt_list_table.heading(col, command=lambda: sort(col, not reverse))

        try:
            with open("data.json", "r") as read_file:
                data = json.load(read_file)
        except:
            self.bt_list_tab_label = Label(self.bt_list_tab, text = 'Командировки отсутствуют')
            self.bt_list_tab_label.pack()
        else:
            bt_list = []
            for bt in data['bt']:
                bt_list.append(tuple([
                    bt['btId'],
                    bt['bt_country'], 
                    bt['bt_begin_date'], 
                    bt['bt_end_date'], 
                    bt['bt_days_count']]))
            
            columns = ('id', 'country', 'begin', 'end', 'days')

            self.bt_list_table = ttk.Treeview(self.bt_list_tab, columns=columns, show='headings', selectmode='browse')
    
            self.bt_list_table.heading('id', text='id', command=lambda: sort(0, False))
            self.bt_list_table.heading('country', text='Страна', command=lambda: sort(1, False))
            self.bt_list_table.heading('begin', text='Начало', command=lambda: sort(2, False))
            self.bt_list_table.heading('end', text='Конец', command=lambda: sort(3, False))
            self.bt_list_table.heading('days', text='Дней', command=lambda: sort(4, False))

            # Задание параметров столбцов
            self.bt_list_table.column('#1', width=30, stretch=NO) # ID
            self.bt_list_table.column('#2', width=90, stretch=NO) # Страна
            self.bt_list_table.column('#3', width=70, stretch=NO) # Начало
            self.bt_list_table.column('#4', width=70, stretch=NO) # Конец
            self.bt_list_table.column('#5', width=40, stretch=NO) # Дней

            self.bt_list_table.pack(side=LEFT, fill=BOTH, expand=1)

            # Создание Scrollbar для пролистывания списка командировок
            self.bt_list_scroll_y = ttk.Scrollbar(self.bt_list_tab, orient=tk.VERTICAL, command=self.bt_list_table.yview)
            self.bt_list_scroll_y.pack(side=RIGHT, fill=Y)
            self.bt_list_table['yscrollcommand'] = self.bt_list_scroll_y.set

            for bt in bt_list:
                tags = ('r-click',)
                self.bt_list_table.insert('', END, values=bt, tags=tags)

            self.bt_list_table.tag_bind('r-click', '<Button-3>', self.open_bt_list_table_menu)
    # Создание интерфейса и логики всплывающего меню при клике ПКМ на строку в списке командировок
    def open_bt_list_table_menu(self, event):

        tree = event.widget
        item = tree.identify_row(event.y)
        item_values = tree.item(item, option='values')
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        menu = Menu(self, tearoff=0)
        # Item values is tuple(id, country, bt_begin_date, bt_end_date, bt_duration)
        menu.add_command(label='Редактировать', command=lambda: EditBtWindow(self, item_values))
        menu.add_command(label='Удалить', command=lambda: self.delete_selected_bt(self, item_values[0]))
        menu.post(x, y)
    # Реализация удаления выбранной командировки из списка командировок
    # Находится в меню вызываемой кликом ПКМ на строку в списке командировок
    def delete_selected_bt(self, event, id):
        bt_id_in_list = int(id)-1
        try:
            with open("data.json", "r") as read_file:
                data = json.load(read_file)
        except:
            showerror('Ошибка чтения', 'Файл хранения командирований повреждён')
        else:
            data['bt'].pop(bt_id_in_list)
            for i in range(bt_id_in_list, len(data['bt'])):
                data['bt'][i]['btId'] -= 1
            
            with open('data.json', 'w') as write_file:
                json.dump(data, write_file, indent=2)
            
            self.update_bt_list()
    # Реализация очистки списка командирования - удаление data.json
    def bt_list_clear_click(self, event):
        result = askyesno(title="Подтвержение операции", message="Вы действительно хотите очистить список командировок?")
        if result:
            try:
                with open("data.json", "r") as read_file:
                    data = json.load(read_file)
            except:
                pass
            else:
                os.remove('data.json')
                showinfo("Результат", "Список командировок очищен")
                self.update_bt_list()
        else:     
            showinfo("Результат", "Операция отменена")
    # Функция реализующая обновление вкладок основной информации и списка командировок
    # Используется при внесении изменений в data.json
    def update_bt_list(self):
        self.bt_main_info.destroy()
        self.bt_main_info = ttk.Frame(self.tab_control)
        self.tab_control.insert(0, self.bt_main_info, text='Основная информация')
        self.tab_control.pack(expand=1, fill='both')
        self.show_bt_main_info()

        self.bt_list_tab.destroy()
        self.bt_list_tab = ttk.Frame(self.tab_control)
        self.tab_control.insert(1, self.bt_list_tab, text='Список командировок')
        self.tab_control.pack(expand=1, fill='both')
        self.show_bt_list()
    # Фукнция подсчета общего количества командировок и дней командирования
    def bt_days_amount(self):
        try:
            with open("data.json", "r") as read_file:
                data = json.load(read_file)
        except:
            return 'Командировки отсутствуют', 'Командировки отсутствуют'
        else:
            bt_amount = 0
            bt_days_amount = 0
            for bt in data['bt']:
                bt_amount += 1
                bt_days_amount += bt['bt_days_count']
            return bt_amount, bt_days_amount

# Класс реализующий создание и функционал окна добавления командировок    
class AddBtWindow(Tk):
    def __init__(self, bt_window):
        super().__init__()

        # Запись родительского (master) объекта в переменную
        self.bt_window = bt_window

        # TO DO centering window
        self.title("Добавить командировку")

        # Создание интерфейса окна AddBtWindow
        self.bt_country_text = ttk.Label(self, text='Выбор страны: ')
        self.bt_begin_date_text = ttk.Label(self, text='Дата начала командирования:')
        self.bt_end_date_text = ttk.Label(self, text='Дата окончания командирования:')
        self.bt_country_text.grid(column=0, row=0, padx=10, pady=10)
        self.bt_begin_date_text.grid(column=0, row=1, padx=10, pady=10)
        self.bt_end_date_text.grid(column=0, row=2, padx=10, pady=10)

        countries = sorted(['Россия', 'Беларусь', 'Индия', 'Турция', 'Бангладеш', 'Иран'])
        countries_var = countries[0]
        self.bt_country_combobox = ttk.Combobox(self, textvariable=countries_var, values=countries, state="readonly")
        self.bt_begin_entry = ttk.Entry(self)
        self.bt_end_entry = ttk.Entry(self)
        self.bt_country_combobox.grid(column=1, row=0, padx=10)
        self.bt_begin_entry.grid(column=1, row=1, padx=10)
        self.bt_end_entry.grid(column=1, row=2, padx=10)
        Hovertip(self.bt_begin_entry, "В формате: ДД.ММ.ГГГГ", hover_delay=100)
        Hovertip(self.bt_end_entry, "В формате: ДД.ММ.ГГГГ", hover_delay=100)

        self.bt_add_button = ttk.Button(self, text='Добавить')
        self.bt_add_button.bind('<Button-1>', self.add_business_trip)
        self.bt_add_button.grid(column=1, row=3, padx=10, pady=10)

        # Отслеживание закрытие окна, включение кнопки "добавить командировку"
        def on_closing():
            self.destroy()
            bt_window.bt_list_edit_add_bt_button.config(state='normal')
            
        self.protocol("WM_DELETE_WINDOW", on_closing)

    # Функция реализующая добавление командировки из окна AddBtWindow
    # Происходит проверка входных данных и запись в JSON-файл
    def add_business_trip(self, event):
        
        # Получение данных из Entry
        bt_country = self.bt_country_combobox.get()
        bt_begin = self.bt_begin_entry.get()
        bt_end = self.bt_end_entry.get()
        
        # Проверка валидности введенных дат
        # bt_begin and bt_end - str object format DD.MM.YYYY
        if not date_verification(bt_begin, bt_end):
            return
        
        bt_begin_date = tuple(int(item) for item in bt_begin.split('.'))
        bt_end_date = tuple(int(item) for item in bt_end.split('.'))
        bt_begin_date = datetime(bt_begin_date[2], bt_begin_date[1], bt_begin_date[0])
        bt_end_date = datetime(bt_end_date[2], bt_end_date[1], bt_end_date[0])
        bt_duration = bt_end_date - bt_begin_date

        # Проверка существования файла списка командировок, исходя из этого
        # Создание + запись или просто запись
        try:
            with open("data.json", "r") as read_file:
                data = json.load(read_file)
        except:
            bt_id = 1
            data = {}
            data['bt'] = []
            data['bt'].append({
                "btId" : bt_id,
                "bt_country" : bt_country,
                "bt_begin_date" : bt_begin,
                "bt_end_date" : bt_end,
                "bt_days_count" : bt_duration.days + 1
            })
                
            with open('data.json', 'w') as write_file:
                json.dump(data, write_file, indent=2)
            
            # Включение кнопки, обновление списка командировок, закрытие окна
            self.bt_window.bt_list_edit_add_bt_button.config(state='normal')
            self.bt_window.update_bt_list()
            self.destroy()
            
        else:
            for bt in data['bt']:

                data_bt_begin_date = tuple(int(item) for item in bt['bt_begin_date'].split('.'))
                data_bt_end_date = tuple(int(item) for item in bt['bt_end_date'].split('.'))
                data_bt_begin_date = datetime(data_bt_begin_date[2], data_bt_begin_date[1], data_bt_begin_date[0])
                data_bt_end_date = datetime(data_bt_end_date[2], data_bt_end_date[1], data_bt_end_date[0])
                
                # Проверка пересечения добавляемой командировки с существующими
                if bt_end_date > data_bt_begin_date:
                    if bt_begin_date < data_bt_end_date:
                        except_bt_id = bt['btId'] 
                        except_bt_country = bt['bt_country']
                        except_bt_begin = bt['bt_begin_date']
                        except_bt_end = bt['bt_end_date']
                        showwarning(title="Пересечение командировок", message=f'Введённый срок командирования пересекается с:\n'\
                            f'Командировка №{except_bt_id}: {except_bt_country}({except_bt_begin}-{except_bt_end})')
                        return
                
            bt_count = 0
            for bt in data['bt']:
                bt_count += 1
            bt_id = bt_count + 1
            data['bt'].append({
                "btId" : bt_id,
                "bt_country" : bt_country,
                "bt_begin_date" : bt_begin,
                "bt_end_date" : bt_end,
                "bt_days_count" : bt_duration.days + 1
            })
                
            with open('data.json', 'w') as write_file:
                json.dump(data, write_file, indent=2)
            
            self.bt_window.bt_list_edit_add_bt_button.config(state='normal')
            self.bt_window.update_bt_list()
            self.destroy()

# Класс реализующий создание и функционал окна редактирования определенного командирования.
class EditBtWindow(Tk):
    def __init__(self, bt_window, bt_info):
        super().__init__()

        # Получение объекта родителя (master) - BussinesTripWindow
        self.bt_window = bt_window
        # Получение информации о выбранной для редактирования командировки.
        # Информация в виде tuple(id, country, bt_begin_date, bt_end_date, bt_duration),
        # получаемая из объекта Treeview в tab из Notebook класса BussinesTripWindow
        self.bt_info = bt_info

        # TO DO centering window
        self.title(f'Изменить командировку: {self.bt_info[1]}({self.bt_info[2]}-{self.bt_info[3]})')

        # Создание интерфейса окна
        self.bt_country_text = ttk.Label(self, text='Выбор страны: ')
        self.bt_begin_date_text = ttk.Label(self, text='Дата начала командирования:')
        self.bt_end_date_text = ttk.Label(self, text='Дата окончания командирования:')
        self.bt_country_text.grid(column=0, row=0, padx=10, pady=10)
        self.bt_begin_date_text.grid(column=0, row=1, padx=10, pady=10)
        self.bt_end_date_text.grid(column=0, row=2, padx=10, pady=10) 
        countries = sorted(['Россия', 'Беларусь', 'Индия', 'Турция', 'Бангладеш', 'Иран'])
        self.bt_country_combobox = ttk.Combobox(self, values=countries, state="readonly")
        self.bt_country_combobox.set(self.bt_info[1])
        self.bt_begin_entry = ttk.Entry(self)
        self.bt_begin_entry.insert(0, self.bt_info[2])
        self.bt_end_entry = ttk.Entry(self)
        self.bt_end_entry.insert(0, self.bt_info[3])
        self.bt_country_combobox.grid(column=1, row=0, padx=10)
        self.bt_begin_entry.grid(column=1, row=1, padx=10)
        self.bt_end_entry.grid(column=1, row=2, padx=10)

        # Подсказки при наведении на Entry для ввода даты
        Hovertip(self.bt_begin_entry, "В формате: ДД.ММ.ГГГГ", hover_delay=100)
        Hovertip(self.bt_end_entry, "В формате: ДД.ММ.ГГГГ", hover_delay=100)

        # Реализация кнопки "Изменить" для вызова фунции change_bt_info 
        # Применяет изменения внесённые в форму к выбранному командированию
        self.bt_add_button = ttk.Button(self, text='Изменить')
        self.bt_add_button.bind('<Button-1>', self.change_bt_info)
        self.bt_add_button.grid(column=1, row=3, padx=10, pady=10)

        # Функция для закрытия окна на "крестик" интерфейса окон windows
        def on_closing():
            self.destroy()
        
        self.protocol("WM_DELETE_WINDOW", on_closing)

    # Реализация функции изменения выбранного командирования 
    def change_bt_info(self, event):

        bt_id = int(self.bt_info[0])
        bt_prev_country = self.bt_info[1]
        bt_prev_begin = self.bt_info[2]
        bt_prev_end = self.bt_info[3]

        bt_country = self.bt_country_combobox.get()
        bt_begin = self.bt_begin_entry.get()
        bt_end = self.bt_end_entry.get()
        
        
        if not date_verification(bt_begin, bt_end):
            return
        
        bt_begin_date = tuple(int(item) for item in bt_begin.split('.'))
        bt_end_date = tuple(int(item) for item in bt_end.split('.'))
        bt_begin_date = datetime(bt_begin_date[2], bt_begin_date[1], bt_begin_date[0])
        bt_end_date = datetime(bt_end_date[2], bt_end_date[1], bt_end_date[0])
        bt_duration = bt_end_date - bt_begin_date

        # Checking for the existence of a file, and then creating file or writing information to the file.
        try:
            with open("data.json", "r") as read_file:
                data = json.load(read_file)
        except:
            showwarning(title="Error: File is not exist", message="Файл хранения командировок повреждён")
            self.destroy()
        else:
            for bt in data['bt']:

                data_bt_begin_date = tuple(int(item) for item in bt['bt_begin_date'].split('.'))
                data_bt_end_date = tuple(int(item) for item in bt['bt_end_date'].split('.'))
                data_bt_begin_date = datetime(data_bt_begin_date[2], data_bt_begin_date[1], data_bt_begin_date[0])
                data_bt_end_date = datetime(data_bt_end_date[2], data_bt_end_date[1], data_bt_end_date[0])

                if bt['btId'] == bt_id:
                    continue

                if bt_end_date > data_bt_begin_date:
                    if bt_begin_date < data_bt_end_date:
                        except_bt_id = bt['btId'] 
                        except_bt_country = bt['bt_country']
                        except_bt_begin = bt['bt_begin_date']
                        except_bt_end = bt['bt_end_date']
                        showwarning(title="Пересечение командировок", message=f'Введённый срок командирования пересекается с:\n'\
                            f'Командировка №{except_bt_id}: {except_bt_country}({except_bt_begin}-{except_bt_end})')
                        return
                
            data['bt'][bt_id-1]['bt_country'] = bt_country
            data['bt'][bt_id-1]['bt_begin_date'] = bt_begin
            data['bt'][bt_id-1]['bt_end_date'] = bt_end
            data['bt'][bt_id-1]['bt_days_count'] = bt_duration.days + 1
                
            with open('data.json', 'w') as write_file:
                json.dump(data, write_file, indent=2)
            
            self.bt_window.update_bt_list()
            self.destroy()
