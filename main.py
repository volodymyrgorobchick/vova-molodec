from customtkinter import *
from tkinter import filedialog
from PIL import Image


import io, base64, socket, threading


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
       
        self.title("LogiTalk")
        self.geometry("800x600")


        self.frame = CTkFrame(self, width=0, height=self.winfo_height())
        self.frame.place(x=0, y=0)
        self.frame.pack_propagate(False)  # Не дозволяє фрейму змінювати розміри
       
        self.is_open = False
        self.frame_width = 0
       
        self.label = CTkLabel(self.frame, text='Ваше Ім`я')
        self.label.pack(pady=30)
        self.entry = CTkEntry(self.frame)
        self.entry.pack()
       
        self.name_btn = CTkButton(self.frame, text='Ввести', command=self.change_name)
        self.name_btn.pack(pady=20)
       
        self.label_theme = CTkOptionMenu(self.frame, values=['Система','Темна', 'Світла'], command=self.change_theme)
        self.label_theme.pack(side='bottom', pady=20)
        self.theme = None
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
       
        # властивості для роботи програми (ім'я, люди що онлайн)
        self.user_name = 'Dmytro'
        self.online = None


        # лейбл для відображення онлайн користувачів
        self.chat_online = CTkLabel(self, text="Онлайн", height=self.btn.winfo_height())
        self.chat_online.place(x=0, y=0)
       
        # фрейм для відображення чату, він прокручується
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)


        # ентрі для введення повідомлення, placeholder_text - текст підказка
        self.message_entry = CTkEntry(self, placeholder_text="Введіть повідомлення", height=40)
        self.message_entry.place(x=0, y=0)
       
        # бінд для прив'язки клавіші або комбінації клавіш до функції (заміна для command в деяких об'єктах)
        self.message_entry.bind("<Return>", self.send_message)
       
        # кнопка для відправлення повідомлення, command - функція, яка викликається при натисканні кнопки
        self.send_btn = CTkButton(self, text=">", width=50, height=40, command=self.send_message)
        self.send_btn.place(x=0, y=0)
       
        # кнопка для вибору зображення, command - функція, яка викликається при натисканні кнопки
        self.open_btn = CTkButton(self, text="📂", width=50, height=40, command=self.open_img)
        self.open_btn.place(x=0, y=0)
       
        # властивості для роботи прев'ю зображення
        self.file_name = None
        self.raw = None
        self.image_to_send = CTkLabel(self, text="")
       
        # бінд для прив'язки клавіші, щоб видаляти картинку при кліку на неї)
        self.image_to_send.bind("<Button-1>", self.remove_image)
   
        self.adaptation_ui() # виклик методу адаптації інтерфейсу
       
        try:
            # AF_INET - ipv4, SOCK_STREAM - tcp протокол
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('4.tcp.eu.ngrok.io', 19339))
           
            hello = f'TEXT@{self.user_name}@[SYSTEM] {self.user_name} підключився(лась) до чату!'
            self.socket.sendall(hello.encode('utf-8'))
           
            threading.Thread(target=self.recieve_message, daemon=True).start()
        except Exception as e:
            self.add_message(f'Не вдалося підключитися до сервера: {e}')
   
    # метод для адаптації інтерфейсу під розмір вікна
    def adaptation_ui(self):
        w_width = self.winfo_width() # отримуємо ширину вікна
        w_height = self.winfo_height() # отримуємо висоту вікна


        self.chat_field.place(
            x=self.frame.winfo_width(),
            y=self.btn.winfo_height()
        ) # розміщуємо фрейм чату
        self.chat_field.configure(
            width=w_width-self.frame.winfo_width()-20,
            height=w_height-self.btn.winfo_height()- 45
        ) # задаємо ширину і висоту фрейму чату
       
        self.send_btn.place(
            x = w_width - 50,
            y = w_height - 40
        ) # розміщуємо кнопку відправлення повідомлення
        self.open_btn.place(
            x = w_width - 105,
            y = w_height - 40
        ) # розміщуємо кнопку вибору зображення
       
        self.message_entry.configure(
            width = self.open_btn.winfo_x() - self.frame.winfo_width() - 5,
            height = 40
        ) # задаємо ширину і висоту ентрі для введення повідомлення
        self.message_entry.place(
            x = self.frame.winfo_width(),
            y = w_height - 40
        ) # розміщуємо ентрі для введення повідомлення
       
        self.chat_online.place(
            x = self.btn.winfo_width() + 20,
            y = 5
        ) # розміщуємо лейбл для відображення онлайн користувачів
       
        if self.raw:
            self.image_to_send.configure(
                image=CTkImage(Image.open(self.file_name), size=(100,100))
            )
            self.image_to_send.place(
                x=self.frame.winfo_width() + 20,
                y = self.message_entry.winfo_y() - 100
            )
       
        self.after(100, self.adaptation_ui) # викликаємо метод адаптації інтерфейсу через 100 мс
       
    # метод для зміни теми програми
    # set_appearance_mode - функція, яка змінює тему програми (темна, світла, система)
    def change_theme(self, value):
        if value == 'Темна':
            set_appearance_mode('dark')
        elif value == 'Світла':
            set_appearance_mode('light')
        elif value == 'Система':
            set_appearance_mode('system')
   
    # метод для зміни імені користувача
    def change_name(self):
        if self.entry.get()!='':
            self.user_name = self.entry.get() # get() - отримує текст з ентрі
            self.label.configure(text=self.user_name) # configure() - змінює текст в лейблі
            self.entry.delete(0, 'end') # delete() - очищує текст в ентрі
   
    def toggle_show_menu(self):
        if self.is_open: # якщо меню відкрите, закриваємо його
            self.is_open = False # тепер меню закрите
            self.close_menu() # закриваємо меню
        else: # якщо меню закрите, відкриваємо його
            self.is_open = True # тепер меню відкрите
            self.open_menu() # відкриваємо меню
           
    def open_menu(self):
        # якщо розмір меню менше 200, то збільшуємо його на 5
        if self.frame_width <= 200:
            self.frame_width += 5
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            # якщо розмір меню більше 30, то змінюємо текст на "◀️" і починаємо міняти ширину кнопки
            if self.frame_width >= 30:
                self.btn.configure(text='◀️', width=self.frame_width)
        # якщо меню відкрите, то відкриваємо його далі
        if self.is_open:
            self.after(1, self.open_menu)
   
    def close_menu(self):
        # якщо розмір меню більше 0, то зменшуємо його на 5
        if self.frame_width >= 0:
            self.frame_width -= 5
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(text='▶️', width=self.frame_width)
        if not self.is_open:
            self.after(1, self.close_menu)
   
    def open_img(self):
        self.file_name = filedialog.askopenfilename(
            filetypes=[("Зображення", "*.png;*.jpg;*.jpeg;")]
        )
        if not self.file_name:
            return
        # r - читати, w - записати, a - дописати, rb - читати бінарний, wb - записати бінарний, ab - дописати бінарний
        with open(self.file_name, 'rb') as f: # with - за допомогою open - відкрити (повний шлях до файлу, тип доступу до файлу)
            self.raw = f.read() # прочитати файл
        return self.raw
           
    def send_message(self):
        message = self.message_entry.get() # отримуємо текст з поля
        if message and not self.raw: # якщо є повідомлення і нема картинки
            self.add_message(f'{self.user_name}: {message}') # відображаємо повідомлення
            data = f'TEXT@{self.user_name}@{message}\n' # тип повідомлення, ім'я користувача, повідомлення
            try: # намагаємось відправити повідомлення
                self.socket.sendall(data.encode())
            except:
                pass
        elif self.raw: # якщо в є зображення
            b64_data = base64.b64encode(self.raw).decode() # кодуємо і декодуємо картинку для відправки
            self.add_message(f'{self.user_name}: {message}', img=self.resize_image(Image.open(self.file_name))) # відображаємо повідомлення
            data = f'IMAGE@{self.user_name}@{message}@{b64_data}\n' # тип повідомлення, ім'я користувача, повідомлення, зображення
            try: # намагаємось відправити повідомлення
                self.socket.sendall(data.encode())
            except:
                pass
            self.remove_image()
        self.message_entry.delete(0,'end')
   
    def remove_image(self, event=None):
        self.image_to_send.place_forget() # place_forget() - відкріпити віджет від програми
        self.raw = None
        self.file_name = None
   
    def recieve_message(self): # отримання повідомлень
        buffer = '' # рядок для збереження всіх повідомлень
        while True:
            try:
                message = self.socket.recv(16384) # отримання повідомлень з максимальною довжиною 16384 біти
                buffer += message.decode('utf-8', errors='ignore') # розкодовуємо повідомлення з стандартом utf-8 і ігноруємо помилки
                while '\n' in buffer: # якщо отримано більше 1 повідомлення перебираємо їх як окремі
                    line, buffer = buffer.split('\n', 1) # розділюємо рядок на елементи списку \n 1 - кількість розрізів
                    self.handle_line(line.strip()) # відображаємо повідомлення, strip для забирання пробілів у кінці рядка
            except:
                break
           
    def handle_line(self, line): # відображення отриманих повідомлень
        if not line: # якщо немає повідомлення то повертаємось і нічого не робимо
            return
        parts = line.split('@') # розбиваємо повідомлення на кусочки
        message_type = parts[0] # перша частина повідомлення визначає нього тип (IMAGE|TYPE)
        if message_type == 'TEXT':
            self.add_message(f'{parts[1]}: {parts[2]}') # додаємо повідомлення до вікна parts[1] - хто пише, parts[2] - повідомлення
        elif message_type == 'IMAGE':
            try:
                image_data = base64.b64decode(parts[3]) # перетворити картинку в біти
                img = io.BytesIO(image_data) # зібрати біти в купу
                img = Image.open(img) # відкрити картинку
                img = self.resize_image(img) # змінити розміри
                self.add_message(f'{parts[1]}: {parts[2]}', img=img) # додаємо до програми повідомлення з картинкою
            except Exception as e:
                self.add_message(f'Помилка отримання зображення:', e)
   
    # img=None що якщо не передаєм картинку то функція не поламається (воно очікує картинку але не обов'язково)
    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color='#636363') # фон для повідомлень
        message_frame.pack(padx=5,pady=5, anchor='w') # anchor підсовує до сторони
       
        w_size = self.winfo_width() // 2 - 220 # обмеження ширини повідомлення
       
        if not img: # якщо немає картинки
            CTkLabel(message_frame, text=message, text_color='white', justify='left', wraplength=w_size).pack(pady=10,padx=10)
        else: # якщо є картинка
            CTkLabel(message_frame, text=message, text_color='white', justify='left', wraplength=w_size, image=img, compound='top').pack(pady=10,padx=10)
       
   
    def resize_image(self, image):
        # Image.open(filename)
        width, height = image.size # отримуємо ширину і висоту картинки
        new_width = 300 # нова максимальна ширина
       
        if width <= new_width:
            if height < 300:
                return CTkImage(image, size=(width, height))
            else:
                new_height = 300
                new_width = int(width*new_height/height)
        new_height = int(height*new_width/width)
       
        return CTkImage(image, size=(new_width, new_height))
       
   
window = MainWindow()
window.mainloop()

