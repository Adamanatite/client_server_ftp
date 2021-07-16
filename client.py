import socket
import sys
import os
import os.path
import Server.netfunctions as netfunctions


def usage():
    """Prints the correct command line usage of this file"""
    print('Usage: python client.py <hostname> <portNumber> <command> (arguments)')


def check_args():
    """Validates the command line arguments given

    Returns:
    hostname: The host name chosen if valid, otherwise -1
    portnumber: The port number chosen if valid, otherwise -1
    cmd: The command chosen if valid, otherwise -1
    msg: The command arguments if valid, otherwise -1
    """
    # Check number of arguments
    if len(sys.argv) < 4:
        print('Wrong number of arguments')
        usage()
        return (-1, -1, -1, -1);

    hostname = sys.argv[1]
    cmd = sys.argv[3]
    # Get command arguments if they exist
    if len(sys.argv) == 3:
        msg = ""
    else:
        msg = " ".join(sys.argv[4:])

    # Validate port number
    try:
        portnumber = int(sys.argv[2])
    except ValueError:
        print('Please specify a valid port number')
        usage()
        return (-1,-1, -1, -1);
    else:
        return hostname, portnumber, cmd, msg


def isValidFilename(filename):
    """Validates the given filename

    Parameters:
    filename (String): The file name to validate

    Returns:
    True if filename is valid, False otherwise
    """
    if len(filename) == 0:
        print("Please include filename")
        return False
    special_chars = ['\\','/','<','>',':', '*', '?', '"', '|']
    for character in filename:
        if character in special_chars:
            print("Invalid character in filename: " + character + " (Failure)")
            return False
    return True

def sendRequest(cmd, msg=""):
    """Validates the given filename

    Parameters:
    cmd (String): The command to execute
    msg (String): The argument of the command (default "")

    Returns:
    cli_sock: The socket created to send the request
    """
    # Create TCP socket and connect to server
    cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Connecting...")
        cli_sock.connect((host, port))
    except Exception:
        print("Connection attempt to server failed (Failure)")
        exit(1)
    print('connected to ' + host + ":" + str(port))

    # Concatenate command and arguments
    if len(msg) != 0:
        cmd = cmd + " " + msg

    cli_sock.sendall(str.encode(cmd))

    # Return socket
    return cli_sock

# Parse arguments and validate
host, port, cmd, msg = check_args()
if host == -1:
    exit(1)
cmd = cmd.lower()

try:
    cli_sock = ""

    if cmd == "list":
        # Send request and await response
        cli_sock = sendRequest("list")
        bytes = netfunctions.recv_listing(cli_sock)
        # Print listing
        if bytes > 0:
            print("Received listing (" + str(bytes) + " bytes) from " + host + ":" + str(port) + " (Success)")
            exit(0)
        # Print error
        print("Listing not received, connection lost (Failure)")
        exit(1)

    if not isValidFilename(msg):
        exit(1)

    # Store if file exists
    fileExists = os.path.exists("./" + msg)

    if cmd == "put":
        if not fileExists:
            print("File " + msg + " does not exist (Failure)")
            exit(1)
        # Send file
        bytes_to_send = os.path.getsize(msg)
        cli_sock = sendRequest("put", msg + " " + str(bytes_to_send))
        bytes = netfunctions.send_file (cli_sock, msg)
        # Print confirmation
        if bytes > -1:
            print("Put file " + msg + " (" + str(bytes) + " bytes) in server " + host + ":" + str(port) + " (Success)")
            exit(0)
        # Exit with error
        exit(1)

    if cmd == "get":
        if fileExists:
            print("File " + msg + " already exists (Failure)")
            exit(1)
        # Get file size from server
        cli_sock = sendRequest("get", msg)
        filesize = int(cli_sock.recv(2048).decode())
        # Receive if file exists
        if filesize == -1:
            print("File does not exist in server (Failure)")
            exit(1)
        bytes = netfunctions.recv_file(cli_sock, msg, filesize)
        # Print confirmation
        if bytes > -1:
            print("Got file " + msg + " (" + str(bytes) + " bytes) from server " + host + ":" + str(port) + " (Success)")
            exit(0)
        else:
            # Delete file and exit with error
            netfunctions.delete_file(msg)
            exit(1)
            
    # Error for incorrect command
    print("Unrecognised command: " + cmd)
    exit(1)

except Exception:
    # Error for unhandled exception
    print("Disconnected from server (Failure)")
    exit(1)
finally:
    # Close/disconnect socket
    if cli_sock:
        cli_sock.close()
    exit(0)
