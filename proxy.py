import os, sys, socket,_thread

BACKLOG = 50    # maximum number of pending connections
DATA = 99999    # maximum number of bytes that can be received
port = 8080     # the port number
host = ''       # we leave the host blank for localhost

def main():

    try:
        print("localhost\nport:", port)

        # we create a socket and and bind it with our host and property
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))

        # the function that listens to spot when the browser wants
        # to connect
        s.listen(BACKLOG)

    except socket.error as e:
        if s:
            s.close()
        print (e)
        sys.exit(1)

    while True:
        # when the browser connects we accept and we start a new proxy thread
        conn, address = s.accept()
        _thread.start_new_thread(proxy_function, (conn, address))

    s.close()


def proxy_function(conn, address):
    # the request we get from browser
    req = conn.recv(DATA)

    # we need to get the first line of the request to find
    # the url of the webserver
    line = req.decode().split('\n')[0]

    url = line.split(' ')[1]

    # we find the index of te port and the webserver
    http_index = url.find("://")

    if ( http_index != -1):
        url = url[(http_index + 3):]

    port_index = url.find(":")
    webserver_index = url.find("/")
    if webserver_index == -1:
        webserver_index = len(url)

    port = -1
    webserver = ""

    if (port_index==-1 or webserver_index < port_index):
        port = 80
        webserver = url[:webserver_index]
    else:
        port = int((url[(port_index+1):])[:webserver_index-port_index-1])
        webserver = url[:port_index]

    # we check whether the webserver is in the blocklist
    # if it is we don't send anything to the webserver
    f = open("blockedURLs.txt", "r")
    lines = f.readlines()

    for i in lines:
        print(i)
        print(webserver)
        if str(webserver) == str(i):
            print("That webserver was blocked.")
            conn.close()
            sys.exit(1)

    print("Request:\n", req)
    print("Port: ", port)
    print("Webserver: ", webserver)
    try:
        # we connect to the webserver and send the request
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(req)

        while True:
            # we receive data from the webserver and send it
            # to browser
            data = s.recv(DATA)
            
            if (len(data) > 0):
                conn.send(data)
                print("sent")
            else:
                break

        s.close()
        conn.close()
    except socket.error as e:
        if s:
            s.close()
        if conn:
            conn.close()
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
