import socket
import sys
import os
import os.path
import netfunctions

# Print usage string
def usage():
    print('Usage: python server.py <portNumber>')

# Validate command line arguments
def check_args():
    # Check arguments length
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        usage()
        return -1
    # Check port number is valid
    try:
        portNo = int(sys.argv[1])
    except ValueError:
        print('Invalid port number')
        usage()
        return -1
    else:
        return portNo

# Check arguments
portNo = check_args()
if portNo < 0:
    exit(1)

# Create socket
srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Register the socket with the OS
    srv_sock.bind(("", portNo))
    # Create a queue for incoming connection requests
    srv_sock.listen(5)
except Exception:
    # Print exception and return erro code
    print("Could not create socket (Failure)")
    exit(1)

# Print confirmation message
print('Socket created and listening on port ' + str(portNo))
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

        # Split request into command and arguments
        commands = request.split(" ")
        cmd = commands[0]

        # Check if command is list
        if cmd == "list":
            # Attempt to send listing
            try:
                bytes = netfunctions.send_listing(cli_sock)
            except Exception:
                print("Connection lost to client when sending listing (Failure)")
                continue
            # Print confirmation
            print("Sent listing (" + str(bytes) + " bytes) to " + str(cli_addr) + " (Success)")
            continue


        # Get file name
        msg = commands[1]
        # Store if file exists
        fileExists = os.path.exists("./" + msg)

        # Check if command is put
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
        # Check if command is get
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

#Close server socket to preserve resources
srv_sock.close()
#Exit with 0 code to show no error
exit(0)
