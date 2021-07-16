import socket
import sys
import os
import os.path
import Server.netfunctions as netfunctions

# Print usage string
def usage():
    print('Usage: python client.py <hostname> <portNumber> <command> (arguments)')

# Validate command line arguments
def check_args():
    # Check argument length
    if len(sys.argv) < 4:
        print('Wrong number of arguments')
        usage()
        return (-1, -1, -1, -1);

    # Get hostname and command issued
    hostname = sys.argv[1]
    cmd = sys.argv[3]

    # Get command arguments if they exist
    if len(sys.argv) == 3:
        msg = ""
    else:
        msg = " ".join(sys.argv[4:])

    # Check port number is valid
    try:
        portNo = int(sys.argv[2])
    except ValueError:
        print('Please specify a valid port number')
        usage()
        return (-1,-1, -1, -1);
    else:
        return hostname, portNo, cmd, msg


def isValidFilename(filename):
    if len(filename) == 0:
        print("Please include filename")
        return False
    specialChars = ['\\','/','<','>',':', '*', '?', '"', '|']
    for c in filename:
        if c in specialChars:
            print("Invalid character in filename: " + c + " (Failure)")
            return False
    return True

def sendRequest(cmd, msg=""):
    # Create socket
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect socket to server
    try:
        print("Connecting...")
        cli_sock.connect((host, port))
    except Exception:
        print("Connection attempt to server failed (Failure)")
        exit(1)

    # Confirm connection
    print('connected to ' + host + ":" + str(port))

    if len(msg) != 0:
        cmd = cmd + " " + msg
    cli_sock.sendall(str.encode(cmd))
    # Return socket
    return cli_sock

# Check args and get connection/command details
host, port, cmd, msg = check_args()
if host == -1:
    exit(1)

# Make command lower case
cmd = cmd.lower()

try:
    # Initialise socket
    cli_sock = ""
    # Check if command is list
    if cmd == "list":
        # Send list request to server
        cli_sock = sendRequest("list")
        # Prepare to receive listing
        bytes = netfunctions.recv_listing(cli_sock)
        # Print confirmation if list was received
        if bytes > 0:
            print("Received listing (" + str(bytes) + " bytes) from " + host + ":" + str(port) + " (Success)")
            exit(0)
        # Print error if no listing was received
        print("Listing not received, connection lost (Failure)")
        exit(1)

    # Check filename
    if not isValidFilename(msg):
        exit(1)

    # Store if file exists
    fileExists = os.path.exists("./" + msg)

    # Check if command is put
    if cmd == "put":
        #Check file exists
        if not fileExists:
            print("File " + msg + " does not exist (Failure)")
            exit(1)
        # Send put request with filesize
        bytes_to_send = os.path.getsize(msg)
        cli_sock = sendRequest("put", msg + " " + str(bytes_to_send))
        #Start sending file
        bytes = netfunctions.send_file (cli_sock, msg)
        # Print confirmation if file was properly sent
        if bytes > -1:
            print("Put file " + msg + " (" + str(bytes) +  " bytes) in server " + host + ":" + str(port) + " (Success)")
            exit(0)
        # Exit with error if an error occurred
        exit(1)

    # Check if command is get
    if cmd == "get":
        # Check file doesn't already exist
        if fileExists:
            print("File " + msg + " already exists (Failure)")
            exit(1)
        # Send get request
        cli_sock = sendRequest("get", msg)
        # Get filesize from server
        filesize = int(cli_sock.recv(2048).decode())
        # Exit if file doesn't exist
        if filesize == -1:
            print("File does not exist in server (Failure)")
            exit(1)
        # Prepare to receive file
        bytes = netfunctions.recv_file(cli_sock, msg, filesize)
        # Print confirmation if file was received
        if bytes > -1:
            print("Got file " + msg + " (" + str(bytes) + " bytes) from server " + host + ":" + str(port) + " (Success)")
            exit(0)
        else:
            # Delete file if not fully received
            netfunctions.delete_file(msg)
            exit(1)

    # Print error if command not recognised
    print("Unrecognised command: " + cmd)
    exit(1)
except Exception:
    #Print error for unhandled exception
    print("Disconnected from server (Failure)")
    exit(1)
finally:
    # Close/disconnect socket
    if cli_sock:
        cli_sock.close()
    exit(0)
