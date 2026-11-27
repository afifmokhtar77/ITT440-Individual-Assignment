import socket
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("0.0.0.0", 2121))

server.listen()

print("Server waiting for connection")

connection, address = server.accept()

print("Client connected:", address)

connection.sendall(b"220 FTP Service Ready\n")

username = ""
authenticated = False

data_server = None
shared_folder = "shared_files"

while True:
    data = connection.recv(1024)

    if not data:
        break

    message = data.decode().rstrip("\r\n")

    parts = message.split(" ", 1)

    command = parts[0].upper()

    argument = ""

    if len(parts) > 1:
        argument = parts[1]

    print(command)

    if command == "USER":
        username = argument
        authenticated = False

        connection.send(b"331 Password required\r\n")

    elif command == "PASS":
        authenticated = False

        if username == "":
            connection.send(b"503 Send USER first\r\n")

        elif username == "student" and argument == "itt440":
            authenticated = True

            connection.send(b"230 Login successful\r\n")

        else:
            connection.send(b"530 Login incorrect\r\n")
   
    elif command == "PASV":

        if not authenticated:
            connection.sendall(b"530 Not logged in\r\n")

        else:
            if data_server is not None:
                data_server.close()

            data_server = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            data_server.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            data_server.bind(("0.0.0.0", 50000))
            data_server.listen(1)
            data_server.settimeout(10)

            connection.sendall(
                b"227 Entering Passive Mode (127,0,0,1,195,80)\r\n"
            )

    elif command == "LIST":

        if not authenticated:
            connection.sendall(b"530 Not logged in\r\n")

        elif data_server is None:
            connection.sendall(b"425 Use PASV first\r\n")

        else:
            try:
                files = os.listdir(shared_folder)

                listing = "\r\n".join(files) + "\r\n"

                connection.sendall(
                    b"150 Opening data connection\r\n"
                )

                data_connection, data_address = data_server.accept()

                with data_connection:
                    data_connection.sendall(listing.encode())

                connection.sendall(
                    b"226 Transfer complete\r\n"
                )

            except OSError:
                connection.sendall(
                    b"451 Transfer failed\r\n"
                )

            finally:
                data_server.close()
                data_server = None

    elif command == "RETR":

        if not authenticated:
            connection.sendall(b"530 Not logged in\r\n")

        elif data_server is None:
            connection.sendall(b"425 Use PASV first\r\n")

        else:
            filename = os.path.join(shared_folder, argument)

            try:
                if (
                    not argument
                    or os.path.basename(argument) != argument
                    or os.path.islink(filename)
                    or not os.path.isfile(filename)
                ):
                    connection.sendall(b"550 File unavailable\r\n")

                else:
                    with open(filename, "rb") as file:

                        connection.sendall(
                            b"150 Opening data connection\r\n"
                        )

                        data_connection, data_address = data_server.accept()

                        with data_connection:
                            while True:
                                data = file.read(1024)

                                if not data:
                                    break

                                data_connection.sendall(data)

                    connection.sendall(
                        b"226 Transfer complete\r\n"
                    )

            except OSError:
                connection.sendall(b"451 Transfer failed\r\n")

            finally:
                data_server.close()
                data_server = None

    elif command == "STOR":

        if not authenticated:
            connection.sendall(b"530 Not logged in\r\n")

        elif data_server is None:
            connection.sendall(b"425 Use PASV first\r\n")

        else:
            filename = os.path.join(shared_folder, argument)

            try:
                if (
                    not argument
                    or argument in (".", "..")
                    or os.path.basename(argument) != argument
                    or os.path.islink(filename)
                    or os.path.exists(filename)
                ):
                    connection.sendall(b"550 File unavailable\r\n")

                else:
                    with open(filename, "xb") as file:

                        connection.sendall(
                            b"150 Opening data connection\r\n"
                        )

                        data_connection, data_address = data_server.accept()

                        with data_connection:
                            while True:
                                data = data_connection.recv(1024)

                                if not data:
                                    break

                                file.write(data)

                    connection.sendall(
                        b"226 Transfer complete\r\n"
                    )

            except OSError:
                connection.sendall(b"451 Transfer failed\r\n")

            finally:
                data_server.close()
                data_server = None

    elif command == "NOOP":
        connection.send(b"200 Command OK\r\n")

    elif command == "QUIT":
        connection.send(b"221 Goodbye\r\n")
        break

    else:
        connection.send(b"500 Unknown command\r\n")

if data_server is not None:
    data_server.close()

connection.close()
server.close()