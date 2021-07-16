import socket
import sys
import os
import os.path
import netfunctions


def usage():
    """Prints the correct command line usage of this file"""
    print('Usage: python server.py <portNumber>')


def check_args():
    """Validates the command line arguments given

    Returns:
    portnumber: The port number if valid, otherwise -1
    """
    # Check number of arguments
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        usage()
        return -1
    # Check port number is valid
    try:
        portnumber = int(sys.argv[1])
    except ValueError:
        print('Invalid port number')
        usage()
        return -1
    else:
        return portnumber


# Validate port
port = check_args()
if port < 0:
    exit(1)

# Create TCP socket
srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Register socket and create request queue
    srv_sock.bind(("", port))
    srv_sock.listen(5)
except Exception:
    # Error case
    print("Could not create socket (Failure)")
    exit(1)

print('Socket created and listening on port ' + str(port))
while True:
    try:
        print("Waiting for new client...")
        # Block until a new connection request arrives
        cli_sock, cli_addr = srv_sock.accept()
        print("Connected to " + str(cli_addr))

        # Receive request from client
        request = cli_sock.recv(4096).decode()
        if not request:
            print('Client lost connection (Failure)')
            continue

        # Parse request
        commands = request.split(" ")
        cmd = commands[0]

        if cmd == "list":
            # Attempt to send listing
            try:
                bytes = netfunctions.send_listing(cli_sock)
            except Exception:
                print("Connection lost to client when sending listing (Failure)")
                continue
            print("Sent listing (" + str(bytes) + " bytes) to " + str(cli_addr) + " (Success)")
            continue


        # Check file exists
        msg = commands[1]
        fileExists = os.path.exists("./" + msg)

        if cmd == "put":
            # Check file doesn't already exist in directory
            if fileExists:
                print("File " + msg + " already exists")
                cli_sock.sendall(str.encode("exists"))
                continue
            # Attempt to receive file
            try:
                filesize = int(commands[2])
                bytes = netfunctions.recv_file(cli_sock, msg, filesize)
                # Send confirmation if file was received
                if bytes > -1:
                    print("Received file " + msg + " (" + str(bytes) + " bytes) from " + str(cli_addr) + " (Success)")
                else:
                    # Delete file if not fully Received
                    netfunctions.delete_file(msg)
            except Exception:
                print("Connection lost to client when receiving file (Failure)")
                netfunctions.delete_file(msg)
            continue

        if cmd == "get":
            # Check file exists in directory
            if not fileExists:
                print("File " + msg + " does not exist (Failure)")
                cli_sock.sendall(str.encode(str(-1)))
                continue
            else:
                # Send file size
                cli_sock.sendall(str.encode(str(os.path.getsize(msg))))
            # Attempt to send file
            try:
                bytes = netfunctions.send_file(cli_sock, msg)
                # Send confirmation if file was sent
                if bytes > -1:
                    print("Sent file " + msg + " (" + str(bytes) + " bytes) to " + str(cli_addr) + " (Success)")
                continue
            except Exception:
                print("Connection lost to client when sending file (Failure)")
            continue

    finally:
        # Close connection when finished
        print("Closed connection to client\n")
        cli_sock.close()

# Close server socket
srv_sock.close()
exit(0)
