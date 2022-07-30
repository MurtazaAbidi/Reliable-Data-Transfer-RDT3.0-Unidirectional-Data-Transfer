
import sys
import os
import time
import rdt3 as rdt


def main():
    MSG_LEN = rdt.PAYLOAD  # get the system payload limit

    if len(sys.argv) != 5:
        print("Usage:  " + sys.argv[0] + "  <server IP>  <filename>  <drop rate>  <error rate>")
        sys.exit(0)

    filename = sys.argv[2] # second argument is file name 

    try:
        fobj = open(filename, 'rb')
    except OSError as emsg:
        print("Open file error: ", emsg)
        sys.exit(0)
    print("Open file successfully")

    filelength = os.path.getsize(filename)
    print("File bytes are ", filelength)

    rdt.rdt_network_init(sys.argv[3], sys.argv[4]) # intilizing drop rate and error rate

    sock = rdt.rdt_socket()
    if sock == None:
        sys.exit(0)

    if rdt.rdt_bind(sock, rdt.CPORT) == -1:
        sys.exit(0)

    if rdt.rdt_peer(sys.argv[1], rdt.SPORT) == -1:
        sys.exit(0) 

    osize = rdt.rdt_send(sock, str(filelength).encode("ascii"))
    if osize < 0:
        print("Cannot send message1")
        sys.exit(0)
    osize = rdt.rdt_send(sock, filename.encode("ascii"))
    if osize < 0:
        print("Cannot send message2")
        sys.exit(0)
    rmsg = rdt.rdt_recv(sock, MSG_LEN)
    if rmsg == b'':
        sys.exit(0)
    elif rmsg == b'ERROR':
        print("Server experienced file creation error.\nProgram terminated.")
        sys.exit(0)
    else:
        print("Received server positive response")

    print("Start the file transfer . . .")
    starttime = time.monotonic()  # record start time
    sent = 0
    while sent < filelength:
        print("---- Client progress: %d / %d" % (sent, filelength))
        smsg = fobj.read(MSG_LEN)
        if smsg == b'':
            print("EOF is reached!!")
            sys.exit(0)
        osize = rdt.rdt_send(sock, smsg)
        if osize > 0:
            sent += osize
        else:
            print("Experienced sending error! Has sent", sent, "bytes of message so far.")
            sys.exit(0)

    endtime = time.monotonic()  # record end time
    print("Completed the file transfer.")

    fobj.close()
    rdt.rdt_close(sock)
    print("Client program terminated")


if __name__ == "__main__":
    main()
