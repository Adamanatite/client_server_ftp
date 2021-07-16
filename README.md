# client_server_socket
Python code for a client to communicate with a server using sockets for file transfer and listing

<b>Usable client commands:</b>
  * <b>List</b>: Lists all of the files currently stored on the server
  * <b>Put</b>: Uploads a file from the client folder into the server folder
  * <b>Get</b>: Gets a file from the server folder and downloads it into the client folder

<b>Usage:</b><br />
Both the client and server modules (client.py and server.py) are run from the command prompt <br />
To run the server, use the command "python server.py <portNumber>" <br />
To run a client command, use the command "python client.py <hostName> <portNumber> <get/put/list> (filename)" (A filename is not required for the "list" command) 
