import socket
import threading
import sqlite3

HOST = "127.0.0.1"


PORT = 5050
open("CHAT.db", "w")
open("CHAT.db-journal", "w")

class Server:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = {}
        self.idOfMessages = 0
        self.conn = sqlite3.connect("CHAT.db", check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE chat (id INTEGER , message TEXT , fromClient TEXT, toClient TEXT)")
        self.sock.bind((host, port))
        self.sock.listen(100)
        print("[SERVER] Running...")
        print('[SERVER] Running on host: ' + str(host))
        print('[SERVER] Running on port: ' + str(port))

        while True:
            client, address = self.sock.accept()

            username = client.recv(1024).decode()
            # qqq = cursor.execute("")
            print('New connection. Username: ' + str(username))
            self.broadcast(f'{username} is connected to the server!!!. ')

            self.nicknames[client] = username

            self.clients.append(client)

            tr = threading.Thread(target=self.handle_client, args=(client, address,))
            tr.start()

    def broadcast(self, msg):
        for connection in self.clients:
            connection.send(msg.encode())

    def broadcastDistinctOne(self, message, thisClient):
        for client in self.clients:
            if client != thisClient:
                client.send(message)

    def privateMessage(self, fromClient, toClient, message):
        toClient.send(f'private message from {fromClient}: {message}'.encode("utf-8"))

        data2 = message[message.find(":") + 1:]
        Nickname_of_client = self.nicknames[toClient]
        self.cur.execute(
            f'INSERT INTO chat (id, message, fromClient, toClient) VALUES({self.idOfMessages} , "{data2}","{fromClient}","{Nickname_of_client}")')

        self.idOfMessages = +1

    def handle_client(self, client, address):
        while True:
            try:
                message = client.recv(1024)
            except:
                client.shutdown(socket.SHUT_RDWR)
                self.clients.remove(client)
                print(str(self.nicknames[client]) + ' left the server.')
                self.broadcast(str(self.nicknames[client]) + ' has left the server.')
                break

            if message.decode() != '' and "'" not in message.decode():
                msg = str(message.decode('utf-8'))  # era:/show my logs
                fromClient = msg[:msg.find(":")]
                logs = msg[msg.find(":") + 2:msg.find("\n")]

                if "/private to " in msg:
                    toClient = msg[msg.find("/private to") + 12:msg.find(" ", msg.find("/private to") + 12)]
                    lengthOfToClient = len(toClient)
                    data = msg[msg.find(toClient) + lengthOfToClient + 1:]
                    if toClient in self.nicknames.values():
                        for nickname in self.nicknames.items():
                            if toClient == nickname[1]:
                                toClient = nickname[0]  # client(socket obj)
                                break
                        else:
                            client.send("this person doesn't exist".encode())
                        self.privateMessage(fromClient, toClient, data)
                    else:
                        client.send("this person doesn't exist".encode())

                elif logs == "/show my logs":
                    self.cur.execute(f"SELECT * FROM chat WHERE fromClient ='{fromClient}'")

                    dataFromDB = self.cur.fetchall()
                    for i in dataFromDB:
                        client.send(f"you sent to {i[3]}:{i[1]}\n".encode())
                else:
                    print('New message: ' + str(message.decode()))
                    fromClient = self.nicknames[client]
                    data = str(message.decode())
                    data2 = data[data.find(":") + 1:]
                    self.cur.execute(
                        f'INSERT INTO chat (id, message, fromClient, toClient) VALUES({self.idOfMessages} ,"{data2}","{fromClient}","chat")')
                    self.broadcastDistinctOne(message, client)
                    self.idOfMessages = +1
            else:
                client.send("Warning! do not use the quotation marks in the messages".encode())
server = Server(HOST, PORT)
