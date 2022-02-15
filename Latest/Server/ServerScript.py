# This is the server manager - this manages connections to the server, and therefore any requests to the database.
import socket
import mysql.connector


def retrieve(selection):
    db = mysql.connector.connect(
        host="localhost",
        user="scripts",
        passwd="PassEnv123",
        database="mydatabase"
    )
    mycursor = db.cursor()
    # sql query 
    sql = "SELECT line1,line2 FROM tles WHERE name LIKE %s"
    # execute query
    mycursor.execute(sql, ("%" + selection + "%",))
    # .execute requires a tuple and the % must be inserted around the value

    return mycursor.fetchall()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8080))
server.listen(5)

queue = []

while True:
    conn, addr = server.accept()    # accept connection from client
    from_client = ''
    while True:
        data = conn.recv(150)      # receive data (should be a small amount of text)
        if not data: break      # if there is no more data then exit loop
        from_client += data

    response = retrieve(from_client, addr)  # get data from database
    conn.send(response)     # send the response
    conn.close()    # close connection
    print('client disconnected')
# 

