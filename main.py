from kivy.config import Config
from kivy.core.audio import SoundLoader

Config.set('graphics', 'width', '1300')
Config.set('graphics', 'height', '500')

import random
from kivy import platform
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file('menu.kv')


class MainWidget(RelativeLayout):
    from actions import on_keyboard_up, on_keyboard_down, keyboard_closed, on_touch_down, on_touch_up
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    label_text = StringProperty("G    A    L    A    X    Y")
    button_text = StringProperty("START")
    score_text = StringProperty('')
    vertical_lines = []
    horizontal_lines = []
    Vline_number = 16
    Vline_spacing = .2
    Hline_number = 8
    Hline_spacing = .1

    speed_y = 1
    current_offset_y = 0
    current_y_loop = 0

    speed_x = 3
    current_speed_x = 0
    current_offset_x = 0

    number_of_tiles = 40
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    game_over_state = False
    game_has_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.init_audio()
        self.pre_fill_coordinates()
        self.generate_tiles_coordinates()

        # Checking the platform
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        # Updating the code to make you think you are moving
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.sound_galaxy.play()

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.tiles_coordinates = []
        self.pre_fill_coordinates()
        self.generate_tiles_coordinates()
        self.score_text = ''

        self.game_over_state = False

    def is_desktop(self):
        if platform in ('linux', 'win', 'macos'):
            return True
        else:
            return False

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.number_of_tiles):
                self.tiles.append(Quad())

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tiles_coordinate(ti_x, ti_y)
        xmax, ymax = self.get_tiles_coordinate(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def pre_fill_coordinates(self):
        for i in range(10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0

        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_y = last_coordinate[1] + 1
            last_x = last_coordinate[0]

        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        for i in range(len(self.tiles_coordinates), self.number_of_tiles):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.Vline_number / 2) + 1
            end_index = start_index + self.Vline_number - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

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
        ti_y = ti_y - self.current_y_loop
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
        for i in range(self.number_of_tiles):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tiles_coordinate(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tiles_coordinate(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update(self, dt):
        time_factor = dt * 60.0
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.game_over_state and self.game_has_started:

            speed_y = self.speed_y * self.height / 200
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.Hline_spacing * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_text = "SCORE : " + str(self.current_y_loop)
                self.generate_tiles_coordinates()
                print("loop : " + str(self.current_y_loop))

            speed_x = self.current_speed_x * self.width / 200
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.game_over_state:
            self.game_over_state = True
            self.menu_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 3)
            self.label_text = "G   A   M   E   O   V   E   R"
            self.button_text = "RESTART"
            print("GAME OVER")

    def play_game_over_voice_sound(self, dt):
        if self.game_over_state:
            self.sound_gameover_voice.play()

    def on_button_clicked(self):
        if self.game_over_state:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.game_has_started = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


GalaxyApp().run()
