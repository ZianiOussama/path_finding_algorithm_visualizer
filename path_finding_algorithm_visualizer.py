import math

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivymd.app import MDApp

is_there_start = False
is_there_target = False

WHIT = [1, 1, 1, 1]
BLACK = [0, 0, 0, 1]
BLUE = [0, .5, 1, 1]
ORANGE = [1, .5, 0, 1]
GREEN = [0, .9, 0, 1]
RED = [.9, 0, 0, 1]
PURPLE = [.5, 0, .5, 1]


class Rect(Widget):
    color = ListProperty(WHIT)

    def __init__(self, **kwargs):
        super(Rect, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        global is_there_start
        global is_there_target
        x, y = touch.pos
        if self.collide_point(x, y):

            if not is_there_start and self.color != BLUE:
                self.color = ORANGE
                is_there_start = True

            elif not is_there_target and self.color != ORANGE:
                self.color = BLUE
                is_there_target = True
            else:
                if self.color == BLACK:
                    self.color = WHIT
                elif self.color == ORANGE:
                    self.color = WHIT
                    is_there_start = False
                elif self.color == BLUE:
                    self.color = WHIT
                    is_there_target = False
                else:
                    self.color = BLACK
            return True
        else:
            return super(Rect, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        x, y = touch.pos
        if self.collide_point(x, y):
            self.color = BLACK
            return True
        else:
            return super(Rect, self).on_touch_down(touch)


class Grid(GridLayout):
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self.rows = 34
        self.cols = 41
        self.spacing = 1
        [self.add_widget(Rect()) for _ in range(41 * 34)]

        self._keyboard = Window.request_keyboard(self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.edge_y = Window.height / self.rows
        self.edge_x = Window.width / self.cols
        self.current = None
        self.open_set = []
        self.closed_set = []
        self.end = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        global is_there_start
        global is_there_target

        if keycode[1] == 'enter' and is_there_start and is_there_target:
            self.a_star_algo()
        if text == ' ':
            self.clear_widgets()
            [self.add_widget(Rect()) for _ in range(41 * 34)]
            self.current = None
            self.open_set = []
            self.closed_set = []
            self.end = None

            is_there_start = False
            is_there_target = False
        if keycode[1] == 'escape':
            keyboard.release()
        return True

    def a_star_algo(self):
        start, self.end = self.get_start_and_end_nodes()
        self.set_costs(self.end)
        start.g_cost = 0
        self.open_set.append(start)
        self.event = Clock.schedule_interval(self.algo, 1 / 100)

    def algo(self, dt):
        current = self.open_set[0]
        self.open_set.pop(0)
        if current.color == GREEN:
            current.color = RED
        self.closed_set.append(current)

        if current == self.end:
            self.current = current
            self.event.cancel()
            self.path_drawing_event = Clock.schedule_interval(self.draw_path, 1 / 100)

        for neighbour in self.get_neighbours(current):
            if neighbour.color == BLACK or neighbour in self.closed_set:
                continue
            if self.is_new_path_shorter(current, neighbour) or neighbour not in self.open_set:
                neighbour.f_cost = neighbour.g_cost + neighbour.h_cost

                if neighbour not in self.open_set:
                    if neighbour.color == WHIT:
                        neighbour.color = GREEN
                    self.add_to_open_set(neighbour)

    def add_to_open_set(self, neighbour):
        if len(self.open_set) == 0:
            self.open_set.append(neighbour)
        else:
            for i in self.open_set:
                if neighbour.f_cost < i.f_cost:
                    idx = self.open_set.index(i)
                    self.open_set.insert(idx, neighbour)
                    return

    def is_new_path_shorter(self, current, neighbour):
        new_g = current.g_cost + 12
        if new_g < neighbour.g_cost:
            neighbour.g_cost = new_g
            neighbour.parent = current
            return True

    def set_costs(self, end):
        for child in self.children:
            a, b = abs(child.center[0] - end.center[0]), abs(child.center[1] - end.center[1])
            child.h_cost = math.sqrt((a**2) + (b**2))
            child.g_cost = float('inf')
            child.f_cost = child.h_cost

    def get_start_and_end_nodes(self):
        nodes = []
        for child in self.children:
            if child.color == BLUE:
                nodes.insert(0, child)
                if len(nodes) == 2:
                    return nodes
            if child.color == ORANGE:
                nodes.insert(1, child)
                if len(nodes) == 2:
                    return nodes

    def get_neighbours(self, node):
        neighbours = []
        for child in self.children:
            if child.collide_point(node.center[0] - self.edge_x, node.center[1]):
                neighbours.append(child)
            elif child.collide_point(node.center[0] + self.edge_x, node.center[1]):
                neighbours.append(child)
            elif child.collide_point(node.center[0], self.edge_y + node.center[1]):
                neighbours.append(child)
            elif child.collide_point(node.center[0], node.center[1] - self.edge_y):
                neighbours.append(child)

            """elif child.collide_point(node.center[0] - self.edge_x, node.center[1] + self.edge_y):
                neighbours.append(child)
            elif child.collide_point(node.center[0] + self.edge_x, node.center[1] + self.edge_y):
                neighbours.append(child)
            elif child.collide_point(node.center[0] - self.edge_x, node.center[1] - self.edge_y):
                neighbours.append(child)
            elif child.collide_point(node.center[0] + self.edge_x, node.center[1] - self.edge_y):
                neighbours.append(child)"""

        return neighbours

    def draw_path(self, dt):
        try:
            self.current.parent.color = PURPLE
            self.current = self.current.parent
        except AttributeError:
            self.path_drawing_event.cancel()


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Grid()


if __name__ == '__main__':
    app = MyApp()
    app.run()
