import sys
sys.path.append(".")
import gi.repository.Gtk as Gtk
import gi.repository.Gdk as Gdk
import canvas as Canvas
import random

class VentanaPrincipal(Gtk.Window):

    def __init__(self):
        super(VentanaPrincipal, self).__init__()
        self.canvas = Canvas.Canvas()
        self.canvas.modify_bg(Gtk.StateType.NORMAL, Gdk.Color.from_floats(0, 0, 0.2))
        self.canvas.set_verbose(True)
        self.add(self.canvas)


if __name__ == "__main__":
    vp = VentanaPrincipal()
    vp.connect("delete-event", Gtk.main_quit)
    vp.set_default_size(800, 600)
    #vp.maximize()
    vp.show_all()
    Gtk.main()
