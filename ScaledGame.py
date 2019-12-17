import pygame
from pygame.locals import *
import os

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