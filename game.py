import pygame
from frog import Frog
from car import Car
from log import Log
from settings import TILE_SIZE

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.frog = Frog(7 * TILE_SIZE, 14 * TILE_SIZE)
        self.cars = []
        self.cars.append(Car(5 * TILE_SIZE, 12 * TILE_SIZE, 1, 1))
        self.cars.append(Car(7 * TILE_SIZE, 9 * TILE_SIZE, 2, 0))
        self.logs = []
        self.logs.append(Log(8 * TILE_SIZE, 6 * TILE_SIZE, 0.5, 1))
        self.logs.append(Log(1 * TILE_SIZE, 3 * TILE_SIZE, 1.5, 0))


    def update(self):
        self.frog.update()
        for car in self.cars:
            car.update()
        for log in self.logs:
            log.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for log in self.logs:
            log.draw(self.screen)
        self.frog.draw(self.screen)
        for car in self.cars:
            car.draw(self.screen)