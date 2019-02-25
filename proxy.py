import os, sys, socket,_thread

BACKLOG = 50
DATA = 99999
port = 8080
host = ''

def main():

    try:
        print("localhost\nport:", port)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(BACKLOG)

    except socket.error as e:
        if s:
            s.close()
        print (e)
        sys.exit(1)

    while True:

        conn, address = s.accept()
        _thread.start_new_thread(proxy_function, (conn, address))

    s.close()

def proxy_function(conn, address):
    req = conn.recv(DATA)

    line = req.decode().split('\n')[0]

    url = line.split(' ')[1]
    #print(url)

    print("Request:\n", url)

    http_index = url.find("://")

    if ( http_index != -1):
        url = url[(http_index + 3):]

    port_index = url.find(":")
    webserver_index = url.find("/")
    if webserver_index == -1:
        webserver_index = len(url)

    if (port_index==-1 or webserver_index < port_index):
        port = 80
        webserver = url[:webserver_index]
    else:
        port = int((url[(port_index+1):])[:webserver_index-port_index-1])
        webserver = url[:port_index]

    print("Port: "port)
    print("Webserver: "webserver)
    f = open("blockedURLs.txt", "r")
    lines = f.readline()

    for i in lines:
        if webserver == i:
            print("That webserver was blocked.")
            conn.close()
            sys.exit()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((webserver, port))
    s.send(req)

    while 1:
        data = s.recv(DATA)

        if (len(data) > 0):
            conn.send(data)
        else:
            break

    s.close()
    conn.close()


if __name__ == '__main__':
    main()
