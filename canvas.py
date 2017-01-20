# coding:utf-8
import gi.repository.Gtk as Gtk
import gi.repository.Gdk as Gdk
import gi.repository.GObject as GObject
import math
import time
import cairo


class Canvas(Gtk.DrawingArea):

    def __init__(self):
        super(Canvas, self).__init__()

        # Arrays
        self.objects = []
        self.selected_objects = []

        # Variables
        self.verbose = False
        self.allow_selection_area = True
        self.allow_multiple_selection = True
        self.scaling = False
        self.corner = -1
        self.mouse_movement = MouseMovement()
        self.mouse_movement_follower = MouseMovement()
        self.selection_area = None

        # Events
        self.add_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.connect("draw", self.ev_draw)
        self.connect("button-press-event", self.ev_click)
        self.connect("button-release-event", self.ev_release)
        self.connect("motion-notify-event", self.ev_move)
        self.connect("key-press-event", self.ev_key_pressed)

        # Others
        self.set_can_focus(True)
        self.HAND2 = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.ARROW = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.window_gdk = self.get_root_window()

    # Sets and gets
    def is_allow_selection_area(self):
        return self.allow_selection_area

    def is_allow_multiple_selection(self):
        return self.allow_multiple_selection

    def get_verbose(self):
        return self.verbose

    def set_allow_selection_area(self, s):
        self.allow_selection_area = s

    def set_allow_multiple_selection(self, s):
        self.allow_multiple_selection = s

    def set_verbose(self, v):
        self.verbose = v

    # Add
    def add_object(self, i, obj):
        self.objects.insert(i, obj)
        obj.set_canvas(self)
        obj.set_outline(Outline(obj))
        obj.ev_add(i)

    def add_last(self, obj):
        self.add_object(0, obj)

    def add_ahead(self, obj):
        self.add_object(len(self.objects), obj)

    def calculate_drawing(self, objects):
        xis = []
        yis = []
        xfs = []
        yfs = []
        for o in objects:
            xis.append(o.get_x())
            yis.append(o.get_y())
            xfs.append(o.get_x() + o.get_width())
            yfs.append(o.get_y() + o.get_height())
        xmin = min(xis)
        ymin = min(yis)
        xmax = max(xfs)
        ymax = max(yfs)
        return (xmin, ymin, xmax - xmin + 1, ymax - ymin + 1)

    def deselect(self, w):
        for obj in self.selected_objects:
            obj.set_selected(False)
        self.paint_area(w, self.selected_objects)
        self.selected_objects = []

    def select(self, w, objects):
        objs = []
        for obj in objects:
            if obj.is_selectable():
                obj.set_selected(True)
                objs.append(obj)
        self.selected_objects += objs
        self.paint_area(w, self.selected_objects)

    def paint_area(self, w, objetos):
        for o in objetos:
            o.repaint()

    def search(self, x, y):
        """
        Description:
            Return a object in the position (x, y) or None if is a empty point.
            Takes into account the axis z.
        """
        obj = None
        i = len(self.objects) - 1
        while i >= 0:
            o = self.objects[i]
            if o.contains(x, y):
                obj = o
                break
            i -= 1
        return obj

    def restore(self, w, cr):
        """
        Description:
            Restore the parameters of draw.
        :param w: The widget, this is, the canvas.
        :param cr: The Context Cairo
        """
        cr.set_line_width(1)
        cr.set_source_rgb(0, 0, 0)

    def change_position_in_z(self, num):
        pass

    # EVENTS

    def ev_click(self, w, e):
        """
        Description:
            Event generated when you click on the canvas.

        Parameters:
            w -- Is the canvas.
            e -- the Gdk.EventButton which triggered this signal.
        """
        self.grab_focus()
        if e.type == Gdk.EventType.BUTTON_PRESS:
            # Simple click
            if e.button == 1:
                if self.verbose:
                    print ("Left click")
                # Left click
                self.ev_left_click(w, e)
            elif e.button == 3:
                if self.verbose:
                    print ("Right click")
                # Right click
                self.ev_right_click(w, e)
        elif e.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            # Double click
            if self.verbose:
                print ("Double click")

    def ev_right_click(self, w, e):
        """
        Description:
            Event generated when you right click on the canvas.

        Parameters:
            w -- Is the canvas.
            e -- the Gdk.EventButton which triggered this signal.
        """
        x = e.x
        y = e.y
        obj = self.search(x, y)
        empty_point = obj is None

        self.deselect(w)
        if empty_point:
            self.ev_right_click_in_empty_point(w, x, y)
        else:
            self.ev_right_click_in_object(w, x, y)
            self.select(w, [obj])
            obj.ev_right_click(x, y)

    def ev_right_click_in_empty_point(self, w, x, y):
        if self.verbose:
            print ("Right click in empty point: %f, %f" % (x, y))

    def ev_right_click_in_object(self, w, x, y):
        if self.verbose:
            print ("Right click in object: %f, %f" % (x, y))

    def ev_left_click(self, w, e):
        """
        Description:
            Event generated when you left click on the canvas.

        Parameters:
            w -- Is the canvas.
            e -- the Gdk.EventButton which triggered this signal.
        """
        x = e.x
        y = e.y

        self.mouse_movement.set_point((x, y))

        for o in self.objects:
            i = o.is_outline(x, y)
            if i >= 0:
                self.scaling = True
                self.corner = i
                return

        obj = self.search(x, y)
        empty_point = obj is None

        if self.allow_multiple_selection and e.state & Gdk.ModifierType.CONTROL_MASK:
            if self.verbose:
                print ("Multiple selection")
            if empty_point:
                self.ev_left_click_in_empty_point(w, x, y)
            else:
                selected = False
                for o in self.selected_objects:
                    if obj.get_name() == o.get_name():
                        selected = True
                        break
                self.ev_left_click_in_object(w, x, y)
                if selected:
                    # Object selected previously
                    # Nothing
                    pass
                else:
                    # Not selected
                    self.select(w, [obj])
                obj.ev_left_click(x, y)
        else:
            if empty_point:
                # Deselect the objects.
                self.ev_left_click_in_empty_point(w, x, y)
                self.deselect(w)
            else:
                selected = False
                for o in self.selected_objects:
                    if obj.get_name() == o.get_name():
                        selected = True
                        break
                self.ev_left_click_in_object(obj, x, y)
                if selected:
                    # Object selected previously
                    # Nothing
                    pass
                else:
                    # Not selected
                    self.deselect(w)
                    self.select(w, [obj])
                obj.ev_left_click(x, y)

    def ev_left_click_in_empty_point(self, w, x, y):
        if self.verbose:
            print("Left click in empty point: %f, %f" % (x, y))

    def ev_left_click_in_object(self, obj, x, y):
        if self.verbose:
            print("Left click in object: %f, %f" % (x, y))

    def ev_selection_area(self, w, e):
        if not self.allow_selection_area:
            return
        if self.verbose:
            print("Selection area")

        if self.selection_area is None:
            self.selection_area = SelectionArea(e.x, e.y)
            self.selection_area.set_canvas(self)
        else:
            s = self.mouse_movement.get_vector()
            self.selection_area.move(s)

    def ev_draw(self, w, cr):
        for obj in self.objects:
            self.restore(w, cr)
            obj.draw(w, cr)
        for obj in self.objects:
            self.restore(w, cr)
            obj.draw_outline(w, cr)
        if self.selection_area is not None:
            self.restore(w, cr)
            self.selection_area.draw(w, cr)

    def ev_end_selection_area(self, w, e):
        """
        if self.selection_area is not None:
            self.selection_area.set_hidden(True)
            self.selection_area.repaint()
            self.selection_area = None
        """
        pass

    def ev_release(self, w, e):
        if self.verbose:
            print ("Release %f, %f" % (e.x, e.y))
        self.ev_end_selection_area(w, e)
        self.ev_end_moving_objects(w, e)
        if self.scaling:
            self.ev_end_scaling_object(w, e)
        self.mouse_movement = MouseMovement()

    def ev_move(self, w, e):
        x = e.x
        y = e.y
        if self.scaling:
            if self.verbose:
                print ("Scaling....")
            self.mouse_movement.set_point((x, y))
            self.ev_scaling_object(w, e)
        elif e.state & Gdk.ModifierType.BUTTON1_MASK:
            if self.verbose:
                print ("Dragging")
            self.mouse_movement.set_point((x, y))
            if len(self.selected_objects) > 0:
                self.ev_moving_objects(w, e)
            else:
                self.ev_selection_area(w, e)
        self.mouse_movement_follower.set_point((x, y))
        v = self.mouse_movement_follower.get_vector()
        if v is not None:
            for o in self.objects:
                if o.is_follower():
                    o.set_following(True)
                    o.move(v)

    def ev_end_moving_objects(self, w, e):
        self.window_gdk.set_cursor(self.ARROW)
        for o in self.selected_objects:
            o.set_moving(False)
        self.paint_area(w, self.selected_objects)

    def ev_moving_objects(self, w, e):
        if self.verbose:
            print ("Moving objects")
        self.window_gdk.set_cursor(self.HAND2)

        s = self.mouse_movement.get_vector()
        for o in self.selected_objects:
            if o.is_movable():
                o.set_moving(True)
                o.move(s)

    def ev_scaling_object(self, w, e):
        for o in self.selected_objects:
            if o.is_expandable():
                o.set_expanding(True)
                s = self.mouse_movement.get_vector()
                o.scale(s, self.corner)

    def ev_end_scaling_object(self, w, e):
        print ("End scale")
        self.scaling = False
        for o in self.selected_objects:
            o.set_expanding(False)

    def ev_key_pressed(self, w, e):
        if self.verbose:
            print ("Key %d" % (e.keyval))
        if e.state == Gdk.ModifierType.CONTROL_MASK and e.keyval == 65362:
            # Flecha de arriba
            pass
        elif e.state == Gdk.ModifierType.CONTROL_MASK and e.keyval == 65364:
            # Flecha de abajo
            pass
        elif e.state == Gdk.ModifierType.CONTROL_MASK and e.keyval == 43:
            # Tecla más (+)
            for o in self.selected_objects:
                s = Vector(5, 5)
                o.scale(s)
        elif e.state == Gdk.ModifierType.CONTROL_MASK and e.keyval == 45:
            # Tecla menos (-)
            for o in self.selected_objects:
                s = Vector(-5, -5)
                o.scale(s)
        for o in self.objects:
            o.ev_key_pressed(w, e)


class Flags():
    MOVING_OBJECTS = False
    SCALING_OBJECT = False
    SELECTION_AREA = False
    FOLLOWING = False

    LEFT_TOP_CORNER = 0
    RIGHT_TOP_CORNER = 1
    RIGHT_BOTTOM_CORNER = 2
    LEFT_BOTTOM_CORNER = 3

    MIDDLE_TOP = 4
    MIDDLE_RIGHT = 5
    MIDDLE_BOTTOM = 6
    MIDDLE_LEFT = 7


class MouseMovement():
    def __init__(self):
        self.v = None
        self.p1 = None
        self.p2 = None

    def set_point(self, p):
        if self.p1 is None:
            self.p1 = p
        else:
            self.p2 = p
            x = self.p2[0] - self.p1[0]
            y = self.p2[1] - self.p1[1]
            self.v = Vector(x, y)
            self.p1 = self.p2

    def get_vector(self):
        return self.v


class Square:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def contains(self, x, y):
        return x >= self.x and x <= self.x + self.width and y >= self.y and y <= self.y + self.height

    def draw(self, w, cr):
        cr.rectangle(self.x, self.y, self.width, self.height)
        cr.fill()

    def scale(self, s):
        self.move(s)

    def move(self, s):
        self.x = self.x + s.get_x()
        self.y = self.y + s.get_y()


class Outline():
    def __init__(self, obj):
        self.obj = obj
        self.length_square = 6
        self.half = self.length_square / 2
        self.x = self.obj.get_x() + 1
        self.y = self.obj.get_y() + 1
        self.width = self.obj.get_width() - 2
        self.height = self.obj.get_height() - 2
        self._load_squares()

    def _load_squares(self):
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        self.squares = [
            Square(x - self.half, y - self.half, self.length_square, self.length_square),
            Square(x + width - self.half, y - self.half, self.length_square, self.length_square),
            Square(x + width - self.half, y + height - self.half, self.length_square, self.length_square),
            Square(x - self.half, y + height - self.half, self.length_square, self.length_square),

            Square(x - self.half + width / 2, y - self.half, self.length_square, self.length_square),
            Square(x - self.half + width, y - self.half + height / 2, self.length_square, self.length_square),
            Square(x - self.half + width / 2, y - self.half + height, self.length_square, self.length_square),
            Square(x - self.half, y - self.half + height / 2, self.length_square, self.length_square)
        ]

    def contains(self, x, y):
        b = False
        i = 0
        k = -1
        for s in self.squares:
            b = b or s.contains(x, y)
            if b:
                k = i
                break
            i += 1
        return k

    def move(self, s):
        for sq in self.squares:
            sq.move(s)

    def scale(self, s):
        self.x = self.obj.get_x() + 1
        self.y = self.obj.get_y() + 1
        self.width = self.obj.get_width() - 2
        self.height = self.obj.get_height() - 2
        self._load_squares()

    def load_squares(self):
        self._load_squares()

    def draw(self, w, cr):
        cr.set_line_width(1)
        cr.set_dash([5])
        cr.set_source_rgb(0, 0, 0)

        if self.obj.is_expandable():
            for s in self.squares:
                s.draw(w, cr)

        x = self.obj.get_x()
        y = self.obj.get_y()
        width = self.obj.get_width()
        height = self.obj.get_height()
        cr.rectangle(x, y, width, height)
        cr.stroke()

    def repaint(self, w):
        obj = self.obj
        w.queue_draw_area(obj.get_x() - self.half, obj.get_y() - self.half,
                          obj.get_width() + self.length_square + 2, obj.get_height() + self.length_square + 2)


class Vector():
    """
    Description:
        This class represents a two-dimensional vector.
        This is, a position (x, y) or also a (angle, length).
    """
    def __init__(self, x, y):
        super(Vector, self).__init__()
        self.x = x
        self.y = y
        self.calculate_angle_and_length()

    def calculate_angle_and_length(self):
        if self.y == 0 and self.x == 0:
            self.angle = 0
            self.length = 0
        else:
            if self.x != 0:
                if self.y >= 0:
                    self.angle = math.atan2(self.y, self.x)
                else:
                    self.angle = 2 * math.pi + math.atan2(self.y, self.x)
            else:
                if self.y > 0:
                    self.angle = math.pi / 2
                else:
                    self.angle = -math.pi / 2
            self.length = math.hypot(self.x, self.y)

    def calculate_x_and_y(self):
        self.x = self.length * math.cos(self.angle)
        self.y = self.length * math.sin(self.angle)

    def get_angle(self):
        return self.angle

    def get_angle_in_radians(self):
        return self.get_angle()

    def get_angle_in_degrees(self):
        return math.degrees(self.angle)

    def get_length(self):
        return self.length

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_angle(self, new_angle):
        self.angle = new_angle
        self.calculate_x_and_y()

    def set_angle_in_radians(self, new_angle):
        self.set_angle(new_angle)

    def set_angle_in_degrees(self, new_angle_in_degree):
        self.angle = math.radians(new_angle_in_degree)
        self.calculate_x_and_y()

    def set_length(self, new_length):
        self.length = new_length
        self.calculate_x_and_y()

    def set_x(self, new_x):
        self.x = new_x
        self.calculate_angle_and_length()

    def set_y(self, new_y):
        self.y = new_y
        self.calculate_angle_and_length()


class ObjectCanvas():

    def __init__(self):
        super(ObjectCanvas, self).__init__()

        # Actions
        self.selectable = True
        self.movable = True
        self.expandable = True
        self.rotable = True
        self.follower = False
        self.allow_change_z = True

        # Action data
        self.selected = False
        self.moving = False
        self.expanding = False
        self.rotating = False
        self.following = False
        self.hidden = False

        # Geometric data
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.angle = 0
        self.min_width = 5
        self.min_height= 5

        # Other data
        self.name = "%f" % (time.time())
        self.canvas = None
        self.outline = None

    def get_canvas(self):
        return self.canvas

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def get_name(self):
        return self.name

    def get_outline(self):
        return self.outline

    def get_x(self):
        return self.x

    def get_xm(self):
        return self.x + self.width / 2

    def get_y(self):
        return self.y

    def get_ym(self):
        return self.y + self.height / 2

    def is_allow_change_z(self):
        return self.allow_change_z

    def is_expandable(self):
        return self.expandable

    def is_expanding(self):
        return self.expanding

    def is_follower(self):
        return self.follower

    def is_following(self):
        return self.following

    def is_hidden(self):
        return self.hidden

    def is_movable(self):
        return self.movable

    def is_moving(self):
        return self.moving

    def is_rotable(self):
        return self.rotable

    def is_rotating(self):
        return self.rotating

    def is_selectable(self):
        return self.selectable

    def is_selected(self):
        return self.selected

    def set_canvas(self, canvas):
        self.canvas = canvas

    def set_height(self, height):
        self.height = height

    def set_width(self, width):
        self.width = width

    def set_allow_change_z(self, cz):
        self.allow_change_z = cz

    def set_expandable(self, e):
        self.expandable = e

    def set_expanding(self, e):
        self.expanding = e

    def set_follower(self, f):
        self.follower = f

    def set_following(self, f):
        self.following = f

    def set_hidden(self, h):
        self.hidden = h

    def set_movable(self, m):
        self.movable = m

    def set_moving(self, m):
        self.moving = m

    def set_outline(self, o):
        self.outline = o

    def set_rotable(self, r):
        self.rotable = r

    def set_rotating(self, r):
        self.rotating = r

    def set_selectable(self, s):
        self.selectable = s

    def set_selected(self, s):
        self.selected = s

    def set_name(self, name):
        self.name = name

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def ev_add(self, position_z):
        print ("Agregado en la posición ", position_z)

    def ev_right_click(self, x, y):
        pass

    def ev_left_click(self, x, y):
        pass

    def ev_key_pressed(self, w, e):
        pass

    def is_outline(self, x, y):
        if self.selected:
            return self.outline.contains(x, y)
        return -2

    def contains(self, x, y):
        xf = self.x + self.width
        yf = self.y + self.height
        b = self.x <= x and xf >= x and self.y <= y and yf >= y
        return b

    def scale(self, s, corner):
        old_x = self.get_x()
        old_y = self.get_y()
        old_width = self.get_width()
        old_height = self.get_height()
        dx = s.get_x()
        dy = s.get_y()
        if corner == Flags.LEFT_TOP_CORNER:
            new_x = self.get_x() + s.get_x()
            new_y = self.get_y() + s.get_y()
            new_width = self.get_width() - s.get_x()
            new_height = self.get_height() - s.get_y()
        elif corner == Flags.RIGHT_TOP_CORNER:
            new_x = self.get_x()
            new_y = self.get_y() + s.get_y()
            new_width = self.get_width() + s.get_x()
            new_height = self.get_height() - s.get_y()
        elif corner == Flags.RIGHT_BOTTOM_CORNER:
            new_x = self.get_x()
            new_y = self.get_y()
            new_width = self.get_width() + s.get_x()
            new_height = self.get_height() + s.get_y()
        elif corner == Flags.LEFT_BOTTOM_CORNER:
            new_x = self.get_x() + s.get_x()
            new_y = self.get_y()
            new_width = self.get_width() - s.get_x()
            new_height = self.get_height() + s.get_y()
        elif corner == Flags.MIDDLE_TOP:
            new_x = self.get_x()
            new_y = self.get_y() + s.get_y()
            new_width = self.get_width()
            new_height = self.get_height() - s.get_y()
        elif corner == Flags.MIDDLE_RIGHT:
            new_x = self.get_x()
            new_y = self.get_y()
            new_width = self.get_width() + s.get_x()
            new_height = self.get_height()
        elif corner == Flags.MIDDLE_BOTTOM:
            new_x = self.get_x()
            new_y = self.get_y()
            new_width = self.get_width()
            new_height = self.get_height() + s.get_y()
        elif corner == Flags.MIDDLE_LEFT:
            new_x = self.get_x() + s.get_x()
            new_y = self.get_y()
            new_width = self.get_width() - s.get_x()
            new_height = self.get_height()

        if new_width < self.min_width or new_height < self.min_height:
            return

        self.set_x(new_x)
        self.set_y(new_y)
        self.set_width(new_width)
        self.set_height(new_height)
        #if new_width >= self.min_width:
        #    self.set_width(new_width)

        #if new_height >= self.min_height:
        #    self.set_height(new_height)

        #new_x = self.get_x() - dx
        #new_y = self.get_y() - dy
        #self.set_x(new_x)
        #self.set_y(new_y)

        if self.outline is not None:
            self.outline.scale(s)
        if self.canvas is not None:
            self.canvas.queue_draw_area(old_x - 5, old_y - 5, old_width + 15, old_height + 15)
            self.repaint()

    def rotate(self, s):
        pass

    def move(self, s):
        old_x = self.get_x()
        old_y = self.get_y()
        new_x = s.get_x() + self.get_x()
        new_y = s.get_y() + self.get_y()
        self.set_x(new_x)
        self.set_y(new_y)
        self.outline.move(s)
        if self.canvas is not None:
            self.canvas.queue_draw_area(old_x - 5, old_y - 5, self.width + 15, self.height + 15)
            self.repaint()

    def repaint(self):
        if self.canvas is not None:
            self.canvas.queue_draw_area(self.x, self.y, self.width + 1, self.height + 1)
            self.outline.repaint(self.canvas)

    def draw(self, w, cr):
        pass
       
    def draw_outline(self, w, cr):
        if self.selected:
            self.outline.draw(w, cr)


class RectangleCanvas(ObjectCanvas):

    def __init__(self):
        super(RectangleCanvas, self).__init__()
        self.rgb_no_selected = (0, 0, 255)
        self.rgb_selected = (0, 255, 0)

    def set_rgb_no_selected(self, rgb):
        self.rgb_no_selected = rgb

    def set_rgb_selected(self, rgb):
        self.rgb_selected = rgb

    def draw(self, w, cr):
        if self.selected:
            cr.set_source_rgb(self.rgb_selected[0], self.rgb_selected[1], self.rgb_selected[2])
        else:
            cr.set_source_rgb(self.rgb_no_selected[0], self.rgb_no_selected[1], self.rgb_no_selected[2])
        cr.rectangle(self.x, self.y, self.width, self.height)
        cr.fill()

class CircleCanvas(ObjectCanvas):

    def __init__(self, xc, yc, radio):
        super(CircleCanvas, self).__init__()
        self.radio = radio
        self.x = xc - radio
        self.y = yc - radio
        self.width = radio * 2
        self.height = radio * 2
        self.rgb_no_selected = (0, 0, 255)
        self.rgb_selected = (0, 255, 0)

    def set_rgb_no_selected(self, rgb):
        self.rgb_no_selected = rgb

    def set_rgb_selected(self, rgb):
        self.rgb_selected = rgb

    def draw(self, w, cr):
        if self.selected and self.moving:
            cr.set_source_rgb(255, 0, 0)
        elif self.selected:
            cr.set_source_rgb(self.rgb_selected[0], self.rgb_selected[1], self.rgb_selected[2])
        else:
            cr.set_source_rgb(self.rgb_no_selected[0], self.rgb_no_selected[1], self.rgb_no_selected[2])
        cr.save()
        cr.translate(self.get_x() + self.get_width() / 2., self.get_y() + self.get_height() / 2.)
        cr.scale(self.get_width() / 2., self.get_height() / 2.)
        cr.arc(0., 0., 1., 0., 2 * math.pi)
        #cr.arc(self.x + self.radio, self.y + self.radio, self.radio, 0, math.pi * 2)
        cr.restore()
        cr.fill()


class LineCanvas(ObjectCanvas):

    def __init__(self):
        super(LineCanvas, self).__init__()

    def draw(self, w, cr):
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(self.x, self.y)
        cr.line_to(self.width + self.x, self.height + self.y)
        cr.stroke()


class ImageCanvas(ObjectCanvas):

    def __init__(self, url_image):
        super(ImageCanvas, self).__init__()
        self.url_image = url_image
        self.image = cairo.ImageSurface.create_from_png(self.url_image)
        self.set_width(self.image.get_width())
        self.set_height(self.image.get_height())
        self.expandable = False

    def draw(self, w, cr):
        #cr.save()
        #width_ratio = float(self.get_width()) / float(self.image.get_width())
        #height_ratio = float(self.get_height()) / float(self.image.get_height())
        #scale_xy = min(height_ratio, width_ratio)
        #cr.scale(0.2, 0.2)
        cr.set_source_surface(self.image, self.get_x(), self.get_y())
        cr.paint()
        #cr.restore()


class AnimationRectangleCanvas(RectangleCanvas):

    def __init__(self):
        super(AnimationRectangleCanvas, self).__init__()
        self.counter = 1
        self.animation_function = None
        self.delay = 30
        self.expandable = False

    def anim(self):
        self.move(Vector(5, 0))
        self.counter += 1
        if self.get_x() > 400:
            self.set_x(50)
        return True

    def start(self):
        GObject.timeout_add(self.delay, self.anim)


class SelectionArea(ObjectCanvas):

    def __init__(self, pfx, pfy):
        super(SelectionArea, self).__init__()
        self.pfx = pfx
        self.pfy = pfy
        self.x = pfx
        self.y = pfy
        self.width = 0
        self.height = 0

    def move(self, s):
        pass

    def repaint(self):
        self.canvas.queue_draw_area(self.x, self.y, self.width + 1, self.height + 1)

    def draw(self, w, cr):
        cr.set_source_rgba(0, 0, 0, 0.1)
        cr.rectangle(self.x, self.y, self.width, self.height)
        cr.fill()
