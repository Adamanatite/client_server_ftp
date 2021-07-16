import sys
import socket
import os
import os.path


def delete_file(file):
    """Deletes a given file, if it exists

    Parameters:
    file (String): The filename of the file to be deleted
    """
    if os.path.exists(file):
        os.remove(file)


def send_file(socket, filename):
    """Sends a file between client and server

    Parameters:
    socket: The socket the file will be transferred over
    filename: The name of the file to send

    Returns:
    bytes_sent: The number of bytes sent
    """
    #Get filesize and initialise counter
    bytes_to_send = os.path.getsize(filename)
    bytes_sent = 0

    # Cancel if file exists
    status = socket.recv(2048).decode()
    if status == "exists":
        print("File already existed (Failure)")
        return -1

    with open(filename, "rb") as f:
        data = bytearray(1)
        # Read in and send all file data
        while len(data) > 0:
            data = f.read(4096)
            socket.sendall(data)
            bytes_sent += len(data)

    # Parse response
    response = socket.recv(2048).decode()
    try:
        response = int(response)
    except:
        print("Invalid response from server (Failure)")
        return -1
    # Send error if bytes were lost
    if not (response == bytes_sent):
        print("Could only send " + str(response) + " of " + str(bytes_sent) + " bytes (Failure)")
        return -1
    return bytes_sent



def recv_file(socket, name, size):
    """Receives a file from client or server

    Parameters:
    socket: The socket the file will be transferred over
    name: The name of the file to receive
    size: The size of the file to receive (in bytes)

    Returns:
    bytes_read: The number of bytes received
    """
    data = bytearray(1)
    bytes_read = 0
    # Prepare to receive
    socket.sendall(str.encode("ready"))

    # Open file to write
    with open(name, "wb") as f:
        # Receive all data
        while len(data) > 0 and bytes_read < size:
            data = socket.recv(4096)
            f.write(data)
            bytes_read += len(data)

    # Send error if we missed bytes
    if bytes_read < size:
        print("Error: read " + str(bytes_read) + " of " + str(filesize) + " bytes (Failure)")
        return -1

    # Send bytes received to sender
    socket.sendall(str.encode(str(bytes_read)))
    return bytes_read



def send_listing(socket):
    """Sends directory listing to client

    Parameters:
    socket: The socket the listing will be sent over

    Returns:
    bytes_sent: The number of bytes sent
    """
    #Split files by new line
    toSend = str.encode('\n'.join(os.listdir()) + "\n")
    #Get bite size and send
    bytes_sent = len(toSend)
    socket.sendall(toSend)

    return bytes_sent


def recv_listing(socket):
    """Receives directory listing from server

    Parameters:
    socket: The socket the listing will be received over

    Returns:
    bytes_read: The number of bytes received
    """
    data = bytearray(1)
    bytes_read = 0

    # Print header
    print("\nServer Directory:")

    # Receive and print directory data until completely sent
    while len(data) > 0:
        data = socket.recv(4096)
        print(data.decode())
        bytes_read += len(data)
    return bytes_read
