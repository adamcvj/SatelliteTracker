# have 'first time setup' where the program gets a list of satellite names from the database
# would just be "SELECT names FROM tles" o.e.
# probably another python file
import socket
import time
import ctypes  # Used to show error box


class get_names:
    def all(addr, port):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create client object
            client.connect((addr, port))  # connect to server
            client.send("allnames".encode())  # send name of satellite(s) or constellation
            length = int(client.recv(4096).decode())  # get number of names back from server
        except:  # in case there is a server error
            ctypes.windll.user32.MessageBoxW(0,
                                             "A problem occurred when getting data from the server, please try again.",
                                             "Error", 0)
            exit()
            return None
        print(length)
        from_server = b''  # creating a bytes-type variable to add data to
        for i in range(length + 1):
            # get 'length' amounts of data from the server and add it to the variable 'from_server'
            from_server += client.recv(4096)
            # could add a time.sleep but the for loop should suffice
        print(from_server)
        line = from_server.decode()  # converting from bytes to string
        decoded = line.split('\r')
        return decoded


class get:
    def __init__(self, selection, server_addr, port):
        self.name = selection
        self.addr = server_addr
        self.port = port

    def requestTLE(self):
        # This step could be bypassed and the script could directly connect to the database,
        # however, this means that there is no way of managing concurrent connections.
        # Also means i can set up a proper client-server network.
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create client object
            client.connect((self.addr, self.port))  # connect to server
            client.send(self.name.encode())  # send name of satellite(s) or constellation
            length = int(client.recv(4096).decode()) # get length of TLE data back from server
        except:  # in case of a server error
            ctypes.windll.user32.MessageBoxW(0,
                                             "A problem occurred when getting data from the server, please try again.",
                                             "Error", 0)
            return None
        if length == 0:
            ctypes.windll.user32.MessageBoxW(0,
                                             "No Satellites found.",
                                             "Error", 0)
        from_server = b''   # creating a bytes-type variable to add data to
        # Wait for reasonable time for server to send data
        for i in range(2):
            time.sleep(1)
            # get data held in the receive queue (buffer can be shrunk, however a request for all satellites is large
            from_server += client.recv(2*524288)

        print(from_server)
        line = from_server.decode() # converting from bytes to string

        # splits the response every 165 characters which is the length of one TLE
        # hence splitting the response into separate TLEs
        n = 165
        decoded = [line[i:i + n] for i in range(0, len(line), n)]   # split every 165 characters in the line
        print("DECODED", decoded)
        return decoded  # return the response
