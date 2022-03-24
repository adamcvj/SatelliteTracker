# satellite-tracker
A Satellite Tracking Interface using python.  
This is an old project that is not maintained and is now archived.  
The project was written without knowledge of git and proper software conventions which may explain why it's so messy!  

### Project idea(s):
- Perhaps a batch file or executable which can setup the server first and then run the client. Could also be used to time an update of the database which is important as orbit data is not accurate if it goes out of date - see: [info on satellite data and tracking](#info-on-satellite-data-and-tracking).


# Server Setup
- Using mysql to create the table - copy this and create a database to store satellite information:
CREATE table mydatabase.tles (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), line1 VARCHAR(255), line2 VARCHAR(255));
  - where mydatabase is the database you have created
- These packages must be installed:
  - mysql.connector
  - requests
- In server_download.py change self.auth and self.key (lines 14 & 15) to your database credentials.
  - if you changed the name of your database from "mydatabase" then update the 'database' variable on line 23
- Run server_download.py
- Start the server by running ascioServer.py
- At the moment you will need to manually run server_download.py every 6 (or so) hours to keep the database updated - this increases the accuracy of satellite data.

# Client Setup
- Setting up an anaconda environment is **highly** recommended - these packages must be installed:
  - traits
  - traitsui
  - tvtk
  - mayavi
  - skyfield
  - pyface
  - ctypes
  - envisage
  - pyqt
- in main.py change serverIP and portNo variables (lines 15 & 16) to that of your server's.
- run main.py (and cross your fingers)

# Info on Satellite Data and tracking
- all data is taken from celestrak.com (more specifcally: https://celestrak.com/NORAD/elements/active.txt)

there is various documentation surrounding the skyfield package and how data points are generated:

here is an important excerpt from https://rhodesmill.org/skyfield/earth-satellites.html
1.	The accuracy of the satellite positions is not perfect. 
    To quote directly from Revisiting Spacetrack Report #3 Appendix B:
    “The maximum accuracy for a TLE is limited by the number of decimal places in each field. In general, TLE data is accurate to about a kilometre or so at epoch and it quickly      degrades.”
2.	Satellite elements go rapidly out of date. You will want to pay attention to the “epoch” — the date on which an element set is most accurate — of every TLE element set you       use. Elements are only useful for a week or two on either side of the epoch date, and for dates outside of that range you will want to download a fresh set of elements.
3.	Expect a satellite’s orbit to constantly change as the SGP4 propagation routine models' effects like atmospheric drag and the Moon’s gravity. In particular, the true anomaly     parameter can swing wildly for satellites with nearly circular orbits, because the reference point from which true anomaly is measured — the satellite’s perigee — can be         moved by even slight perturbations to the orbit.

# How satellite information is being stored:
Satellites are to be stored in the database using the Two-Line Element set (TLE).
### What is a TLE?
- This is a way of storing orbital data so that its orbital path can be predicted to some accuracy.
- Example:

> ISS (ZARYA)  
  1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927  
  2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537  

Data can be extracted by splitting each line into lists. 
