import tkinter as tk
from tkinter import messagebox
import customtkinter
import requests
from functools import partial
from tkinter import simpledialog  # Import the simpledialog module
from tkinter import ttk
from CTkTable import *
customtkinter.set_appearance_mode("dark")
roles_window = None
roles_table = None

def add_skill_to_project(project_id, skill_id):
    # Данные для запроса
    data = {
        'ID_проекта': project_id,
        'ID_навыков': skill_id
    }

    # Отправка запроса на сервер
    response = requests.post('http://ideal-web.site:5000/add_skill_to_project', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    # Проверка ответа
    if response.status_code == 200:
        messagebox.showinfo("Успех", "Скилл успешно добавлен к проекту")
        load_project_skills(project_id, skills_table)  # Обновление таблицы скиллов проекта
    else:
        messagebox.showerror("Ошибка", response.json().get('message', 'Не удалось добавить скилл к проекту'))
def add_skill_to_project_with_combobox(project_id, skill_combobox, window):
    skill_info = skill_combobox.get()
    if not skill_info:
        messagebox.showwarning("Предупреждение", "Выберите скилл")
        return

    skill_id = skill_info.split(' (ID: ')[1].split(')')[0]
    add_skill_to_project(project_id, skill_id)
    window.destroy()
def fetch_skills():
    response = requests.get('http://ideal-web.site:5000/skills', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        return response.json()['skills']
    else:
        print("Ошибка при получении списка скиллов")
        return []
def setup_table_style():
    style = ttk.Style()
    style.configure("Custom.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))  # Примерный шрифт
    style.configure("Custom.Treeview.Heading", font=('Calibri', 13, 'bold'))  # Примерный шрифт для заголовков
    style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])  # Убрать границу

def login():
    username = entry_username.get()
    password = entry_password.get()
    response = requests.post('http://ideal-web.site:5000/login', json={'email': username, 'password': password})
    if response.status_code == 200:
        data = response.json()
        if data['user']['Статус'] == 'Админ':
            open_main_window(data['access_token'])
        else:
            label_status.configure(text="Доступ разрешен только администраторам")
    else:
        label_status.configure(text="Неверный логин или пароль")


def on_tab_changed(event):
    selected_tab = event.widget.tab('current')['text']
    if selected_tab == 'Роли':
        fetch_and_display_roles()
    elif selected_tab == 'Пользователи':
        fetch_and_display_users()
    elif selected_tab == 'Скиллы':
        fetch_and_display_skills()

def on_role_select(event):
    selected = roles_table.selection()
    state = 'normal' if selected else 'disabled'
    edit_role_button.configure(state=state)
    delete_role_button.configure(state=state)

def fetch_and_display_users():
    global users_table
    response = requests.get('http://ideal-web.site:5000/users', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        users = response.json()['users']
        for i in users_table.get_children():
            users_table.delete(i)
        for user in users:
            users_table.insert('', 'end', values=(user['ID_участника'], user['Имя'], user['Фамилия'], user['Почта'], user['Статус']))
    else:
        print("Ошибка при получении списка пользователей")
# Функция для добавления нового пользователя
    
def add_user_interface():
    add_user_window = customtkinter.CTkToplevel()
    add_user_window.title("Добавление пользователя")

    # Элементы интерфейса для ввода данных пользователя
    label_email = customtkinter.CTkLabel(add_user_window, text="Email")
    label_email.pack(pady=(25,0))
    entry_email = customtkinter.CTkEntry(add_user_window)
    entry_email.pack(padx=25)

    label_fname = customtkinter.CTkLabel(add_user_window, text="Имя")
    label_fname.pack(pady=(25,0))
    entry_fname = customtkinter.CTkEntry(add_user_window)
    entry_fname.pack(padx=25)

    label_lname = customtkinter.CTkLabel(add_user_window, text="Фамилия")
    label_lname.pack(pady=(25,0))
    entry_lname = customtkinter.CTkEntry(add_user_window)
    entry_lname.pack(padx=25)

    label_password = customtkinter.CTkLabel(add_user_window, text="Пароль")
    label_password.pack(pady=(25,0))
    entry_password = customtkinter.CTkEntry(add_user_window, show="*")
    entry_password.pack()

    # Кнопка отправки данных
    submit_button = customtkinter.CTkButton(add_user_window, text="Добавить",border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: submit_new_user(entry_email.get(), entry_fname.get(), entry_lname.get(), entry_password.get(), add_user_window))
    submit_button.pack(pady=25)

def submit_new_user(email, fname, lname, password, window):
    # Функция для отправки данных нового пользователя на сервер
    data = {
        'Почта': email,
        'Имя': fname,
        'Фамилия': lname,
        'Пароль': password
    }
    response = requests.post('http://ideal-web.site:5000/register', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        print("Пользователь успешно добавлен")
        window.destroy()
        fetch_and_display_users()
    else:
        print("Ошибка при добавлении пользователя: ", response.json().get('message', ''))

# Функция изменения пользователя
def edit_user_interface():
    selected_item = users_table.selection()
    if not selected_item:
        print("Пользователь не выбран")
        return

    user_id = users_table.item(selected_item[0], "values")[0]

    # Открытие окна редактирования
    edit_user_window = customtkinter.CTkToplevel()
    edit_user_window.title(f"Редактирование пользователя {user_id}")

    label_email = customtkinter.CTkLabel(edit_user_window, text="Email")
    label_email.pack(padx=50,pady=(25,0))
    entry_email = customtkinter.CTkEntry(edit_user_window)
    entry_email.pack()

    label_fname = customtkinter.CTkLabel(edit_user_window, text="Имя")
    label_fname.pack(padx=50,pady=(25,0))
    entry_fname = customtkinter.CTkEntry(edit_user_window)
    entry_fname.pack()

    label_lname = customtkinter.CTkLabel(edit_user_window, text="Фамилия")
    label_lname.pack(padx=50,pady=(25,0))
    entry_lname = customtkinter.CTkEntry(edit_user_window)
    entry_lname.pack()

    label_password = customtkinter.CTkLabel(edit_user_window, text="Пароль")
    label_password.pack(padx=50,pady=(25,0))
    entry_password = customtkinter.CTkEntry(edit_user_window, show="*")
    entry_password.pack()

    # Выпадающий список для статуса
    label_status = customtkinter.CTkLabel(edit_user_window, text="Статус")
    label_status.pack(padx=50,pady=(25,0))
    status_combobox = customtkinter.CTkComboBox(edit_user_window, values=['Админ', 'Пользователь'])
    status_combobox.pack()

    # Кнопка для отправки измененных данных
    submit_button = customtkinter.CTkButton(edit_user_window, text="Сохранить", border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: submit_user_changes(user_id, entry_email.get(), entry_fname.get(), entry_lname.get(), entry_password.get(), status_combobox.get(), edit_user_window))
    submit_button.pack(padx=50,pady=(25,20))

def submit_user_changes(user_id, email, fname, lname, password, status, window):
    # Создание запроса с измененными данными пользователя
    data = {}
    if email:
        data['Почта'] = email
    if fname:
        data['Имя'] = fname
    if lname:
        data['Фамилия'] = lname
    if password:
        data['Пароль'] = password
    # Предполагаем, что статус всегда должен быть выбран
    data['Статус'] = status

    # Отправляем запрос только если есть измененные данные
    if data:
        response = requests.put(f'http://ideal-web.site:5000/edit_user/{user_id}', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
        if response.status_code == 200:
            print("Профиль пользователя успешно обновлен")
            window.destroy()
            fetch_and_display_users()
        else:
            print("Ошибка при обновлении профиля пользователя: ", response.json().get('message', ''))
    else:
        print("Нет изменений для сохранения")
        window.destroy()
def show_project_comments(project_id):
    comments_window = customtkinter.CTkToplevel()
    comments_window.title(f"Комментарии проекта {project_id}")

    comments_table = ttk.Treeview(comments_window, columns=('ID', 'Дата', 'Имя', 'Фамилия', 'Email', 'Текст'), show='headings')
    comments_table.column('ID', width=5, anchor ='c')
    comments_table.column('Дата', anchor ='c')
    comments_table.column('Имя', anchor ='c')
    comments_table.column('Фамилия', anchor ='c')
    comments_table.column('Email', anchor ='c')
    comments_table.column('Текст', anchor ='c')
    comments_table.heading('ID', text='ID')
    comments_table.heading('Дата', text='Дата')
    comments_table.heading('Имя', text='Имя')
    comments_table.heading('Фамилия', text='Фамилия')
    comments_table.heading('Email', text='Email')
    comments_table.heading('Текст', text='Текст')
    comments_table.pack()
    def on_comment_select(event):
        delete_comment_button.configure(state='normal')
    # Кнопка для удаления комментария

    comments_table.bind("<<TreeviewSelect>>", on_comment_select)

    add_comment_button = customtkinter.CTkButton(comments_window, text="Добавить комментарий",border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: add_comment(project_id))
    add_comment_button.pack(side='left',padx=150,pady=40)

    delete_comment_button = customtkinter.CTkButton(comments_window, text="Удалить комментарий", state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: delete_comment(project_id, comments_table))
    delete_comment_button.pack(side="right",padx=150,pady=40)

    load_comments(project_id, comments_table)

def show_selected_project_comments():
    selected_item = table_projects.selection()[0]
    if not selected_item:
        print("Проект не выбран")
        return

    project_id = table_projects.item(selected_item, "values")[0]
    show_project_comments(project_id)
    
def delete_comment(project_id, comments_table):
    selected_item = comments_table.selection()
    if not selected_item:
        print("Комментарий не выбран")
        return

    comment_id = int(comments_table.item(selected_item[0], "values")[0])
    response = requests.delete(f'http://ideal-web.site:5000/delete_comment/{comment_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.status_code == 200:
        show_project_comments(project_id)
    else:
        print("Ошибка при удалении комментария")

def load_comments(project_id, comments_table):
    response = requests.get(f'http://ideal-web.site:5000/get_comments/{project_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        comments = response.json()['comments']
        for comment in comments:
            comments_table.insert('', 'end', values=(comment['ID_комментария'], comment['Дата'], comment['Имя'], comment['Фамилия'], comment['Почта'], comment['Текст']))
    else:
        print("Ошибка при получении комментариев")

def add_comment(project_id):
    # Открыть диалоговое окно для ввода текста комментария
    comment_text = simpledialog.askstring("Добавить комментарий", "Введите текст комментария:")
    if comment_text:
        # Отправить комментарий на сервер
        submit_comment(project_id, comment_text)
def submit_comment(project_id, text):
    # Убедитесь, что project_id является целым числом
    project_id_int = int(project_id)

    data = {
        'ID_проекта': project_id_int,
        'Текст': text
    }
    response = requests.post('http://ideal-web.site:5000/add_comment_to_project', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        # После добавления комментария обновить отображение комментариев
        show_project_comments(project_id)
    else:
        print("Ошибка при добавлении комментария: ", response.json().get('message', ''))
def delete_user_interface():
    selected_item = users_table.selection()
    if not selected_item:
        print("Пользователь не выбран")
        return

    user_id = users_table.item(selected_item[0], "values")[0]
    response = requests.delete(f'http://ideal-web.site:5000/delete_user/{user_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    
    if response.status_code in [200, 204]:
        print("Пользователь успешно удален")
        fetch_and_display_users()
    else:
        try:
            error_message = response.json().get('message', 'Ошибка при удалении пользователя')
        except ValueError:  # Если тело ответа не содержит JSON
            error_message = "Неизвестная ошибка при удалении пользователя"
        print(error_message)
def download_user_portfolio():
    selected_item = users_table.selection()
    if not selected_item:
        messagebox.showwarning("Внимание", "Пользователь не выбран")
        return

    user_id = users_table.item(selected_item[0], "values")[0]
    response = requests.get(f'http://ideal-web.site:5000/download_portfolio/{user_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    
    if response.status_code == 200:
        # Здесь код для сохранения PDF файла, полученного в ответе
        with open('portfolio.pdf', 'wb') as f:
            f.write(response.content)
        messagebox.showinfo("Успешно", "Портфолио успешно скачано")
    else:
        messagebox.showerror("Ошибка", "Не удалось скачать портфолио")
def show_project_skills():
    selected_item = table_projects.selection()
    if not selected_item:
        print("Проект не выбран")
        return
    project_id = table_projects.item(selected_item[0], "values")[0]
    open_skills_window(project_id)
def open_skills_window(project_id):
    skills_window = customtkinter.CTkToplevel()
    skills_window.title(f"Скиллы проекта {project_id}")

    # Таблица для отображения скиллов проекта
    skills_table = ttk.Treeview(skills_window, columns=('ID', 'Название'), show='headings')
    skills_table.column('ID', anchor='center', width=50)
    skills_table.column('Название', anchor='center', width=150)
    skills_table.heading('ID', text='ID')
    skills_table.heading('Название', text='Название')
    skills_table.pack(expand=True, fill='both')

    # Загрузка существующих скиллов проекта
    load_project_skills(project_id, skills_table)

    # Выпадающий список для выбора скилла
    label_skill = customtkinter.CTkLabel(skills_window, text="Выберите скилл")
    label_skill.pack(pady=(25, 5))
    skill_combobox = customtkinter.CTkComboBox(skills_window, values=[f"{skill['Название']} (ID: {skill['ID_навыков']})" for skill in fetch_skills()])
    skill_combobox.pack(pady=(0, 20))

    # Кнопка для добавления скилла к проекту
    add_skill_button = customtkinter.CTkButton(skills_window, text="Добавить скилл к проекту", command=lambda: add_skill_to_project_with_combobox(project_id, skill_combobox, skills_window))
    add_skill_button.pack(pady=10)

def load_project_skills(project_id, skills_table):
    # Предположим, что у вас есть эндпоинт, который возвращает скиллы для определенного проекта
    response = requests.get(f'http://ideal-web.site:5000/project/{project_id}/skills', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        skills = response.json()['skills']
        for skill in skills:
            skills_table.insert('', 'end', values=(skill['ID'], skill['Название']))
    else:
        print("Ошибка при получении скиллов проекта")

def add_skill_to_project_with_combobox(project_id, skill_combobox, window):
    skill_info = skill_combobox.get()
    if not skill_info:
        messagebox.showwarning("Предупреждение", "Выберите скилл")
        return

    skill_id = skill_info.split(' (ID: ')[1].split(')')[0]
    add_skill_to_project(project_id, skill_id)
    window.destroy()

def add_skill_to_project(project_id, skill_id):
    data = {
        'ID_проекта': project_id,
        'ID_навыков': skill_id
    }
    response = requests.post('http://ideal-web.site:5000/add_skill_to_project', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        messagebox.showinfo("Успех", "Скилл успешно добавлен к проекту")
        load_project_skills(project_id, skills_table)  # Обновление таблицы скиллов проекта
    else:
        messagebox.showerror("Ошибка", response.json().get('message', 'Не удалось добавить скилл к проекту'))

def fetch_skills():
    response = requests.get('http://ideal-web.site:5000/skills', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        return response.json()['skills']
    else:
        print("Ошибка при получении списка скиллов")
        return []

def load_project_skills(project_id, skills_table):
    # Предположим, что у вас есть эндпоинт, который возвращает скиллы для определенного проекта
    response = requests.get(f'http://ideal-web.site:5000/project/{project_id}/skills', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        skills = response.json()['skills']
        for skill in skills:
            skills_table.insert('', 'end', values=(skill['ID'], skill['Название']))
    else:
        print("Ошибка при получении скиллов проекта")

def add_skill_to_project(project_id, skills_table):
    # Здесь код для добавления нового скилла к проекту
    # Обновите таблицу после добавления
    load_project_skills(project_id, skills_table)

def delete_skill_from_project(project_id, skills_table):
    # Здесь код для удаления выбранного скилла из проекта
    # Обновите таблицу после удаления
    load_project_skills(project_id, skills_table)
def open_main_window(token):
    global ACCESS_TOKEN, login_window, table_projects, edit_button, delete_button, members_button,skills_button, create_button, roles_table, users_table,edit_role_button, delete_role_button,skills_table,show_comments_button, comments_button
    ACCESS_TOKEN = token
    login_window.destroy()


    main_window = customtkinter.CTk()
    main_window.geometry("1024x768")
    main_window.title("Админ-панель")

    frame_topbar = customtkinter.CTkFrame(master=main_window,border_width=1,border_color="#871b41",)
    frame_topbar.pack(side='top', fill="x",)
    textbox = customtkinter.CTkLabel(frame_topbar, text="Admin Panel",font=("Calirby",45))
    textbox.pack(side="left", fill="x", padx=15,pady=15)
    tab_control = ttk.Notebook(main_window)

    # Инициализация вкладки "Проекты"
    tab_projects = customtkinter.CTkFrame(tab_control,border_width=1,border_color="#871b41",)
    tab_control.add(tab_projects, text='Проекты')
    # Инициализация вкладки "Пользователи"
    tab_users = customtkinter.CTkFrame(tab_control,border_width=1,border_color="#871b41",)
    tab_control.add(tab_users, text='Пользователи')
    # Инициализация вкладки "Роли"
    tab_roles = customtkinter.CTkFrame(tab_control,border_width=1,border_color="#871b41",)
    tab_control.add(tab_roles, text='Роли')
    tab_skills = customtkinter.CTkFrame(tab_control,border_width=1,border_color="#871b41",)
    tab_control.add(tab_skills, text='Скиллы')
    # Создание таблицы проектов
    style = ttk.Style()
    style.theme_use("default")
    
    # Настройка цвета фона для ячеек и текста
    style.configure("Treeview",
                    background="#E1E1E1",  # серый фон для строк
                    foreground="#321414",  # цвет текста
                    rowheight=55,  # высота строки
                    fieldbackground="#E1E1E1",
                    font=('Arial', 12))  # фон для ячеек (делает фон за пределами строк того же цвета)
    
    # Настройка стиля при выделении
    style.map("Treeview", background=[('selected', '#641c34')])  # цвет выделенной строки

    # Настройка заголовков столбцов
    style.configure("Treeview.Heading",
                    background="#D3D3D3",  # светло-серый фон для заголовков
                    foreground="#321414",  # цвет текста заголовков
                    relief="flat",
                    font=('Arial', 15, 'bold'))  # убирает эффект "выпуклости" у заголовков
    
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  # Убирает границы
    table_projects = ttk.Treeview(tab_projects, columns=('ID', 'Название', 'Описание', 'Статус'), show='headings', style="Treeview")
    table_projects.column('ID', anchor='center', width=15)
    table_projects.column('Название', anchor='center', width=200)
    table_projects.column('Описание', anchor='center', width=300)
    table_projects.column('Статус', anchor='center', width=200)
    table_projects.heading('ID', text='ID')
    table_projects.heading('Название', text='Название')
    table_projects.heading('Описание', text='Описание')
    table_projects.heading('Статус', text='Статус')
    table_projects.pack(expand=True, fill='both')
    table_projects.bind("<<TreeviewSelect>>", on_project_select)

    # Кнопки управления проектами
    
    create_button = customtkinter.CTkButton(tab_projects, text="Создать новый проект", command=create_new_project,border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    create_button.pack(side='left', fill="x", padx=15,pady=25)
    edit_button = customtkinter.CTkButton(tab_projects, text="Редактировать", command=edit_selected_project, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    edit_button.pack(side='left', fill="x", padx=15,pady=25)
    skills_button = customtkinter.CTkButton(tab_projects, text="Скиллы", command=lambda: show_project_skills(), state='disabled', border_width=1, border_color="#871b41", text_color="#f3f3f3", fg_color="#641c34", hover_color="#8c2749", corner_radius=1)
    skills_button.pack(side='left', fill="x", padx=15, pady=25)
    delete_button = customtkinter.CTkButton(tab_projects, text="Удалить", command=delete_selected_project, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    delete_button.pack(side='left', fill="x", padx=15,pady=25)

    members_button = customtkinter.CTkButton(tab_projects, text="Участники", command=show_selected_project_members, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    members_button.pack(side='left',fill="x",  padx=15,pady=25)

    comments_button = customtkinter.CTkButton(tab_projects, text="Комментарии", command=show_selected_project_comments, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    comments_button.pack(side='left',fill="x",  padx=15,pady=25)


    # Создание таблицы ролей
    roles_table = ttk.Treeview(tab_roles, columns=('ID', 'Название'), show='headings')
    roles_table.column('ID',  anchor='center', width=50)
    roles_table.column('Название',  anchor='center', width=150)
    roles_table.heading('ID', text='ID')
    roles_table.heading('Название', text='Название')
    roles_table.pack(expand=True, fill='both')
    roles_table.bind("<<TreeviewSelect>>", on_role_select)

    # Кнопки управления ролями
    add_role_button = customtkinter.CTkButton(tab_roles, text="Добавить роль", command=add_role,border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    add_role_button.pack(side='left', fill="x", padx=100,pady=25)

    edit_role_button = customtkinter.CTkButton(tab_roles, text="Редактировать роль", command=edit_role, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    edit_role_button.pack(side='left', fill="x", padx=100,pady=25)

    delete_role_button = customtkinter.CTkButton(tab_roles, text="Удалить роль", command=delete_role, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    delete_role_button.pack(side='left', fill="x", padx=100,pady=25)


    # Создание таблицы пользователей
    users_table = ttk.Treeview(tab_users, columns=('ID', 'Имя', 'Фамилия', 'Почта', 'Статус'), show='headings')
    users_table.column('ID',  anchor='center', width=50)
    users_table.column('Имя',  anchor='center', width=150)
    users_table.column('Фамилия', anchor='center',  width=150)
    users_table.column('Почта',  anchor='center', width=200)
    users_table.column('Статус', anchor='center',  width=100)
    users_table.heading('ID', text='ID')
    users_table.heading('Имя', text='Имя')
    users_table.heading('Фамилия', text='Фамилия')
    users_table.heading('Почта', text='Почта')
    users_table.heading('Статус', text='Статус')
    users_table.pack(expand=True, fill='both')
    add_user_button = customtkinter.CTkButton(tab_users, text="Добавить пользователя", command=add_user_interface,border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    add_user_button.pack(side='left', fill="x", padx=25,pady=25)
    def on_user_select(event):
        selected = users_table.selection()
        state = 'normal' if selected else 'disabled'
        edit_user_button.configure(state=state)
        delete_user_button.configure(state=state)
        show_comments_button.configure(state=state)
        download_portfolio_button.configure(state=state)
    def on_skill_select(event):
        selected = skills_table.selection()
        state = 'normal' if selected else 'disabled'
        edit_skill_button.configure(state=state)
        delete_skill_button.configure(state=state)

    edit_user_button = customtkinter.CTkButton(tab_users, text="Изменить пользователя", command=edit_user_interface, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    edit_user_button.pack(side='left', fill="x", padx=25,pady=25)

    delete_user_button = customtkinter.CTkButton(tab_users, text="Удалить пользователя", command=delete_user_interface, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    delete_user_button.pack(side='left', fill="x", padx=25,pady=25)
    show_comments_button = customtkinter.CTkButton(tab_users, text="Показать комментарии", command=show_selected_user_comments, state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    show_comments_button.pack(side='left', fill="x", padx=25,pady=25)
    download_portfolio_button = customtkinter.CTkButton(tab_users, text="Получить портфолио", command=download_user_portfolio, state='disabled', border_width=1, border_color="#871b41", text_color="#f3f3f3", fg_color="#641c34", hover_color="#8c2749", corner_radius=1)
    download_portfolio_button.pack(side='left', fill="x", padx=25, pady=25)
    tab_control.pack(expand=1, fill='both')
    tab_control.bind('<<NotebookTabChanged>>', on_tab_changed)

    skills_table = ttk.Treeview(tab_skills, columns=('ID', 'Название'), show='headings')
    skills_table.column('ID', anchor='center', width=50)
    skills_table.column('Название', anchor='center', width=150)
    skills_table.heading('ID', text='ID')
    skills_table.heading('Название', text='Название')
    skills_table.pack(expand=True, fill='both')
    add_skill_button = customtkinter.CTkButton(tab_skills, text="Добавить скилл",border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=add_skill_interface)
    add_skill_button.pack(side='left', padx=25,pady=25)
    edit_skill_button = customtkinter.CTkButton(tab_skills, text="Редактировать скилл",state='disabled', border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1,command=edit_skill_interface)
    edit_skill_button.pack(side='left', padx=25,pady=25)

    delete_skill_button = customtkinter.CTkButton(tab_skills, text="Удалить скилл", state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1,command=delete_skill_interface)
    delete_skill_button.pack(side='left',padx=25, pady=25)
    fetch_projects()  # Загрузка данных проектов
    # fetch_users() можно добавить здесь, если нужна автоматическая загрузка пользователей

    skills_table.bind("<<TreeviewSelect>>", on_skill_select)
    users_table.bind("<<TreeviewSelect>>", on_user_select)
    main_window.mainloop()

def add_skill_interface():
    add_skill_window = customtkinter.CTkToplevel()
    add_skill_window.title("Добавление скилла")

    label_name = customtkinter.CTkLabel(add_skill_window, text="Название скилла")
    label_name.pack(pady=(25, 0))
    entry_name = customtkinter.CTkEntry(add_skill_window)
    entry_name.pack(padx=25)

    submit_button = customtkinter.CTkButton(add_skill_window, text="Добавить", border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1,command=lambda: submit_new_skill(entry_name.get(), add_skill_window))
    submit_button.pack(pady=25)

def submit_new_skill(name, window):
    data = {'Название': name}
    response = requests.post('http://ideal-web.site:5000/create_skill', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        window.destroy()
        fetch_and_display_skills()
    else:
        print("Ошибка при добавлении скилла")
def edit_skill_interface():
    selected_item = skills_table.selection()
    if not selected_item:
        print("Скилл не выбран")
        return

    skill_id = skills_table.item(selected_item[0], "values")[0]
    current_name = skills_table.item(selected_item[0], "values")[1]

    edit_skill_window = customtkinter.CTkToplevel()
    edit_skill_window.title(f"Редактирование скилла {skill_id}")

    label_name = customtkinter.CTkLabel(edit_skill_window, text="Название скилла")
    label_name.pack(pady=(25, 0))
    entry_name = customtkinter.CTkEntry(edit_skill_window)
    entry_name.pack(padx=25)
    entry_name.insert(0, current_name)

    submit_button = customtkinter.CTkButton(edit_skill_window, text="Сохранить", border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: submit_skill_changes(skill_id, entry_name.get(), edit_skill_window))
    submit_button.pack(pady=25)

def submit_skill_changes(skill_id, name, window):
    data = {'Название': name}
    response = requests.put(f'http://ideal-web.site:5000/skills/{skill_id}', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        window.destroy()
        fetch_and_display_skills()
    else:
        print("Ошибка при редактировании скилла")
def delete_skill_interface():
    selected_item = skills_table.selection()
    if not selected_item:
        print("Скилл не выбран")
        return

    skill_id = skills_table.item(selected_item[0], "values")[0]
    response = requests.delete(f'http://ideal-web.site:5000/skills/{skill_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.status_code == 200:
        fetch_and_display_skills()
    else:
        print("Ошибка при удалении скилла")
def fetch_and_display_skills():
    global skills_table
    response = requests.get('http://ideal-web.site:5000/skills', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        skills = response.json()['skills']
        for i in skills_table.get_children():
            skills_table.delete(i)
        for skill in skills:
            skills_table.insert('', 'end', values=(skill['ID_навыков'], skill['Название']))
    else:
        print("Ошибка при получении списка скиллов")

def show_selected_user_comments():
    selected_item = users_table.selection()
    if not selected_item:
        print("Пользователь не выбран")
        return

    user_id = users_table.item(selected_item[0], "values")[0]
    show_user_comments(user_id)

def show_user_comments(user_id):
    comments_window = customtkinter.CTkToplevel()
    comments_window.title(f"Комментарии пользователя {user_id}")

    comments_table = ttk.Treeview(comments_window, columns=('ID', 'Дата', 'Текст'), show='headings')
    comments_table.column('ID', width=50)
    comments_table.column('Дата', width=100)
    comments_table.column('Текст', width=250)
    comments_table.heading('ID', text='ID')
    comments_table.heading('Дата', text='Дата')
    comments_table.heading('Текст', text='Текст')
    comments_table.pack(expand=True, fill='both')
    delete_comment_button = customtkinter.CTkButton(comments_window, text="Удалить комментарий", state='disabled', border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1,command=lambda: delete_user_comment(user_id, comments_table))
    delete_comment_button.pack(side='right',pady=25,padx=25)
    load_user_comments(user_id, comments_table)
    def on_comment_select(event):
        selected = comments_table.selection()
        delete_comment_button.configure(state='normal' if selected else 'disabled')

# Привязка обработчика к таблице комментариев
    comments_table.bind("<<TreeviewSelect>>", on_comment_select)
def delete_user_comment(user_id, comments_table):
    selected_item = comments_table.selection()
    if not selected_item:
        print("Комментарий не выбран")
        return

    comment_id = comments_table.item(selected_item[0], "values")[0]
    response = requests.delete(f'http://ideal-web.site:5000/delete_comment/{comment_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.status_code == 200:
        load_user_comments(user_id, comments_table)
    else:
        print("Ошибка при удалении комментария")
def load_user_comments(user_id, comments_table):
    selected_item = users_table.selection()
    if not selected_item:
        print("Пользователь не выбран")
        return
    user_id = users_table.item(selected_item[0], "values")[0]
    response = requests.get(f'http://ideal-web.site:5000/get_comments_by_user/{user_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        comments = response.json()['comments']
        for comment in comments:
            comments_table.insert('', 'end', values=(comment['ID_комментария'], comment['Дата'], comment['Текст']))
    else:
        print("Ошибка при получении комментариев пользователя")
# Функция для добавления новой роли
def add_role():
    add_role_window = customtkinter.CTkToplevel()
    add_role_window.title("Добавление роли")

    label_name = customtkinter.CTkLabel(add_role_window, text="Название роли")
    label_name.pack(padx=25,pady=(25,0),)

    entry_name = customtkinter.CTkEntry(add_role_window)
    entry_name.pack(pady=(0,15),padx=25)

    add_button = customtkinter.CTkButton(add_role_window, text="Добавить", border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: create_role(entry_name.get(), add_role_window))
    add_button.pack(pady=(20,25))

# Функция для создания роли (отправка данных на сервер)
def create_role(role_name, window):
    data = {'Название': role_name}
    response = requests.post('http://ideal-web.site:5000/create_role', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    
    if response.status_code == 200:
        window.destroy()
        fetch_and_display_roles()  # Обновить список ролей
    else:
        print("Ошибка при создании роли")

# Функция для редактирования выбранной роли
def edit_role():
    selected_item = roles_table.selection()
    if not selected_item:
        print("Роль не выбрана")
        return

    role_id = roles_table.item(selected_item[0], "values")[0]
    edit_role_window = customtkinter.CTkToplevel()
    edit_role_window.title(f"Редактирование роли {role_id}")

    # Получаем информацию о выбранной роли
    role_info = fetch_role_info(role_id)

    label_name = customtkinter.CTkLabel(edit_role_window, text="Название роли")
    label_name.pack(pady=(25,0))

    entry_name = customtkinter.CTkEntry(edit_role_window)
    entry_name.pack(padx=25)
    entry_name.insert(0, role_info['Название'])  # Загружаем название роли в поле ввода

    save_button = customtkinter.CTkButton(edit_role_window, text="Сохранить",border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: save_role_changes(role_id, entry_name.get(), edit_role_window))
    save_button.pack(pady=25)

def fetch_role_info(role_id):
    response = requests.get(f'http://ideal-web.site:5000/role/{role_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        return response.json()['role']  # Предполагается, что сервер возвращает информацию о роли внутри ключа 'role'
    else:
        print("Ошибка при получении информации о роли: ", response.text)
        return None
    
# Функция для сохранения изменений роли
def save_role_changes(role_id, role_name, window):
    # Проверка на пустое название роли
    if not role_name.strip():
        print("Ошибка: Название роли не может быть пустым")
        return

    data = {'Название': role_name}
    response = requests.put(f'http://ideal-web.site:5000/roles/{role_id}', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.status_code == 200:
        print("Роль успешно обновлена")
        window.destroy()
        fetch_and_display_roles()
    else:
        error_message = response.json().get('message', 'Ошибка при сохранении изменений роли')
        print(error_message)
# Функция для удаления выбранной роли
def delete_role():
    selected_item = roles_table.selection()
    if not selected_item:
        print("Роль не выбрана")
        return

    role_id = roles_table.item(selected_item[0], "values")[0]

    response = requests.delete(f'http://ideal-web.site:5000/roles/{role_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.status_code == 200:
        print("Роль успешно удалена")
        fetch_and_display_roles()
    else:
        error_message = response.json().get('message', 'Ошибка при удалении роли')
        print(error_message)
def on_project_double_click(event):
    # Получаем выбранный элемент
    item = table_projects.selection()[0]
    project_id = table_projects.item(item, "values")[0]
    show_project_users(project_id)

def show_project_users(project_id):
    global edit_user_button, delete_user_button

    users_window = customtkinter.CTkToplevel()
    users_window.title(f"Участники проекта {project_id}")

    users_table = ttk.Treeview(users_window, columns=('ID', 'Имя', 'Фамилия', 'Роль'), show='headings')
    users_table.column('ID', width=50)
    users_table.column('Имя', width=150)
    users_table.column('Фамилия', width=150)
    users_table.column('Роль', width=100)
    users_table.heading('ID', text='ID')
    users_table.heading('Имя', text='Имя')
    users_table.heading('Фамилия', text='Фамилия')
    users_table.heading('Роль', text='Роль')
    users_table.pack(expand=True, fill='both')
    users_table.bind("<<TreeviewSelect>>", on_user_select)

    add_user_button = customtkinter.CTkButton(users_window, text="Добавить", border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: add_user(project_id))
    add_user_button.pack(side='left',padx=15,)

    edit_user_button = customtkinter.CTkButton(users_window, text="Редактировать", state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: edit_user(project_id, users_table))
    edit_user_button.pack(side='left',pady=25)

    delete_user_button = customtkinter.CTkButton(users_window, text="Удалить", state='disabled',border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: delete_user(project_id, users_table))
    delete_user_button.pack(side='left',padx=15)

    project_users = fetch_project_users(project_id)
    for user in project_users:
        users_table.insert('', 'end', values=(user['ID_участника'], user['Имя'], user['Фамилия'], user['Роль']))

def on_user_select(event):
    selected = event.widget.selection()
    state = 'normal' if selected else 'disabled'
    edit_user_button.configure(state=state)
    delete_user_button.configure(state=state)
    show_comments_button.configure(state=state) 


def edit_user(project_id, users_table):
    selected_item = users_table.selection()[0]
    user_id = users_table.item(selected_item, "values")[0]

    edit_user_window = customtkinter.CTkToplevel()
    edit_user_window.title(f"Редактирование участника {user_id}")

    roles = fetch_roles()  # Получаем список ролей

    label_role = customtkinter.CTkLabel(edit_user_window, text="Роль")
    label_role.pack(pady=(25,0))
    role_combobox = customtkinter.CTkComboBox(edit_user_window, values=[role['Название'] for role in roles])
    role_combobox.pack(padx=25)

    save_button = customtkinter.CTkButton(edit_user_window, text="Сохранить",border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: save_user_role_change(user_id, role_combobox.get(), edit_user_window, project_id))
    save_button.pack(pady=25)
def save_user_role_change(user_id, role_name, window, project_id):
    # Найти ID роли по ее названию
    role_id = next((role['ID_роли'] for role in fetch_roles() if role['Название'] == role_name), None)
    
    if role_id is None:
        print("Роль не найдена")
        return

    # Обновление роли пользователя
    data = {'ID_роли': role_id}
    response = requests.put(f'http://ideal-web.site:5000/update_user_role/{user_id}', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    
    if response.status_code == 200:
        window.destroy()
        show_project_users(project_id)
    else:
        print("Ошибка при сохранении изменений роли участника")


def add_user(project_id):
    add_user_window = customtkinter.CTkToplevel()
    add_user_window.title("Добавление участника")

    # Получение данных о пользователях и ролях
    users = fetch_users()
    roles = fetch_roles()

    # Создание выпадающего списка пользователей
    label_user = customtkinter.CTkLabel(add_user_window, text="Выберите пользователя")
    label_user.pack(pady=(25,5))
    user_combobox = customtkinter.CTkComboBox(add_user_window, values=[f"{user['Почта']} (ID: {user['ID_участника']})" for user in users])
    user_combobox.pack(padx=25)

    # Создание выпадающего списка ролей
    label_role = customtkinter.CTkLabel(add_user_window, text="Выберите роль")
    label_role.pack(pady=(25,5))
    role_combobox = customtkinter.CTkComboBox(add_user_window, values=[f"{role['Название']} (ID: {role['ID_роли']})" for role in roles])
    role_combobox.pack(padx=25)

    # Кнопка для добавления пользователя
    add_button = customtkinter.CTkButton(add_user_window, text="Добавить",border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: add_new_user_to_project(project_id, user_combobox.get(), role_combobox.get(), add_user_window))
    add_button.pack(pady=25)
    
def add_new_user_to_project(project_id, user_info, role_info, window):
    user_email = user_info.split(' (ID: ')[0]  # Извлекаем email пользователя из информации в combobox
    role_id = role_info.split(' (ID: ')[1].split(')')[0]  # Извлекаем ID роли из информации в combobox

    data = {
        'ID_проекта': project_id,
        'Email': user_email,  # Теперь передаем email вместо ID пользователя
        'ID_роли': role_id
    }
    response = requests.post('http://ideal-web.site:5000/add_user_to_project', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.status_code == 200:
        window.destroy()
        show_project_users(project_id)
    else:
        print("Ошибка при добавлении пользователя к проекту")
def fetch_users():
    response = requests.get('http://ideal-web.site:5000/users', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        return response.json()['users']
    else:
        print("Ошибка при получении списка пользователей")
        return []

def fetch_roles():
    response = requests.get('http://ideal-web.site:5000/roles', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        return response.json()['roles']
    else:
        print("Ошибка при получении списка ролей")
        return []
    
def delete_user(project_id, users_table):
    selected_item = users_table.selection()[0]
    user_id = users_table.item(selected_item, "values")[0]

    response = requests.delete(f'http://ideal-web.site:5000/remove_user_from_project/{project_id}/{user_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    
    if response.status_code == 200:
        show_project_users(project_id)
    else:
        print("Ошибка при удалении участника")
def fetch_project_users(project_id):
    response = requests.get(f'http://ideal-web.site:5000/project_users/{project_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        return response.json()['users']  # Assuming the response contains a 'users' key
    else:
        # Handle the error appropriately
        print("Failed to fetch project users")
        return []
def fetch_projects():
    response = requests.get('http://ideal-web.site:5000/projects', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        projects = response.json()['projects']
        for i in table_projects.get_children():
            table_projects.delete(i)
        for project in projects:
            project_id = project['ID_проекта']
            project_row = table_projects.insert('', 'end', values=(project_id, project['Название_проекта'], project['Описание'], project['Статус']))
def on_project_select(event):
    selected = table_projects.selection()
    state = 'normal' if selected else 'disabled'
    edit_button.configure(state=state)
    delete_button.configure(state=state)
    members_button.configure(state=state)
    comments_button.configure(state=state)
    skills_button.configure(state=state)

def edit_selected_project():
    selected_item = table_projects.selection()[0]
    project_id = table_projects.item(selected_item, "values")[0]
    edit_project(project_id)

def delete_selected_project():
    selected_item = table_projects.selection()[0]
    project_id = table_projects.item(selected_item, "values")[0]
    delete_project(project_id)

def show_selected_project_members():
    selected_item = table_projects.selection()[0]
    project_id = table_projects.item(selected_item, "values")[0]
    show_project_users(project_id)

def create_new_project():
    new_project_window = customtkinter.CTkToplevel()
    new_project_window.title("Создание нового проекта")

    label_name = customtkinter.CTkLabel(new_project_window, text="Название проекта")
    label_name.pack(pady=(25,0))

    entry_name = customtkinter.CTkEntry(new_project_window)
    entry_name.pack(padx=25)

    label_description = customtkinter.CTkLabel(new_project_window, text="Описание проекта")
    label_description.pack(pady=(25,0))

    entry_description = customtkinter.CTkEntry(new_project_window)
    entry_description.pack(padx=25)

    create_button = customtkinter.CTkButton(new_project_window, text="Создать", border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1, command=lambda: create_project(entry_name.get(), entry_description.get(), new_project_window))
    create_button.pack(pady=25)

def create_project(name, description, window):
    # Здесь вы отправляете запрос на сервер для создания нового проекта
    data = {
        'Название_проекта': name,
        'Описание': description
    }
    response = requests.post('http://ideal-web.site:5000/create_project', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

    if response.status_code == 200:
        # Если проект успешно создан, обновляем список проектов и закрываем окно создания
        fetch_projects()
        window.destroy()
    else:
        # Обработка ошибки
        print("Ошибка при создании проекта")

def delete_project(project_id):
    response = requests.delete(f'http://ideal-web.site:5000/delete_project/{project_id}', headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
    if response.status_code == 200:
        fetch_projects()  # Обновляем список проектов
def save_project_changes(project_id, name, description, status, edit_window):
    # Создайте запрос к серверу для сохранения изменений проекта
    data = {}
    if name:
        data['Название_проекта'] = name
    if description:
        data['Описание'] = description
    # Для статуса, предполагая, что он всегда должен быть выбран:
    data['Статус'] = status

    # Только если есть что обновлять, отправляем запрос
    if data:
        response = requests.put(f'http://ideal-web.site:5000/edit_project/{project_id}', json=data, headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})
        
        if response.status_code == 200:
            # Если изменения успешно сохранены, закройте окно редактирования
            edit_window.destroy()
            # Обновите список проектов
            fetch_projects()
        else:
            # В случае ошибки вы можете предпринять соответствующие действия, например, отобразить сообщение об ошибке
            print("Ошибка при сохранении изменений проекта:", response.json().get('message', ''))
    else:
        print("Нет данных для обновления")
        edit_window.destroy()
def edit_project(project_id):
    edit_window = customtkinter.CTkToplevel()
    edit_window.title(f"Редактирование проекта {project_id}")

    label_name = customtkinter.CTkLabel(edit_window, text="Название проекта")
    label_name.pack(padx=50,pady=(25,0))

    entry_name = customtkinter.CTkEntry(edit_window)
    entry_name.pack()

    label_description = customtkinter.CTkLabel(edit_window, text="Описание проекта")
    label_description.pack(padx=50,pady=(25,0))

    entry_description = customtkinter.CTkEntry(edit_window)
    entry_description.pack()

    label_status = customtkinter.CTkLabel(edit_window, text="Статус проекта")
    label_status.pack(padx=50,pady=(25,0))

    status_combobox = customtkinter.CTkComboBox(edit_window, values=[
        'На рассмотрении', 'Одобрен', 'В процессе выполнения', 
        'Отправлен на ревью', 'Ревью пройдено', 'Выполнен', 'Заморожен'
    ])
    status_combobox.pack()

    # Кнопка для сохранения изменений
    save_button = customtkinter.CTkButton(edit_window, text="Сохранить", command=lambda: save_project_changes(project_id, entry_name.get(), entry_description.get(), status_combobox.get(), edit_window),border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1)
    save_button.pack(padx=50,pady=(25,20))
def fetch_and_display_roles():
    global roles_table
    roles = fetch_roles()
    for i in roles_table.get_children():
        roles_table.delete(i)
    for role in roles:
        roles_table.insert('', 'end', values=(role['ID_роли'], role['Название']))

login_window = customtkinter.CTk()
login_window.geometry("1024x768")
login_window.title("Авторизация")

# Создаем фрейм для размещения элементов
frame = customtkinter.CTkFrame(login_window, border_width=1,border_color="#871b41")
frame.place(relx=0.5, rely=0.5, anchor="center")

# Создаем и размещаем элементы на фрейме
label_auth = customtkinter.CTkLabel(frame, text="Авторизация", font=("Arial", 35))
label_auth.pack(pady=(40,25))
# Увеличиваем размер текста "Почта"
label_username = customtkinter.CTkLabel(frame, text="Email", font=("Arial", 17))
label_username.pack(pady=(15,0),padx=(0,190))

# Увеличиваем ширину полей для ввода
entry_username = customtkinter.CTkEntry(frame, width=250)
entry_username.pack(pady=(5, 0),padx=35)

label_password = customtkinter.CTkLabel(frame, text="Пароль",font=("Arial", 17))
label_password.pack(pady=(20,0),padx=(0,175))

entry_password = customtkinter.CTkEntry(frame, show="*", width=250)
entry_password.pack(pady=5, padx=35)

label_status = customtkinter.CTkLabel(frame, text="")
label_status.pack(pady=(5,0))
# Добавляем отступ сверху для кнопки "Войти"
button_login = customtkinter.CTkButton(frame, text="Войти", command=login,border_width=1,border_color="#871b41",text_color="#f3f3f3",fg_color="#641c34",hover_color="#8c2749",corner_radius=1,width=180,height=35,font=("Arial", 15))
button_login.pack(pady=(5,40),padx=(0,0),side="right")


login_window.mainloop()
