''' HAPTCHA V2: Free for all group chat without account system. '''
''' SERVER '''

''' Importing required modules '''
import socket as sckt
import time
try:
    import thread as thrd
except:
    import _thread as thrd

''' Defining required constants '''
BYTE_LIMIT = 2048
SERVER_PORT = 12024
READY_COMMAND = '$READY$'
LEAVE_COMMAND = '$LEAVE$'

''' Global variables '''
num_connected_clients = 0
client_sockets_list = []
client_names_list = []

''' Defining required functions '''
# Handles a client. Call in multiple threads for multiple clients
def process_client(client_socket, client_addr):
    # This function modifies global variables, thus:
    global num_connected_clients, client_sockets_list, client_names_list
    
    # Wait for user to send name
    server_print('Waiting for name from IP ' + client_addr[0])
    client_name = client_socket.recv(BYTE_LIMIT).decode()
    server_print('Name ' + client_name + ' received for IP ' + client_addr[0])

    # Update the lists with the client socket and name
    server_print('Adding client ' + client_name + ' to broadcast list')
    client_sockets_list.append(client_socket)
    client_names_list.append(client_name)
    num_connected_clients += 1
    server_print('Added client ' + client_name + ' to broadcast list')
    server_print('Number of active clients is ' +  str(num_connected_clients))

    # Wait for user to send READY_COMMAND
    server_print('Waiting for READY_COMMAND from  ' + client_name)
    while(client_socket.recv(BYTE_LIMIT).decode() != READY_COMMAND):
        pass
    server_print(client_name + ' is ready')
    
    # Informing user and broadcasting to the rest about arrival of new user
    server_print('Informing ' + client_name + ' of successful inclusion')
    client_socket.send('You have succesfully joined the chat room'.encode())
    server_print('Broadcasting successful inclusion of ' + client_name)
    send_message(client_socket, 'HAPTCHA Server', client_name + ' has joined the chat')
    
    # Initiate message recieving loop that only terminates when user types LEAVE_COMMAND
    while True:
        client_message = client_socket.recv(BYTE_LIMIT).decode()
        
        # Break out of the loop if LEAVE_COMMAND received
        if client_message == LEAVE_COMMAND:
            break

        # Else broadcast the message
        server_print(client_name + ' says \"' + client_message + '\"')
        send_message(client_socket, client_name, client_message)
        continue

    # When client leaves, broadcast leaving message
    server_print(client_name + ' requested to leave')
    server_print('Broadcasting successful exclusion of ' + client_name)
    send_message(client_socket, 'HAPTCHA Server', client_name + ' has left the chat')

    # Remove the client socket and name from the list
    server_print('Removing client ' + client_name + ' from broadcast list')
    client_sockets_list.remove(client_socket)
    client_names_list.remove(client_name)
    num_connected_clients -= 1
    server_print('Removed client ' + client_name + ' from broadcast list')
    server_print('Number of active clients is ' +  str(num_connected_clients))

    # Close the connection
    client_socket.close()
    return

# Broadcasts a message to all clients except the sender
def send_message(sending_client_sock, sending_client_name, message):
    
    full_message = sending_client_name + ':> ' + message
    
    for i in range(num_connected_clients):
        # Do not send to the sender of message
        if (client_sockets_list[i] == sending_client_sock):
            continue

        # Send to the rest
        client_sockets_list[i].send(full_message.encode())       
        continue
    return

# This function prints the given message with current time on server console
def server_print(message):
    print(time.ctime() + ':> ' + message + '\n',end='')
    return


''' The main program '''
# Create a listening socket
listening_socket = sckt.socket(sckt.AF_INET,sckt.SOCK_STREAM)
listening_socket.bind(('',SERVER_PORT))
listening_socket.listen()   # MAX number of connections defaults to OS permitted

# Server is up
server_print('Server ready')

# Now the server shall remain up and running, accepting new connections and
# opening new threads for the newly connected clients
while True:
    # Wait for a new connection
    new_client_sock, new_client_addr = listening_socket.accept()
    server_print('New connection from IP ' + new_client_addr[0])

    # Start a new thread with the function process_client. Let the function handle the rest
    server_print('Starting thread for IP ' + new_client_addr[0])
    try:
        thrd.start_new_thread(process_client,(new_client_sock, new_client_addr))
        server_print('New thread started for IP ' + new_client_addr[0])
    except:
        server_print('Starting new thread FAILED for IP ' + new_client_addr[0])
    continue
