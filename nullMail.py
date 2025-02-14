"""
MTA Email Server Assignment
Date: 14 February 2025
Description: This Python script implements a simple MTA server using sockets and threads.
It validates email addresses, limits recipients to 5, checks for a subject line, and limits attachments to 5.
Tested with Thunderbird as an email client.
"""

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
import re

# Function to validate email addresses using regex
def validate_email(email):
    pattern = re.compile(r'^[^@]+@[a-zA-Z0-9]+\\.(com|org|net|edu|io|app)$')
    return pattern.match(email)

# Function to count the number of attachments in the email body
def count_attachments(message_body):
    return message_body.count("Content-Disposition: attachment")

# Handle each client connection in a separate thread
def handle_client(connectionSocket, addr):
    print(f"Accepted connection from {addr}")
    connectionSocket.sendall("220 nusa.foo.net\r\n".encode())

    recipients = []
    subject = None

    while True:
        data = connectionSocket.recv(1024).decode()
        if not data:
            break

        # Handle EHLO, HELO, MAIL, RCPT, DATA, and QUIT commands
        if data.startswith("EHLO"):
            connectionSocket.sendall("502 OK\r\n".encode())
        elif data.startswith("HELO"):
            connectionSocket.sendall("250 OK\r\n".encode())
        elif data.startswith("MAIL FROM:"):
            connectionSocket.sendall("250 OK\r\n".encode())
        elif data.startswith("RCPT TO:"):
            recipient = re.findall(r'<(.*?)>', data)
            if recipient and validate_email(recipient[0]):
                if len(recipients) < 5:
                    recipients.append(recipient[0])
                    connectionSocket.sendall("250 OK\r\n".encode())
                else:
                    connectionSocket.sendall("550 Too many recipients\r\n".encode())
            else:
                connectionSocket.sendall("550 Invalid recipient address\r\n".encode())
        elif data.startswith("DATA"):
            connectionSocket.sendall("354 OK\r\n".encode())
            message_body = ""
            while True:
                line = connectionSocket.recv(1024).decode()
                if line == ".\r\n":
                    break
                if line.lower().startswith("subject:"):
                    subject = line.split(":", 1)[1].strip()
                message_body += line
            attachment_count = count_attachments(message_body)
            if attachment_count > 5:
                connectionSocket.sendall("550 Too many attachments\r\n".encode())
            elif not subject:
                connectionSocket.sendall("451 Subject line missing\r\n".encode())
            else:
                print(message_body)
                print(f"Attachments found: {attachment_count}")
                connectionSocket.sendall("250 OK\r\n".encode())
        elif data.startswith("QUIT"):
            connectionSocket.sendall("221 OK\r\n".encode())
            break

    connectionSocket.close()

# Main server function to set up socket, bind, listen, and accept connections
def main():
    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    welcomeSocket.bind(("", 9000))
    welcomeSocket.listen(4)
    print("Server is listening on port 9000")

    while True:
        connectionSocket, addr = welcomeSocket.accept()
        client_thread = Thread(target=handle_client, args=(connectionSocket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
