from skyfield.api import load, EarthSatellite
from tvtk.api import tvtk
from datetime import datetime
from tqdm import tqdm
import numpy as np


class Plotter:
    def draw_sphere(self, image_file):
        # load and map the texture
        img = tvtk.JPEGReader() # setup jpeg reader
        img.file_name = image_file  # read image
        texture = tvtk.Texture(input_connection=img.output_port, interpolate=1) # create an image based texture
        # (interpolate for a better appearance when zoomed in)

        r = 6371    # radius of the earth
        ang_res = 180   # default angular resolution

        # TexturedSphereSource allows you to add a texture to the sphere
        # create the sphere source with a given radius and angular resolution
        sphere = tvtk.TexturedSphereSource(radius=r, theta_resolution=ang_res, phi_resolution=ang_res)

        # assemble rest of the pipeline, assign texture
        # create a mapper in order to map the texture onto the sphere
        sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port)
        # create the actor and map the texture onto it
        sphere_actor = tvtk.Actor(mapper=sphere_mapper, texture=texture)
        self.scene.add_actor(sphere_actor)   # add the actor to the scene (adding the sphere onto the scene)

    def get_info(self, satellite_name, server, port):
        from tle_getter import get
        name_list = []
        lineonelist = []
        linetwolist = []

        # satellite_name would be the user's selection(s) from the on-screen list of satellites
        # get TLEs from database which would consist of these satellites https://celestrak.com/NORAD/elements/active.txt
        result = get(satellite_name, server, port).requestTLE()
        if result is None:  # If an error occurs in data transmission then return to main
            return

        # loop through the 'result' array
        for tle in result:
            # split up each tle in the result into name, line 1 and line 2
            line = tle.split("\r")
            # print(line)
            # put each item into corresponding list
            name_list.append(line[0])
            lineonelist.append(line[1])
            linetwolist.append(line[2])

        print(len(lineonelist), "tle(s)")   # no. of TLEs
        return name_list, lineonelist, linetwolist

    def plot_point(self):
        x, y, z = self.pos
        # plot each point as a small sphere
        self.scene.mlab.points3d(x, y, z, mode="sphere", color=(0,1,1), line_width=50, scale_factor=125)

    def plot_orbit(self):
        x, y, z = self.points
        # plot all the time-based points and connect them
        self.scene.mlab.plot3d(x, y, z, color=(1,0,1), tube_radius='5',)

    def create_plot(self, l1, l2):
        ts = load.timescale()   # load timescale object

        sat = EarthSatellite(l1, l2, ts=ts)
        # split line 2 so we can get a single data point in the TLE
        L2split = l2.split()
        # getting the mean motion from line 2 of the TLE
        mm = float(L2split[7])
        # print(mm)
        # get current datetime
        now = datetime.now()
        # get date
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))
        day = int(now.strftime("%d"))
        # print("date:", year, month, day)
        # get time
        hour = int(now.strftime("%H"))
        minute = int(now.strftime("%M"))
        second = int(now.strftime("%S"))
        # turn the time into a factor of hours. e.g. 19:43:20 => 19.72222222 (19 + (43/60) + ((20/60)/60)
        fhour = hour + (minute/60) + ((second/60)/60)
        # calculate the period from the mean motion
        period = ((1/mm) * 24) + 0.01 # a constant needs to be added in order for the orbit to look complete
        # the mean motion is not given in high enough accuracy so there will be a gap between the start and end of the orbit
        # if you look closely you can see it
        hours = np.arange(fhour, fhour+period, 0.01)  # list of times in the next period to plot
        # this is done because the orbit moves slightly - this can be demonstrated by replacing
        # 'fhour+period' to something like 'fhour+50'
        times = ts.utc(year, month, day, hours)  # getting times to plot the orbit with
        # extra info on time using skyfield api can be found here: https://rhodesmill.org/skyfield/time.html
        current_time = ts.now()
        # print("Current time is:", current_time.utc)

        self.points = sat.at(times).position.km  # finding the said points
        self.pos = sat.at(current_time).position.km  # getting current position of satellite
        Plotter.plot_point(self)
        Plotter.plot_orbit(self)

    # deprecated -- removed in later versions
    # function below is pointless unless running the file standalone !!!
    def __init__(self):
        image_filename = 'blue_earth_spherical_december.jpg'
        # image from NASA's 'blue marble' collection.
        # "It uses a geographic (Plate Carr´ee) projection, which is based on an equal latitude-longitude
        # grid spacing (not an equal area projection!)."
        # taken from: https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73909/readme.pdf
        # Basically, pixels along the x axis correspond to longitude and pixels along the y axis correspond to latitude.

        """
        draw_sphere(image_filename) # plot the sphere this would be the menu window where the user selects a sat
        mlab.show()     # show earth in GUI before giving the option to pick a satellite
        """
        # plot by name, could also plot by international designator
        name = input("Please enter the name of a satellite or constellation to plot: ")
        # get tle(s) for the requested satellite(s) split into name, line1, line2
        # connecting to localhost port 8080
        names, line1list, line2list = Plotter.get_info(self, name, server="127.0.0.1", port=8080)

        print(line1list, "\n", line2list)

        Plotter.draw_sphere(self, image_filename)  # plot the sphere

        # loop through and plot each tle
        for i in tqdm(range(len(line1list))):       # use module 'tqdm' to show a progress bar
            line1 = line1list[i]
            line2 = line2list[i]            # length of both lists should always be equal
            Plotter.create_plot(self, line1, line2)

    # OLD NOTES
    # Creates a GUI and start interacting with the figure
    # view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene), height=250, width=300, show_label=False),
    #            resizable=True)
    # or
    # mlab.show()
