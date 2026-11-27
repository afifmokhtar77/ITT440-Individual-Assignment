# ITT440-Individual-Assignment

# FTP Client and Server

I created this project for my ITT440 Network Programming assignment. It is a simple FTP client and server written in Python. You can log in, view the files on the server, upload a file and download a file.

You need Python 3 to run it. There are no extra packages to install.

## How it works

The client sends commands to the server on TCP port `2121`. File contents and file listings use a separate connection on TCP port `50000`.

This project uses passive mode. Enter `PASV` before each listing, upload, or download to prepare a new data connection.

## Getting started

Save the programs as `server.py` and `client.py`. Keep them in separate folders so you can easily tell the server's files apart from the client's files.

The code uses `127.0.0.1`. For a simple local setup, run both programs in the same environment, such as two Ubuntu WSL2 terminals or two Windows terminals.

### Start the server

In the folder containing `server.py`, create a folder named `shared_files`. Put a sample file called `server_note.txt` inside it.

Open a terminal in the server folder and run:

```bash
python3 server.py
```

On Windows, use `python server.py` instead. Leave this terminal open when you see `Server waiting for connection`.

### Start the client

Put a file called `upload_note.txt` in the folder containing `client.py`. Open another terminal in that folder and run:

```bash
python3 client.py
```

On Windows, use `python client.py` instead. The client should display the server greeting and the `FTP>` prompt.

### Log in

Enter these commands one at a time:

```text
USER student
PASS itt440
```

The server replies with `230 Login successful`.

## Using the client

To see the files on the server:

```text
PASV
LIST
```

To download the sample file:

```text
PASV
RETR server_note.txt
```

The file is saved in the folder where you started the client. It replaces any local file with the same name.

To upload your local file:

```text
PASV
STOR upload_note.txt
```

The file is saved in the server's `shared_files` folder. The upload is rejected if that filename already exists there.

Use plain filenames without paths or quotation marks. Wait for each command to finish before entering the next one.

## Available commands

| Command | What it does |
| --- | --- |
| `USER student` | Enters the username. |
| `PASS itt440` | Enters the password. |
| `PASV` | Prepares a data connection. |
| `LIST` | Shows the files on the server. |
| `RETR filename` | Downloads a file. |
| `STOR filename` | Uploads a file. |
| `NOOP` | Checks that the server responds. |
| `QUIT` | Ends the session. |

## A few things to know

The server handles one client session and then stops. Start it again before reconnecting.

If a transfer fails, check the filename and the `shared_files` folder. Enter `PASV` again before retrying. An interrupted transfer may leave an incomplete file.

This is a basic assignment project. It supports passive mode only, and it does not encrypt passwords or files.

## References

- [FTP specification - RFC 959](https://www.rfc-editor.org/rfc/rfc959)
- [Python socket documentation](https://docs.python.org/3/library/socket.html)
- [Python os documentation](https://docs.python.org/3/library/os.html)
