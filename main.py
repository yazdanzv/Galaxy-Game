from kivy import platform
from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget


class MainWidget(Widget):
    from actions import on_keyboard_up, on_keyboard_down, keyboard_closed, on_touch_down, on_touch_up
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    vertical_lines = []
    horizontal_lines = []
    Vline_number = 16
    Vline_spacing = .2
    Hline_number = 6
    Hline_spacing = .1

    speed_y = 2
    current_offset_y = 0

    speed_x = 12
    current_speed_x = 0
    current_offset_x = 0

    tile = None
    ti_x = 0
    ti_y = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()

        # Checking the platform
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        # Updating the code to make you think you are moving
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def is_desktop(self):
        if platform in ('linux', 'win', 'macos'):
            return True
        else:
            return False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            self.tile = Quad()

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.Vline_number):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.Hline_number):
                self.horizontal_lines.append(Line())

    def get_line_x_from_index(self, index):
        offset = index - 0.5
        spacing = int(self.perspective_point_x + offset * self.Vline_spacing * self.width) + self.current_offset_x
        return spacing

    def update_vertical_lines(self):
        start_number = -int(self.Vline_number / 2) + 1
        for i in range(start_number, start_number + self.Vline_number):
            spacing = self.get_line_x_from_index(i)
            x1, y1 = self.transform(spacing, 0)
            x2, y2 = self.transform(spacing, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def get_line_y_from_index(self, index):
        spacing = self.height * self.Hline_spacing
        line_y = index * spacing - self.current_offset_y
        return line_y

    def update_horizontal_lines(self):
        start_number = -int(self.Vline_number / 2) + 1
        end_number = start_number + self.Vline_number - 1
        min_x = self.get_line_x_from_index(start_number)
        max_x = self.get_line_x_from_index(end_number)
        for i in range(self.Hline_number):
            y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(min_x, y)
            x2, y2 = self.transform(max_x, y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def get_tiles_coordinate(self, ti_x, ti_y):
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def transform(self, x, y):
        tr_y = (y * self.perspective_point_y / self.height)
        if tr_y > self.perspective_point_y:
            tr_y = self.perspective_point_y
        dif_y = self.perspective_point_y - tr_y
        dif_x = x - self.perspective_point_x
        factor_y = dif_y / self.perspective_point_y
        factor_y = pow(factor_y, 4)
        tr_x = self.perspective_point_x + dif_x * factor_y
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
        return int(tr_x), int(tr_y)

    def update_tiles(self):
        pass

    def update(self, dt):
        time_factor = dt * 60.0
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.current_offset_x += self.current_speed_x * time_factor
        if self.current_offset_y >= self.Hline_spacing * self.height:
            self.current_offset_y -= self.Hline_spacing * self.height
        else:
            self.current_offset_y += self.speed_y * time_factor


class GalaxyApp(App):
    pass


GalaxyApp().run()
