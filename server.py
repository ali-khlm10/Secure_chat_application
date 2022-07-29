import socket
from threading import Thread
import os
import pickle


clients = []
client_names = []
Conference_people = []



def Convert_to_pickle(data):
    return pickle.dumps(data)


def Extract_from_Pickle(data):
    return pickle.loads(data)


SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5545  

client_sockets = set()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")


def listen_for_client(cs):
    while True:
        try:
            msg = Extract_from_Pickle(cs.recv(4096))
            # print(msg)

            if len(msg) == 2 and msg[1] == 'new client':
                flag = 1
                for user in client_names:
                    if user == msg[0]:
                        flag = 0
                        break
                if flag == 0:
                    cs.send(Convert_to_pickle('UserName added before'))
                    break
                else:
                    clients.append([msg[0], cs])
                    client_names.append(msg[0])
                    print(clients)
                    print(client_names)
                    print(f"[+] {msg[0]} connected.")
                    client_sockets.add(cs)
                    # print(client_socket)
                    cs.send(Convert_to_pickle('new client added'))
                    for cl in clients_sockets:
                        cl.send(Convert_to_pickle(['members', client_names]))


            elif len(msg) == 5 and msg[0] == "new message":
                print(f'received from {msg[3]}')
                for client in clients:
                    if msg[2] == client[0]:
                        client[1].send(Convert_to_pickle(
                            ['New message received', msg[1], msg[3], msg[4]]))
                        break

            elif len(msg) == 4 and msg[0] == "Conference":
                global Conference_people
                Conference_people.clear()
                Conference_people.append(msg[1])


                for client in clients:
                    for friend in msg[2]:
                        if friend == client[0]:
                            client[1].send(Convert_to_pickle(msg))

            elif msg[0] == 'yes':
                Conference_people.append(msg[1])

            elif msg[0] == 'left':
                Conference_people.remove(msg[1])
                for client in clients:
                    for conf_name in Conference_people:
                        if client[0] == conf_name and client[0] != msg[1]:
                            client[1].send(Convert_to_pickle(['Left conference',f'{msg[1]} left conference']))


            elif msg[0] == 'Conference message':
                # print(f'received : {msg[2]}')
                for client in clients:
                    for conf_name in Conference_people:
                        if client[0] == conf_name and client[0] != msg[1]:
                            client[1].send(Convert_to_pickle(['Conference message',msg[1],msg[2],msg[3]]))

            elif msg[0] == 'Not data':
                print(msg[1])

            else:
                pass


        except ConnectionResetError as er:
            print(er)
            break

        except Exception as e:
            if e == 'keyError':
                print(e)
                break
            os.system('cls')
            # print(f"[!] Error: {e}")
            client_sockets.remove(cs)
        else:
            pass


while True:
    client_socket, client_address = s.accept()
    s_thread = Thread(target=listen_for_client, args=(client_socket,))
    s_thread.daemon = True
    s_thread.start()

for cs in client_sockets:
    cs.close()
s.close()
