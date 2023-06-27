import json
import random
import socket
import sqlite3

Reverse = "Reverse of OTP"
SumOfDigits = "Sum of Digits in OTP"
PartialSumOfDigits = "Sum of Digits in 1st and 3rd Place from LHS"

reverse = lambda otp: int(str(otp)[::-1])
sumOfDigits = lambda otp: sum(map(int, list(str(otp))))
partialSumOfDigits = lambda otp: int(str(otp)[0]) + int(str(otp)[2]) 

OTPFunctions = {Reverse: reverse, SumOfDigits: sumOfDigits, PartialSumOfDigits: partialSumOfDigits} 

def startServer():
    soc= socket.socket()
    # print("Socket Created Successfully")
    port = 12345
    soc.bind(('', port))
    # print("Socket is binded to port number", port)
    soc.listen(5)
    print("server is listening")
    return soc

def connectDB():
    connection = sqlite3.connect("KJSCE.db")
    # connection.execute("DROP TABLE RECORDS")
    # print ("Database Created successfully")

    # connection.execute(''' CREATE TABLE RECORDS (
    #                        EMAIL VARCHAR(30) PRIMARY KEY,
    #                        PASSWORD VARCHAR(30) NOT NULL,
    #                        FUNCTION VARCHAR(50) NOT NULL 
    #                        );       
    #                 ''')

    cursor = connection.cursor()
    return cursor, connection

def add(record, cursor):
    code = 5
    message = "Registered successfully"
    try:
        cursor.execute("INSERT INTO RECORDS VALUES (?, ?, ?)", record)
    except:
        code = 0
        message = "Email already exists"
    status = {"code": code, "message": message}
    return status

def register(record, cursor, client):
    status = add(record, cursor)
    sendToClient({"status": status, "Function": record[2]}, client)

def login(record, cursor):
    result = cursor.execute("SELECT PASSWORD, FUNCTION FROM RECORDS WHERE EMAIL = ?", (record[0],)).fetchall()
    # print(len(result))
    function = None
    if len(result) == 0:
        code = - 1
        message = "Wrong Email"
        return {"code": code, "message": message}, function
    for line in result:
        password = line[0]
        function = line[1]
    if password == record[1]:
        code = 1
        message = "Successful Login"
    else:
        code = -2
        message = "Wrong Password"
    return {"code": code, "message": message}, function

def sendToClient(data, client):
    data = json.dumps(data)
    client.send(data.encode())

def recieve():
    socket = startServer()
    cursor, connection = connectDB()
    while True:
        client, ip = socket.accept()
        # print("socket receieved connection from", ip)
        input = client.recv(1024)
        input = json.loads(input.decode())
        email = input.get("email")
        password = input.get("password")
        if input.get("action") == "register":
            register((email, password, list(OTPFunctions.keys())[random.randint(0, 2)]), cursor, client)
        elif input.get ("action") == "login":
            status, function = login((email, password), cursor)
            if status["code"] == 1:
                OTP = random.randint(1000, 9999)
                auth = {"status": status, "OTP": OTP}
                sendToClient(auth, client)
                answer = int(json.loads(client.recv(1024).decode())["answer"])
                # print(answer)
                if int(answer) == OTPFunctions[function](OTP):
                    sendToClient({"status": 3, "message": "Authentication Successful"}, client)
                else:
                    sendToClient({"status": 4, "message": "Wrong Answer"}, client)
            else:
                sendToClient({"status": status, "OTP": None}, client)
        else:
            print("\n\nExited Successfully")
            socket.close()
            break
        # display(cursor)
        #lient.send(byten(str(random.randint(1000, 9999)).encode()))
    client.close()
    connection.commit()

recieve()