import socket
import pickle
import random
import time
import os

# Stop and wait program on the SENDER side

# ------------------------------------------ STEP 0: DECLARATIONS (depends on the protocol that we design) ------------------------------------------
# get user input for simulated packet loss
seed = input("Enter a number between 0-99. Note: This number is the approximate percentage of packets that will be lost during transmission")
# cast it to an int, otherwise python thinks it's a string for some reason
seed = int(seed)

# addresses
# both are this local machine for now
# using different ports for send and receive, can't be listening on same port
# receiver_ip = "192.168.1.201"
receiver_ip = socket.gethostbyname(socket.gethostname())
receiver_port = 5051
receiver_addr = (receiver_ip, receiver_port)

sender_port = 15200
sender_ip = socket.gethostbyname(socket.gethostname())
sender_addr = (sender_ip, sender_port)

# socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# need to bind so we can receive ACK
sock.bind(sender_addr)
sock.settimeout(5)

# protocols
buff_size = 1300
# this is minimum payload_size. The number of bytes from the file that we want to send at one time. Note: 1 byte = 1 char.
# setting this as 8 for now
payload_size = 8

# data - gonna put all of the packets we want to send into a list so that we
# can just iterate through the list to send everything in order
#
# header changes with each packet so we can just do something like header = SEQ = index of data in list % 2
# (will be either 0 or 1)
packets = []
# name of the file to be sent, should be located within the project directory so we don't have to navigate to it.
filename = "COSC635_P2_DataSent.txt"

# Statistic data
# total frames sent
frames_sent = 0
# total frames lost
frames_lost = 0
# size of file in bytes
file_size = os.path.getsize(filename)

# ------------------------------------------ STEP 1: DEALING WITH THE FILE ------------------------------------------
# this step deals with: Open the file, read the file, add encoded (utf-8) bytes into the packets list


# tell the user that the file is being read
print("parsing the file...")

# open file, r is the mode to open the file in. All the resources I looked at used r.
file = open(filename, "r")

# iterate over file (character by character) and add the encoded strings to the packets list
# I think this should work as expected but not 100%. Not sure if it breaks out of while loop correctly.
while 1:
    payload = ""
    char = ''
    # read in a payloads worth of chars
    for i in range(payload_size):
        # read 1 character
        char = file.read(1)
        if not char:
            break
        # concatenate char to decoded payload
        payload += char
    # encodes in utf-8 by default
    # payload_encoded = payload_decoded.encode()
    packets.append(payload)
    # breaks while loop if no char stored from for loop
    if not char:
        break
file.close()

# last step for this part: add some "kill connection" message to the file data so the
# while loop on the sender side doesn't keep waiting for data
kill_conn_message = "FINISH"
packets.append(kill_conn_message)

print("parsing complete!")

# ------------------------------------------ STEP 2: SEND THE DATA ------------------------------------------

print("sending the data...")

# data_length is the total number of "frames" that are being sent, doesn't change throughout the loop, only declare once
data_length = len(packets)

start = time.perf_counter()
for i in range(len(packets)):
    # packet to be sent
    data = packets[i]

    # -------- Simulated packet loss --------
    random_number = random.randint(0, 99)
    if random_number < seed:
        frames_lost += 1
        continue

    # figure out what the SEQ should be (0 for even items, 1 for odd items)
    SEQ = i % 2
    expected_ACK = (SEQ + 1) % 2

    # udp_header = [source_port, destination_port, total_length] CAN'T USE STRUCTS WITH LISTS, need to just
    # put all the individual items into the struct

    # prepare the header and the packet to be sent.
    # sending a list containing the relevant information
    # can send it with udp thanks to a library called "pickle" pickle.dumps(list) turns a
    # list into a byte representation that can be sent using udp methods. MUCH easier than using structs as I did previously
    data_list = [data_length, data, SEQ]
    data_to_send = pickle.dumps(data_list)

    # put the communications into a try except block
    try:
        # send the data and add statistic data
        sock.sendto(data_to_send, receiver_addr)
        frames_sent += 1

        # *********** NOT SURE ABOUT THIS LINE: if this was the last message, don't wait for ack, just kill connection ***********
        if packets[i] == kill_conn_message:
            break

        # wait for ACK before proceeding, separate
        while True:
            data_received, addr_received = sock.recvfrom(buff_size)
            # load the list of data received
            data_rec_list = pickle.loads(data_received)
            data_rec_len = data_rec_list[0]
            ACK_received = data_rec_list[1]
            if ACK_received is expected_ACK:
                # print("going next")
                # send next packet
                break
            else:
                print("I've received an unexpected ACK... trying again")
                # not expected, try again
                i -= 1
            # no ACK, try iteration again
            # run this iteration of the loop again
    except socket.timeout:
        print("timeout error")
        i -= 1
stop = time.perf_counter()
print("data has been sent!")

# ------------------------------------------ STEP 3: DISPLAY STATISTICS ------------------------------------------
# transmission time
transmission_time = stop-start
# percentage of lost frames
if max_data > 0:
    loss_percent = (frames_lost/data_length)*100
else:
    loss_percent = 100

print("-------------------")
print("")
print("Transmission Statistics")
print("")
print("Transmission time: ", transmission_time, "seconds")
print("File Size:", file_size, "bytes")
print("Total frames in file:", data_length)
print("Total frames sent:", frames_sent)
print("Total frames 'lost' (simulated):", frames_lost)
print("Percentage of lost frames:", loss_percent, "%")
print("")
print("-------------------")
