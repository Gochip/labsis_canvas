import sys
sys.path.append(".")
import gi.repository.Gtk as Gtk
import canvas as Canvas
import random

class VentanaPrincipal(Gtk.Window):

    def __init__(self):
        super(VentanaPrincipal, self).__init__()
        self.canvas = MyCanvas()
        self.create_objects(self.canvas)
        self.canvas.set_verbose(True)
        self.add(self.canvas)

    def create_objects(self, canvas):
        obj3 = MyRectangleCanvas()
        obj3.set_x(100)
        obj3.set_y(200)
        obj3.set_width(15)
        obj3.set_height(30)
        obj3.set_movable(False)
        canvas.add_last(obj3)


class MyRectangleCanvas(Canvas.RectangleCanvas):

    def __init__(self):
        super(MyRectangleCanvas, self).__init__()

    def ev_right_click(self, x, y):
        self.menu = Gtk.Menu()
        opcion_1 = Gtk.MenuItem("Opción 1")
        opcion_2 = Gtk.MenuItem("Opción 2")
        opcion_3 = Gtk.MenuItem("Opción 3")
        self.menu.append(opcion_1)
        self.menu.append(opcion_2)
        self.menu.append(opcion_3)

        submenu = Gtk.Menu()
        submenu.append(Gtk.MenuItem("A1"))
        submenu.append(Gtk.MenuItem("A2"))
        submenu.append(Gtk.MenuItem("A3"))
        opcion_3.set_submenu(submenu)

        self.menu.popup(None, None, None, None, 3, Gtk.get_current_event_time())
        self.menu.show_all()


class Linking(Canvas.ObjectCanvas):

    def __init__(self, xi, yi):
        super(Linking, self).__init__()
        self.xi = xi
        self.yi = yi
        self.xfant = None
        self.yfant = None
        self.xf = None
        self.yf = None
        self.finished = False

    def is_selectable(self):
        return False

    def repaint(self):
        if self.finished:
            return
        xmin = None
        xmax = None
        ymin = None
        ymax = None

        xf = self.get_x()
        yf = self.get_y()
        self.xf = xf
        self.yf = yf

        if self.xfant is not None:
            xmin = min(self.xi, xf, self.xfant)
            xmax = max(self.xi, xf, self.xfant)
        else:
            xmin = min(self.xi, xf)
            xmax = max(self.xi, xf)

        if self.yfant is not None:
            ymin = min(self.yi, yf, self.yfant)
            ymax = max(self.yi, yf, self.yfant)
        else:
            ymin = min(self.yi, yf)
            ymax = max(self.yi, yf)
        self.xfant = xf
        self.yfant = yf

        self.width = xmax - xmin
        self.height = ymax - ymin
        self.canvas.queue_draw_area(xmin - 2, ymin - 2, self.width + 4, self.height + 4)

    def draw(self, w, cr):
        cr.set_line_width(2)
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(self.xi, self.yi)
        cr.line_to(self.xf, self.yf)
        cr.stroke()

    def contains(self, x, y):
        return not self.finished

    def ev_left_click(self, x, y):
        self.finished = True


class MyCanvas(Canvas.Canvas):

    def __init__(self):
        super(MyCanvas, self).__init__()


if __name__ == "__main__":
    vp = VentanaPrincipal()
    vp.connect("delete-event", Gtk.main_quit)
    vp.set_default_size(800, 600)
    #vp.maximize()
    vp.show_all()
    Gtk.main()
