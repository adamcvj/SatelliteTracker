import mysql.connector
import asyncio
from datetime import datetime


def Constellations(name):
    # Assign actual names for popular aliases of constellations i.e. choice Galileo -> search term GSAT
    alias_dict = {}
    if name.lower == "galileo":
        return "GSAT"
    elif name.lower == "earth satellites":
        return "FLOCK"
    else:
        return name
    # etc... Could be done better using database tables


def updateDB():
    from server_download import Update
    enter = Update()
    deleted = enter.deleteAllRows()
    enter.get_list()
    print("Updated db at time:", datetime.now())


class SQLProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport      # client info
        print(self.transport, "has connected")

    def data_received(self, data):
        self.data = data    # the data received from the client
        print(self.data, "received.")
        self.send_response(self.data)   # send a response

    def send_response(self, event):
        # connect to the database
        db = mysql.connector.connect(
            host="localhost",
            user="serverscripts",
            passwd="PassEnv123",
            database="mydatabase"
        )
        mycursor = db.cursor()
        choice = self.data.decode()
        print(choice.lower())
        if choice.lower() == 'all':
            # this will take a very long time to compute on the user end as it is 3000 satellites to plot
            sql = "SELECT name,line1,line2 FROM tles LIMIT 3000"
            mycursor.execute(sql,)
        elif choice.lower() == 'allnames':
            # this is so the client can show all the names of satellites to the user
            sql = "SELECT name FROM tles LIMIT 5000"
            mycursor.execute(sql,)
        else:
            name = str(Constellations(choice))
            print(name)
            # sql query
            sql = "SELECT name,line1,line2 FROM tles WHERE name LIKE %s"
            # execute query
            mycursor.execute(sql, ("%" + name + "%",))
            # .execute requires a tuple and the % must be inserted around the value for the 'LIKE' comparison

        response = mycursor.fetchall()  # get a response from the database
        print(response)
        self.send(response) # send response to the user

    def send(self, event):
        print(len(event))
        self.transport.write(("%d\r\n" % len(event)).encode())  # first send the length of the response
        for tle in event:
            print(tle)
            for line in tle:
                self.transport.write(line.encode()) # send each line in each TLE
        self.transport.close()  # close the connection to the client


async def main(host, port):
    loop = asyncio.get_running_loop()   # create running loop
    # create server using the class 'SQLProtocol'
    server = await loop.create_server(SQLProtocol, host, port)
    print("Server created", host, port)
    # add timer that updates the database every *10* hours
    updateDB()
    await server.serve_forever()        # server stays up until put down

asyncio.run(main("127.0.0.1", 8080))
