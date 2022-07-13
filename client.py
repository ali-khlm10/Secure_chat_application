# Security requirements
# ////////////////////////////////////////////////////////////////////////////////////////////////


import socket
from threading import Thread
import os
import pickle

import base64
import hashlib
from Cryptodome.Cipher import AES as domeAES
from Cryptodome.Random import get_random_bytes
from Crypto import Random
from Crypto.Cipher import AES as cryptoAES
import hmac

BLOCK_SIZE = cryptoAES.block_size


Shared_secret_key = "Clients secret key"

key = Shared_secret_key.encode()
__key__ = hashlib.sha256(key).digest()


def encrypt(raw):
    BS = cryptoAES.block_size
    def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    raw = base64.b64encode(pad(raw).encode('utf8'))
    iv = get_random_bytes(cryptoAES.block_size)
    cipher = cryptoAES.new(key=__key__, mode=cryptoAES.MODE_CFB, iv=iv)
    a = base64.b64encode(iv + cipher.encrypt(raw))
    IV = Random.new().read(BLOCK_SIZE)
    aes = domeAES.new(__key__, domeAES.MODE_CFB, IV)
    b = base64.b64encode(IV + aes.encrypt(a))
    return b


def decrypt(enc):
    passphrase = __key__
    encrypted = base64.b64decode(enc)
    IV = encrypted[:BLOCK_SIZE]
    aes = domeAES.new(passphrase, domeAES.MODE_CFB, IV)
    enc = aes.decrypt(encrypted[BLOCK_SIZE:])
    def unpad(s): return s[:-ord(s[-1:])]
    enc = base64.b64decode(enc)
    iv = enc[:cryptoAES.block_size]
    cipher = cryptoAES.new(__key__, cryptoAES.MODE_CFB, iv)
    b = unpad(base64.b64decode(cipher.decrypt(
        enc[cryptoAES.block_size:])).decode('utf8'))
    return b




def check_integrity(message_data):
    digest_maker = hmac.new(Shared_secret_key.encode(),
                            message_data.encode(), hashlib.sha512)
    return digest_maker.hexdigest()



# Functional requirements
# ////////////////////////////////////////////////////////////////////////////////////////////////


friends_list = []

Members = []
New_Memers = []

Conference_Name = []
Conference_friends_list = []

Conference_detailes = None
is_in_Conference = 0

def Convert_to_pickle(data):
    return pickle.dumps(data)


def Extract_from_Pickle(data):
    return pickle.loads(data)


def Create_and_add_messages_for_client_file(sender_name, data, receiver_name=''):
    if data == 'create file':
        File = open(f"{sender_name}.txt", 'a')
        File.write(
            f"New Client with this User Name ({sender_name}) connected to server \n")
        File.close()
    else:
        File = open(f"{sender_name}.txt", 'a')
        File.write(
            f"{sender_name} send this message ({data}) to {receiver_name} \n")
        File.close()


def Create_Client_frainds_file(client, friend):
    File = open(f"{client}'s friends.txt", 'a')
    File.write(f"New friend :{friend}\n")
    File.close()



SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5545  

s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")



while True:
    name = input("Enter your name: ")
    if name != '':
        s.send(Convert_to_pickle([name, 'new client']))
        break
    os.system('cls')




def Conferences():
    os.system('cls')
    if len(friends_list) < 2:
        input("You must have two or more friends in your friends list to create a conference. \nAdd another ...\n\n Press enter to continue ... ")
    else:
        conference_name = input("Please specify the name of the conference : ")
        os.system('cls')
        s.send(Convert_to_pickle(
            ['Conference', name, friends_list, conference_name]))
        print(
            f"Conference created by {name} with the name {conference_name} \n\nfor leave the conference type left\n")
        print('--------------------------------\n')
        while True:
            Your_message = input('>>')
            if Your_message == 'left':
                input('You left conference')
                s.send(Convert_to_pickle(['left',name]))
                break
            else:       
                Encrypt_message_to_send = encrypt(
                                Your_message).decode() 
                hmac_message_to_send = check_integrity(
                                Your_message)               
                s.send(Convert_to_pickle(['Conference message',name,Encrypt_message_to_send,hmac_message_to_send]))


def listen_for_messages():
    while True:
        try:
            message = Extract_from_Pickle(s.recv(4096))

            if message == 'UserName added before':
                os.system('cls')
                print(
                    "Someone Joined to Server Before with this UserName!! \nTray Again with Unique UserName...")
                os.system('cls')
                s.close()
                break

            elif message == 'new client added':
                Create_and_add_messages_for_client_file(
                    sender_name=name, data='create file')

            elif message[0] == 'members':
                Members.clear()
                New_Memers.clear()
                for member in message[1]:
                    if member != name:
                        Members.append(member)
                        New_Memers.append(member)

            elif message[0] == 'New message received':
                decrypt_received_message = decrypt(message[1].encode())
                if check_integrity(decrypt_received_message) == message[3]:
                    print("\n------------------------------\n")
                    print(
                        f'You have new message from {message[2]} :\n\n {decrypt_received_message}')
                    print("\n------------------------------\n")
                else:
                    print("\n------------------------------\n")
                    print(message[3], '\n')
                    print(
                        f'Received message from {message[2]} is not integrity !!')
                    print("\n------------------------------\n")

            elif message[0] == 'Conference':
                global Conference_detailes
                Conference_detailes = message
                print("\n------------------------------\n")
                print(f'You have new request from {message[1]} \nFor join to this conference type yes')
                print("\n------------------------------\n")

            elif message[0] == 'Conference message':
                decrypt_received_message = decrypt(message[2].encode())
                if check_integrity(decrypt_received_message) == message[3]:
                    print(f'{message[1]} : {decrypt_received_message}')
                else:
                    print("\n------------------------------\n")
                    print(message[3], '\n')
                    print(
                        f'Received message from {message[2]} is not integrity !!')
                    print("\n------------------------------\n")
        
            elif message[0] == 'Left conference':
                print(message[1])

            else:
                print("\n------------------------------\n")
                print(message)
                print("\n------------------------------\n")

        except ConnectionError as er:
            print(er)
            s.close()
            break



c_thread = Thread(target=listen_for_messages)
c_thread.daemon = True
c_thread.start()

while True:
    try:
        os.system('cls')
        print(
            f'\nClient:                {name}         \n------------------------------------------\n')
        print("Select one option :\n1.friend's list\n2.Add friend\n3.Send message to a friend\n4.Conferencee\n5.Exit")
        to_send = input()
        os.system('cls')

        if to_send == '1':
            if len(friends_list) == 0:
                os.system('cls')
                input("Your Friend's List is Empty !!\n\nPress Enter to Continue ...")
                os.system('cls')
            else:
                i = 1
                os.system('cls')
                print("Your Friend's List are : \n-----------------------")
                for friend in friends_list:
                    print(f'{i}.{friend}\n')
                    i += 1
                input('-----------------------\n\nPress Enter to Continue ...')
                os.system('cls')

        elif to_send == '2':
            # print(Members)
            # print(New_Memers)
            if len(New_Memers) > 0:
                if len(Members) == 0:
                    print(
                        'No one has connected to the server yet !!\n\n Press Enter to Continue ..."')
                    input()
                    os.system('cls')
                else:

                    for me in New_Memers:
                        for fr in friends_list:
                            if me == fr:
                                New_Memers.remove(me)
                                break

                    i = 1
                    print('People thet connected to the server :\n')
                    for member in New_Memers:
                        if member != name:
                            print(f'{i}.{member}\n')
                            i += 1
                    friend_name = input(
                        '\n\nTo add a friend, type his/her name :')
                    while True:
                        flag1 = 0
                        for member in New_Memers:
                            if friend_name == member:
                                flag1 = 1
                                friends_list.append(friend_name)
                                Create_Client_frainds_file(name, friend_name)
                                New_Memers.remove(friend_name)
                                input(
                                    f"{friend_name} added into list of your friends \n\n press enter to continue ...")
                                os.system('cls')
                                break
                        if flag1 == 1:
                            break
                        else:
                            friend_name = input(
                                'This person is not among the people connected to the server\n\nEnter new one :')

            else:
                input('no body to add\n\n press enter to continue ...')

                os.system('cls')

        elif to_send == '3':
            os.system('cls')
            if len(friends_list) == 0:
                os.system('cls')
                input("Your Friend's List is Empty !!\n\nPress Enter to Continue ...")
                os.system('cls')

            else:
                os.system('cls')
                flag = 1
                message_to_send = input('Enter your message :')
                while True:
                    person = input("Enter your friend's name :")
                    for friend in friends_list:
                        if person == friend:
                            Encrypt_message_to_send = encrypt(
                                message_to_send).decode()
                            hmac_message_to_send = check_integrity(
                                message_to_send)
                            s.send(Convert_to_pickle(
                                ['new message', Encrypt_message_to_send, person, name, hmac_message_to_send]))
                            Create_and_add_messages_for_client_file(
                                name, message_to_send, person)
                            flag = 0
                            break
                    if flag == 0:
                        input(
                            f"your message send to {person}\n\n press enter to continue ...")
                        break
                    else:
                        input("This person is not your friend !!")


        elif to_send == '4':
            Conferences()


        elif to_send == '5':
            os.system('cls')
            print('connection lost')
            break

        elif to_send == 'yes':
            s.send(Convert_to_pickle(['yes',name]))
            os.system('cls')
            print(
                f'You added this conference by {Conference_detailes[1]}\n\nfor leave the conference type left\n')
            print('--------------------------------\n')               
            while True:
                Your_messages = input(">>")
                if Your_messages == 'left':
                    input('You left conference')
                    s.send(Convert_to_pickle(['left',name]))
                    break
                else:
                    Encrypt_message_to_send = encrypt(
                                Your_messages).decode()
                    hmac_message_to_send = check_integrity(
                                Your_messages)
                    s.send(Convert_to_pickle(['Conference message',name,Encrypt_message_to_send,hmac_message_to_send]))
                    

        else:
            s.send(Convert_to_pickle(['Not data',to_send]))
    except Exception as er:
        os.system('cls')
        print(er)
        break

s.close()
