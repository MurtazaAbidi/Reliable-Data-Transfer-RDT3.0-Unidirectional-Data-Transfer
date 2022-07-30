
import sys
import os
import rdt3 as rdt


def main():
    MSG_LEN = rdt.PAYLOAD

    if len(sys.argv) != 4:
        print("Usage:  " + sys.argv[0] + "  <client IP>  <drop rate>  <error rate>")
        sys.exit(0)

    try:
        os.stat("./Store")
    except OSError as emsg:
        print("Directory './Store' does not exist!!")
        print("Please create the directory before starting up the server")
        sys.exit(0)

    rdt.rdt_network_init(sys.argv[2], sys.argv[3])

    sock = rdt.rdt_socket()
    if sock == None:
        sys.exit(0)

    if rdt.rdt_bind(sock, rdt.SPORT) == -1:
        sys.exit(0)

    if rdt.rdt_peer(sys.argv[1], rdt.CPORT) == -1:
        sys.exit(0)

    rmsg = rdt.rdt_recv(sock, MSG_LEN)
    if rmsg == b'':
        sys.exit(0)
    else:
        filelength = int(rmsg)
        print("Received client request: file size =", filelength)
    rmsg = rdt.rdt_recv(sock, MSG_LEN)
    if rmsg == b'':
        sys.exit(0)
    else:
        filename = "./Store/" + rmsg.decode("ascii")
        try:
            fobj = open(filename, 'wb')
        except OSError as emsg:
            print("Open file error: ", emsg)
        if fobj:
            print("Open file", filename, "for writing successfully")
            osize = rdt.rdt_send(sock, b'OKAY')
            if osize < 0:
                print("Cannot send response message")
                sys.exit(0)
        else:
            print("Cannot open the target file", filename, "for writing")
            osize = rdt.rdt_send(sock, b'ERROR')
            sys.exit(0)

    print("Start receiving the file . . .")
    received = 0
    while received < filelength:
        print("---- Server progress: %d / %d" % (received, filelength))
        rmsg = rdt.rdt_recv(sock, MSG_LEN)
        if rmsg == b'':
            print("Encountered receive error! Has received", received, "so far.")
            sys.exit(0)
        else:
            wsize = fobj.write(rmsg)
            received += wsize

    fobj.close()
    rdt.rdt_close(sock)
    print("Completed the file transfer.")
    print("Server program terminated")


if __name__ == "__main__":
    main()
