# The UI creation wouldn't be possible without the traitsui user guide:
# https://docs.enthought.com/traitsui/traitsui_user_manual/index.html
import os

os.environ['ETS_TOOLKIT'] = 'qt'
from traits.api import HasTraits, Instance, on_trait_change, Str, List, Button, Int
from traitsui.api import View, Item, VGroup, HGroup, ListStrEditor, Group, ProgressEditor, Heading, Label
from mayavi.core.ui.api import MlabSceneModel, SceneEditor
from tvtk.pyface.api import Scene
from pyface.image_resource import ImageResource
from PlotModule import Plotter
from tle_getter import get_names
from tqdm import tqdm

serverIP = "127.0.0.1"  # location of the server you wish to connect to
portNo = 8080


class Visualization(HasTraits):
    scene = Instance(MlabSceneModel, ())

    select_item = Str  # upon selection of satellite from one of the lists - the choice goes here

    a = Str(desc='Search for a satellite')
    b = List(Str, ["Starlink", "ISS (ZARYA)", "Iridium", "Earth Satellites", "Galileo", "Globalstar", "OneWeb"])
    # List of featured satellites and constellations
    c = List(Str, get_names.all(serverIP, portNo))  # uses all satellite names available

    search_btn = Button("Search Satellites")
    all_btn = Button("Plot all Satellites (May Take a While)")  # Initialising buttons
    clear_btn = Button("Clear Plot")

    progress = Int  # variable updated after each time a satellite is plotted - used in the progress bar

    @on_trait_change('scene.activated')  # run when application started
    def create_plot(self):
        # Plot to Show
        self.scene.scene_editor.background = (0, 0, 0)  # set black background
        self.scene.mlab.clf()
        image_filename = 'blue_earth_spherical_december.jpg'
        # image from NASA's 'blue marble' collection.
        # "It uses a geographic (Plate Carr´ee) projection, which is based on an equal latitude-longitude
        # grid spacing (not an equal area projection!)."
        # taken from: https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73909/readme.pdf
        # Basically, pixels along the x axis correspond to longitude and pixels along the y axis correspond to latitude.
        Plotter.draw_sphere(self, image_filename)  # Finally, plot the earth

    def update_plot(self, sat_name):
        # if all satellites are requested, hardware dependent, it may take up to an hour to compute and show the orbits
        # at ~1.5it/s it takes ~35 minutes
        self.scene.mlab.clf()  # clear current figure

        if sat_name is '':  # don't bother finding an orbit for an empty string
            return
        # get tle(s) for the requested satellite(s) split into name, line1, line2
        # connecting to localhost port 8080
        try:
            names, line1list, line2list = Plotter.get_info(self, sat_name, serverIP, portNo)
        except:
            return

        # loop through the list of TLEs and plot each tle
        for i in tqdm(range(len(line1list))):
            line1 = line1list[i]
            line2 = line2list[i]  # length of both lists should always be equal
            Plotter.create_plot(self, line1, line2)
            self.progress = int((i / len(line1list)) * 100)
        self.progress = 100  # as values are rounded down, once all plotting is down get progress to 100
        self.progress = 0  # Upon finishing plotting reset the progress bar

    # PROTECTED
    # Button Actions #
    def _search_btn_fired(self):  # on button click
        self.update_plot(self.a)

    def _clear_btn_fired(self):
        self.create_plot()

    def _all_btn_fired(self):
        self.update_plot(sat_name="all")

    def _select_item_changed(self):  # when a selection variable is changed take it and update the plot
        self.update_plot(self.select_item)

    # UI creation see: https://docs.enthought.com/traitsui/traitsui_user_manual/index.html
    traits_view = View(HGroup(VGroup(Heading("Plot any active satellite"),
                                     Label("When searching for specific satellites be aware there may be "
                                           "multiple satellites with the same name."),
                                     HGroup(Item("a", style="simple", show_label=False),
                                            Item('search_btn', style="simple", show_label=False)),
                                     # Searchbar and Search Button
                                     Heading("Select an Orbit to View"),
                                     Item("b", editor=ListStrEditor(selected="select_item",
                                                                    title="Featured Constellations and Satellites")
                                          , style="custom", springy=True, height=100, show_label=False),
                                     # Featured Satellites List
                                     Item("c", editor=ListStrEditor(selected="select_item",
                                                                    title="All Satellites (Latest Last)"),
                                          style="custom", springy=True, height=250, show_label=False),
                                     # All Satellite List
                                     HGroup(Item("clear_btn", style="simple", show_label=False),
                                            Item("all_btn", style="simple", show_label=False))),
                              # Clear Plot Button
                              Group(Item("scene", editor=SceneEditor(scene_class=Scene), height=250, width=600,
                                         show_label=False))),
                       # Mayavi Scene Embed
                       Item("progress", editor=ProgressEditor(min=0, max=100), padding=-10),
                       resizable=True, title="Orbit Viewer", icon=ImageResource("logo.png"), style="custom")
    # set whether the window can be resized, the title, and logo.
    # code to set the logo was inspired by stack overflow post:
    # https://stackoverflow.com/questions/45819873/how-to-set-a-custom-icon-in-a-traits-ui-window


if __name__ == "__main__":
    vis = Visualization()
    # Start the main event loop
    vis.configure_traits()
