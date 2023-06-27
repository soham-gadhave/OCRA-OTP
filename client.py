import json
import socket

def driver():
    while True:
        socket = connect()
        option = int(input("\nEnter an option\n1. Register\n2. Login\n3. Exit\n"))
        if option == 1:
            register(socket)
        elif option == 2:
            login(socket)
        else:
            exit(socket)
            break

def connect():
    soc = socket.socket()
    port = 12345
    soc.connect(('127.0.0.1', port))
    return soc

def sendToServer(data, socket):
    input = json.dumps(data)
    socket.send(input.encode()) 
    return socket

def recieveFromServer(socket):
    data = socket.recv(1024)
    data = json.loads(data.decode()) 
    return data

def register(socket):
    #Taking input
    email = input("\nEnter email address\n")
    password= input("Password: \n")
    confirmPassword = input ("Confirm Password: \n") 
    while password != confirmPassword:
        print("Passwords did not match")
        password= input("Password: \n")
        confirmPassword = input("Confirm Password: \n")

    #Sending Data to Server 
    sendToServer({"action": "register", "email": email, "password": password}, socket)
    auth = recieveFromServer(socket)

    if auth["status"]["code"] == 5:
        print("Registration Successful. Your Function is", auth["Function"])
    else:
        print('\n' + auth["status"]["message"])

def login(socket):
    email = input("\nEnter email address\n")
    password = input("Password\n")

    sendToServer({"action": "login", "email": email, "password": password}, socket)
    auth = recieveFromServer(socket)
    
    if auth["status"]["code"] == 1:
        print("\nYour OTP is", auth["OTP"])
        answer = input("\nEnter the verification code\n")
        sendToServer({"answer": answer}, socket)
        reply = recieveFromServer (socket)
        status = reply["status"]
        message = reply["message"]
        if status == 3:
            print(message) 
        else:
            print(message)
    else:
        print('\n' + auth["status"]["message"])

def exit(socket):
    sendToServer({"action": "exit"}, socket)
    socket.close()
driver()