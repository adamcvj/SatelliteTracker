# Gets satellite TLEs from https://celestrak.com/NORAD/elements/active.txt formats to fit in database
# for TLEs to work with skyfield's format it must just be the two lines of information
import requests
import mysql.connector


class Update:
    # Checks if there are any new satellites - and adds them to the database
    # All Data will need to be updated frequently - every few hours - as TLEs go out of date quickly.
    # the table's sql is as follows:
    # CREATE table mydatabase.tles
    # (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), line1 VARCHAR(255), line2 VARCHAR(255));
    def __init__(self):
        self.auth = 'serverscripts'
        self.key = 'PassEnv123'
        self.dict = {}         # dictionary to add satellites to
        self.url = "https://celestrak.com/NORAD/elements/active.txt"  # list of all active satellites
        # connect to the database
        self.db = mysql.connector.connect(
            host="localhost",
            user=self.auth,
            passwd=self.key,
            database="mydatabase"
        )
        self.mycursor = self.db.cursor()

    # this function could be made to delete old TLEs instead, and could make this program constantly update the db.
    def deleteAllRows(self):
        # delete all rows from table 'tles'
        sql = "DELETE FROM tles"
        self.mycursor.execute(sql, )
        return True

    def add_record(self, satname, lineOne, lineTwo):
        # SQL for inserting TLEs into the database
        sql = "INSERT INTO tles (name, line1, line2) VALUES (%s, %s, %s)"
        # best practice for using SQL in python (prevents sql injection)
        val = satname, lineOne, lineTwo
        # execute the sql with the data inserted into the statement
        self.mycursor.execute(sql, val)

        self.db.commit()

        # print(val, "\nrecord inserted")

    def get_list(self):
        # print(self.db)
        tle_dictionary = self.dict
        # request all info from given url
        response = requests.get(self.url)
        # split the response into lines whenever there is a newline
        data = response.text.strip().split("\n")

        # loop through each line in the response
        for i in range(len(data)):
            line = data[i]
            # if the first character in the line equals one then we know where we are on the first line of the TLE
            # data for each satellite comes in three lines: Satellite Name and its TLE split into two lines.
            if line[0] == "1":  # if the line begins with a '1' assume it is line 1 of the TLE
                # add TLE to database
                sat_name = data[i - 1]
                lineOne = data[i]  # save lines of the tle
                lineTwo = data[i + 1]
                print("inserting", sat_name, lineOne, lineTwo)
                # add 1 record consisting of the tle and the sat's name
                self.add_record(sat_name, lineOne, lineTwo)
                # adding each tle to the tle dictionary
                tle_dictionary[sat_name] = lineOne + lineTwo
        # return the titles for the dictionary which are the names of the satellites, and the rest of the TLE
        # return tle_dictionary.keys(), tle_dictionary


if __name__ == '__main__':
    enter = Update()
    deleted = enter.deleteAllRows()
    enter.get_list()
