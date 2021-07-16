import sys
import socket
import os
import os.path

# Delete file if exists
def delete_file(file):
    if os.path.exists(file):
        os.remove(file)

# Send file between client and server
def send_file(socket, filename):

    #Get filesize and initialise counter
    bytes_to_send = os.path.getsize(filename)
    bytes_sent = 0

    # Get status from server
    status = socket.recv(2048).decode()
    # Cancel if file already exists
    if status == "exists":
        print("File already existed (Failure)")
        return -1

    # Open file
    with open(filename, "rb") as f:
        # Initialise data
        data = bytearray(1)
        # Read until data is no longer sent
        while len(data) > 0:
            data = f.read(4096)
            socket.sendall(data)
            bytes_sent += len(data)

    # Get response from receiver
    response = socket.recv(2048).decode()
    # Parse response as int
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


# Receive file from socket
def recv_file(socket, name, size):
    #Initialise variables
    data = bytearray(1)
    bytes_read = 0

    # Send confirmation
    socket.sendall(str.encode("ready"))

    # Open file to write
    with open(name, "wb") as f:
        #Loop while we are receiving data and haven't received the whole file
        while len(data) > 0 and bytes_read < size:
            data = socket.recv(4096)
            #Parse filesize if this is the first loop
            f.write(data)
            bytes_read += len(data)

    #Send error if we missed bytes
    if bytes_read < size:
        print("Error: read " + str(bytes_read) + " of " + str(filesize) + " bytes (Failure)")
        return -1

    #Send bytes received to sender
    socket.sendall(str.encode(str(bytes_read)))
    return bytes_read

# Send directory listing
def send_listing(socket):
    #Split files by new line
    toSend = str.encode('\n'.join(os.listdir()) + "\n")
    #Get bite size and send
    bytes_sent = len(toSend)
    socket.sendall(toSend)

    return bytes_sent

# Receive directory listing
def recv_listing(socket):
    #Initialise variables
    data = bytearray(1)
    bytes_read = 0

    # Print header
    print("\nServer Directory:")

    # Receive and print directory data until completely sent
    while len(data) > 0:
        data = socket.recv(4096)
        print(data.decode())
        bytes_read += len(data)
    # Return number of bytes read
    return bytes_read
