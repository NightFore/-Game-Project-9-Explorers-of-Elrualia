import pygame
from pygame.locals import *
import os
from os import path
import pytmx
vec = pygame.math.Vector2

"""
    Settings
"""
# Main Settings
project_title = "Explorers of Elrualia"
screen_size = WIDTH, HEIGHT = 800, 640
FPS = 60

# Secondary Settings
TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Game Settings
PLAYER_SPEED = 300

# Layer Settings
LAYER_PLAYER = 1

"""
    Colors
"""
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255

YELLOW = 255, 255, 0
MAGENTA = 255, 0, 255
CYAN = 0, 255, 255

LIGHTGREY = 100, 100, 100

BLACK = 0, 0, 0
WHITE = 255, 255, 255

"""
    Helpful Classes
"""
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Limit to map size
        x = min(0, x)  # Left
        x = max(-(self.width - WIDTH), x)  # Right
        y = min(0, y)  # Top
        y = max(-(self.height - HEIGHT), y)  # Bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)


class Map:
    def __init__(self, filename):
        self.tmxdata = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.tmxdata.width * self.tmxdata.tilewidth
        self.height = self.tmxdata.height * self.tmxdata.tileheight

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


"""
    Helpful Functions
"""
def update_time_dependent(sprite):
    sprite.current_time += sprite.dt
    if sprite.current_time >= sprite.animation_time:
        sprite.current_time = 0
        sprite.index = (sprite.index + 1) % len(sprite.images)
        sprite.image = sprite.images[sprite.index]
    sprite.rect = sprite.image.get_rect()
    sprite.rect.center = sprite.pos
    sprite.image = pygame.transform.rotate(sprite.image, 0)


def update_bobbing(sprite):
    offset = BOB_RANGE * (sprite.tween(sprite.step / BOB_RANGE) - 0.5)
    sprite.rect.centery = sprite.pos.y + offset * sprite.dir
    sprite.step += BOB_SPEED
    if sprite.step > BOB_RANGE:
        sprite.step = 0
        sprite.dir *= -1


def load_file(path, image=False):
    file = []
    for file_name in os.listdir(path):
        if image:
            file.append(pygame.image.load(path + os.sep + file_name).convert_alpha())
        else:
            file.append(path + os.sep + file_name)
    return file


def load_image(image_path, image_list):
    images = []
    for image in image_list:
        images.append(pygame.image.load(path.join(image_path, image)).convert_alpha())
    return images


def load_tile_table(filename, width, height, colorkey=(0, 0, 0)):
    image = pygame.image.load(filename).convert()
    image.set_colorkey(colorkey)
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_y in range(int(image_height / height)):
        line = []
        tile_table.append(line)
        for tile_x in range(int(image_width / width)):
            rect = (tile_x * width, tile_y * height, width, height)
            line.append(image.subsurface(rect))
    return tile_table


def transparent_surface(width, height, color, border, colorkey=(0, 0, 0)):
    surface = pygame.Surface((width, height)).convert()
    surface.set_colorkey(colorkey)
    surface.fill(color)
    surface.fill(colorkey, surface.get_rect().inflate(-border, -border))
    return surface


"""
    Game
"""
class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.init()
        pygame.key.set_repeat(300, 75)
        self.gameDisplay = ScaledGame(project_title, screen_size, 60)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(FPS) / 1000
        self.load_data()
        self.new()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.gameDisplay.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        data_folder = path.join(game_folder, "data")
        graphics_folder = path.join(data_folder, "graphics")
        sfx_folder = path.join(data_folder, "sfx")
        voice_folder = path.join(data_folder, "voice")
        music_folder = path.join(data_folder, "music")
        map_folder = path.join(data_folder, "map")

        # Font
        self.font = None

        # Pause Screen
        self.dim_screen = pygame.Surface(self.gameDisplay.get_size()).convert_alpha()
        self.dim_screen.fill((100, 100, 100, 120))

        # Map
        self.map = Map(path.join(map_folder, "Map_1.tmx"))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        # Music
        self.music = "music_aaron_krogh_310_world_map.mp3"

        # Image Items
        self.item_images = {}

        # Image Effects
        self.effect_images = {}

        # Sound Effects
        self.sounds_effects = {}

        # Sound Voices
        self.sounds_voice = {}

        # Sound Musics
        pygame.mixer.music.load(path.join(music_folder, self.music))

    def new(self):
        self.paused = False
        self.camera = Camera(self.map.width, self.map.height)
        self.all_sprites = pygame.sprite.LayeredUpdates()

        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width/2, tile_object.y + tile_object.height/2)
            if tile_object.name == "player":
                self.player = Player(self, obj_center.x, obj_center.y)

    def run(self):
        self.playing = True
        pygame.mixer.music.play(-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit_game(self):
        pygame.quit()
        quit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()
                if event.key == pygame.K_p:
                    self.paused = not self.paused

                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.move(dx=-1)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move(dx=+1)
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.move(dy=-1)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.player.move(dy=+1)

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw(self):
        # Map
        self.gameDisplay.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        # Grid
        for col in range(WIDTH // TILESIZE):
            for row in range(HEIGHT // TILESIZE):
                pygame.draw.rect(self.gameDisplay, (100, 100, 100), self.camera.apply_rect(pygame.Rect(TILESIZE * col, TILESIZE * row, TILESIZE, TILESIZE)), 1)

        # Sprite
        for sprite in self.all_sprites:
            self.gameDisplay.blit(sprite.image, self.camera.apply(sprite))

        # Pause
        if self.paused:
            self.gameDisplay.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")


        self.gameDisplay.update()


class ScaledGame(pygame.Surface):
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center window position
    game_size = None
    ss = None
    screen = None
    clock = None
    resize = True
    zoom = False
    game_gap = None
    game_scaled = None
    title = None
    fps = True
    set_fullscreen = False
    factor_w = 1
    factor_h = 1

    def __init__(self, title, game_size, FPS, first_screen=False):
        # Title
        self.title = title
        pygame.display.set_caption(self.title)

        # Window Settings
        self.game_size = game_size
        self.ss = game_size
        self.game_gap = (0, 0)

        # Required to set a good resolution for the game screen
        self.screen_info = pygame.display.Info()

        if not first_screen:
            self.screen = pygame.display.set_mode(game_size, RESIZABLE)
        else:
            # Take 120 pixels from the height because of the menu bar, window bar and dock takes space
            first_screen = (self.screen_info.current_w, self.screen_info.current_h - 120)
            self.screen = pygame.display.set_mode(first_screen, RESIZABLE)

        # Sets up the Surface for the game.
        pygame.Surface.__init__(self, self.game_size)

        # Game Settings
        self.FPS = FPS
        self.clock = pygame.time.Clock()

    def get_resolution(self, ss, gs):
        gap = float(gs[0]) / float(gs[1])  # Game aspect ratio
        sap = float(ss[0]) / float(ss[1])  # Scaled aspect ratio
        if gap > sap:
            # Divides the height by the factor which the width changes so the aspect ratio remains the same.
            factor = float(gs[0]) / float(ss[0])
            new_h = gs[1] / factor
            game_scaled = (ss[0], new_h)
        elif gap < sap:
            # Divides the width by the factor which the height changes so the aspect ratio remains the same.
            factor = float(gs[1]) / float(ss[1])
            new_w = gs[0] / factor
            game_scaled = (new_w, ss[1])
        else:
            game_scaled = self.screen.get_size()
        return game_scaled

    def fullscreen(self):
        if not self.set_fullscreen:
            self.screen = pygame.display.set_mode(self.game_size, FULLSCREEN)
            self.factor_w = 1
            self.factor_h = 1
            self.set_fullscreen = True
        else:
            self.resize = True
            self.set_fullscreen = False

    def update(self):
        # Display FPS in window title
        global ss
        if self.fps:
            pygame.display.set_caption(self.title + " - " + str(int(self.clock.get_fps())) + "fps")

        # Updates screen properly
        win_size_done = False  # Changes to True if the window size is got by the VIDEORESIZE event below
        for event in pygame.event.get():
            if event.type == VIDEORESIZE:
                ss = [event.w, event.h]
                self.resize = True
                win_size_done = True

                if ss[0] == self.screen_info.current_w:
                    self.zoom = True

        # Fullscreen
        if self.set_fullscreen:
            self.screen.blit(self, self.game_gap)

        # Resize
        elif self.resize:
            # Sizes not gotten by resize event
            if not win_size_done:
                ss = [self.screen.get_width(), self.screen.get_height()]

            # Zoom
            if self.zoom and ss[0] != self.screen_info.current_w and ss[1] != self.ss[1]:
                self.game_scaled = self.game_size
                self.zoom = False
            else:
                self.game_scaled = self.get_resolution(ss, self.game_size)
                self.game_scaled = int(self.game_scaled[0]), int(self.game_scaled[1])

            # Scale game to screen resolution, keeping aspect ratio
            self.screen = pygame.display.set_mode(self.game_scaled, RESIZABLE)
            self.resize = False

            # Usable Variables
            self.factor_w = self.game_scaled[0] / self.get_width()
            self.factor_h = self.game_scaled[1] / self.get_height()
            self.ss = ss

        # Add game to screen with the scaled size and gap required.
        self.screen.blit(pygame.transform.scale(self, self.game_scaled), self.game_gap)

        pygame.display.flip()
        self.clock.tick(self.FPS)


"""
    Others Functions
"""
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Setup
        self.game = game
        self.groups = self.game.all_sprites
        self._layer = LAYER_PLAYER
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Position
        self.x = int(x/TILESIZE)
        self.y = int(y/TILESIZE)

        # Surface
        self.image = transparent_surface(TILESIZE, TILESIZE, YELLOW, 6)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy

    def update(self):
        # Position
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE


g = Game()
while True:
    g.new()
    g.run()
