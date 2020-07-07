import pygame


class Screen:
    def __init__(self):
        pygame.init()
        self.pixel_size = 10
        self.screen_width = 64
        self.screen_height = 32

        self.size = self.screen_width * self.pixel_size, self.screen_height * self.pixel_size
        self.display = pygame.display.set_mode(self.size)
        self.black = [0, 0, 0]
        self.white = [255, 255, 255]

    def pixel(self, x, y, color):
        color_to_be = [color*255, color*255, color*255]
        pygame.draw.rect(self.display, color_to_be, (x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size))
        pygame.display.flip()

    def get_pixel(self, x, y):
        if self.display.get_at((x*self.pixel_size, y*self.pixel_size)) == (255, 255, 255, 255):
            return 1
        else:
            return 0

    def clear_screen(self):
        self.display.fill(self.black)
