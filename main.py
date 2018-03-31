__author__ = 'Parisi Germán'

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
        obj1 = Canvas.CircleCanvas(500, 500, 50)
        canvas.add_last(obj1)

        obj = Canvas.LineCanvas()
        obj.set_x(300)
        obj.set_y(10)
        obj.set_width(80)
        obj.set_height(90)
        canvas.add_ahead(obj)

        obj2 = Canvas.RectangleCanvas()
        obj2.set_x(150)
        obj2.set_y(150)
        obj2.set_width(30)
        obj2.set_height(30)
        canvas.add_ahead(obj2)

        obj3 = MyRectangleCanvas()
        obj3.set_x(100)
        obj3.set_y(200)
        obj3.set_width(15)
        obj3.set_height(30)
        obj3.set_movable(False)
        canvas.add_last(obj3)

        obj4 = MyRectangleCanvas()
        obj4.set_x(200)
        obj4.set_y(200)
        obj4.set_width(15)
        obj4.set_height(30)
        canvas.add_last(obj4)

        obj5 = Canvas.ImageCanvas("router.png")
        obj5.set_x(300)
        obj5.set_y(300)
        canvas.add_last(obj5)

        obj6 = Canvas.AnimationRectangleCanvas()
        obj6.set_x(50)
        obj6.set_y(50)
        obj6.set_width(50)
        obj6.set_height(50)
        canvas.add_last(obj6)
        obj6.start()


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


class MyCanvas(Canvas.Canvas):

    def __init__(self):
        super(MyCanvas, self).__init__()
        self.linkings = []

    def ev_left_click_in_empty_point(self, w, x, y):
        # pfx = random.uniform(0, 400)
        # pfy = random.uniform(0, 400)
        l = Canvas.Linking(x, y)
        l.set_x(x)
        l.set_y(y)
        l.set_follower(True)
        self.linkings.append(l)
        self.add_last(l)


if __name__ == "__main__":
    vp = VentanaPrincipal()
    vp.connect("delete-event", Gtk.main_quit)
    vp.set_default_size(800, 600)
    #vp.maximize()
    vp.show_all()
    Gtk.main()
