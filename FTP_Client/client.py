import socket
import os

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(("127.0.0.1", 2121))

reader = client.makefile("rb")
data_socket = None

response = reader.readline()

print(response.decode().strip())

while True:
    command = input("FTP> ")

    if command.upper().startswith("STOR "):

        filename = command.split(" ", 1)[1]

        if not os.path.isfile(filename):
            print("Local file not found")
            continue

    client.sendall((command + "\r\n").encode())

    response = reader.readline()

    if not response:
        break

    print(response.decode().strip())

    if response.startswith(b"227"):

        message = response.decode()

        address = message.split("(")[1].split(")")[0]

        parts = address.split(",")

        data_ip = ".".join(parts[:4])

        data_port = int(parts[4]) * 256 + int(parts[5])

        if data_socket is not None:
            data_socket.close()

        data_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        data_socket.connect((data_ip, data_port))

        print("Data connection established")

    elif response.startswith(b"150"):

        if command.upper().startswith("RETR "):

            filename = os.path.basename(
                command.split(" ", 1)[1]
            )

            with open(filename, "wb") as file:

                while True:
                    data = data_socket.recv(1024)

                    if not data:
                        break

                    file.write(data)

        elif command.upper().startswith("STOR "):

            filename = command.split(" ", 1)[1]

            with open(filename, "rb") as file:

                while True:
                    data = file.read(1024)

                    if not data:
                        break

                    data_socket.sendall(data)

        else:
            listing = b""

            while True:
                data = data_socket.recv(1024)

                if not data:
                    break

                listing += data

            print(listing.decode())

        data_socket.close()
        data_socket = None

        response = reader.readline()
        print(response.decode().strip())

        if response.startswith(b"226"):

            if command.upper().startswith("RETR "):
                print("File downloaded successfully")

            elif command.upper().startswith("STOR "):
                print("File uploaded successfully")

    elif response.startswith((b"550", b"451")):

        if data_socket is not None:
            data_socket.close()
            data_socket = None

    if response.startswith(b"221"):
        break

if data_socket is not None:
    data_socket.close()

reader.close()
client.close()

#