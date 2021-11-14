import threading
import socket
import tkinter
from tkinter import simpledialog
from tkinter import scrolledtext

HOST = "127.0.0.1"

PORT = 5050


class Client:
    def __init__(self, host, port):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ADDR = (host, port)
        self.sock.connect(self.ADDR)
        message = tkinter.Tk()
        message.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose your nickname:", parent=message)
        self.gui = False
        self.running = True

        self.sock.send(self.nickname.encode())
        gui_thread = threading.Thread(target=self.gui_loop)
        gui_thread.start()
        message_handler = threading.Thread(target=self.handle_messages, args=())
        message_handler.start()

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode())
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text=f"Username:{self.nickname}", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)


        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.config(state="disabled")
        self.text_area.pack(pady=5,padx=20)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="send", command=self.write)
        self.send_button.pack(padx=20, pady=5)
        self.send_button.config(font=("Arial", 12))

        self.gui = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def handle_messages(self):
        while self.running:
            # try:
            message = self.sock.recv(1024)
            if self.gui:
                self.text_area.config(state='normal')
                self.text_area.insert("end", message)
                self.text_area.yview("end")
                self.text_area.config(state="disabled")
            # except Exception as r:
            #     print(f"errrrrrrrrror{r}")


client = Client(HOST, PORT)
