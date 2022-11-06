import socket
import pickle

# Stop and wait program on the RECEIVER side

# ------------------------------------------ STEP 0: DECLARATIONS (depends on the protocol that we design) ------------------------------------------
# addresses
receiver_ip = socket.gethostbyname(socket.gethostname())
port = 5051
receiver_addr = (receiver_ip, port)

sender_port = 15200
sender_ip = socket.gethostbyname(socket.gethostname())
sender_addr = (sender_ip, sender_port)

# socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# need to bind so we can receive data
sock.bind(receiver_addr)
sock.settimeout(5)

# protocols
buff_size = 1300

# data stuff
# this is the message indicating to stop waiting for data.
kill_conn_message = "FINISH"
# this is where we'll put all the decoded data that we receive
file_data = []
filename = "../../socketsTest_NetworkAndData/COSC635_P2_DataReceived.txt"

print("Awaiting data on:", receiver_addr)

# ------------------------------------------ STEP 1: RECEIVING THE DATA ------------------------------------------
transmission_start = False

while True:
    # receive the data
    data, sender_addr = sock.recvfrom(buff_size)

    # lets user know that data is being received
    if transmission_start is False:
        print("Receiving data!")
        transmission_start = True

    # unpack the data
    data_received_list = pickle.loads(data)

    # length of data received
    data_received_len = data_received_list[0]

    # decode the packet and send to the list
    message = data_received_list[1]
    # print(message)

    # SEQ number
    SEQ = data_received_list[2]

    # if the message is the "kill connection" message then break the loop, we are done
    if message == kill_conn_message:
        break

    # otherwise, add the data to the list
    file_data.append(message)


    # prepare the ACK and send it
    ACK = (SEQ + 1) % 2

    ack_length = len(b'ACK')

    response_list = [ack_length, ACK]
    response = pickle.dumps(response_list)

    try:
        sock.sendto(response, sender_addr)
    except socket.timeout:
        print("Uh oh! Disconnected from the sender")

print("data has been received!")
# ------------------------------------------ STEP 1: RECEIVING THE DATA ------------------------------------------

print("writing the data to a file called", filename)

# creates the new file within the project directory if it doesn't already exist
# append the file by writing all the data received to it
file = open(filename, "a")
for data in file_data:
    file.write(data)
file.close()

print("file has been created and written to! Check your directory for", filename)
# maybe give the user an option to read the data? idk, we can just open the txt file from the directory after this.
