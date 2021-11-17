__author__ = "Roberto Medina"
__copyright__ = "Copyright 2021, Roberto Carlos Medina"
__version__ = "0.0.1"
__maintainer__ = "Roberto Medina"
__email__ = "robertocarlosmedina.dev@gmail.com "
__status__ = "Production"

"""
    This is the class where all the game loop is controlled, and where all the action are
    controlled.

"""

import pygame
import numpy as np
from random import randint, choice
from time import sleep
from pygame import font
from src.support.font import Game_fonts as fonts
from src.support.colors import Game_color as color
from src.game_components.cube import Cube

class Game_loop:
    
    screen_size :tuple          # screen size info
    screen :pygame.Surface      # screen surface
    game_win :bool              # control if the game was won
    game_table :list            # store information about the game table
    game_events :pygame.event   # hold the current games events
    play_algorithm :str         # hold the current self playing algorithms
    cube_sizes :dict            # store all the information about the cubes
    game_cubes :list            # list of objets related to the cubes on th game

    def __init__(self, screen :pygame.Surface, screen_size :list, algorithm = None ) -> None:
        self.screen = screen
        self.screen_size = screen_size
        self.play_algorithm = algorithm
        self.game_cubes = []
        # starting cubes gaps info
        self.cube_sizes = {"cube_gap": 5}
        # starting the game table info
        self.game_table = {"width": 300, "heigth": 300}
        # starting methods
        self.set_up_games_settings()
        self.start_cubes_display_info()
    
    def set_up_games_settings(self) -> None:
        # Ajustin the table position info
        self.game_table["x_position"] = self.screen_size[0]/2 - self.game_table["width"]/2
        self.game_table["y_position"] = self.screen_size[1]/2 - self.game_table["heigth"]/2
        # Aujusting the cubes information
        self.cube_sizes["width"] = self.game_table["width"]/4 - self.cube_sizes["cube_gap"]*1.22
        self.cube_sizes["heigth"] = self.game_table["heigth"]/4 - self.cube_sizes["cube_gap"]*1.22
        self.cube_sizes["x_start"] = self.game_table["x_position"] + self.cube_sizes["cube_gap"]
        self.cube_sizes["y_start"] = self.game_table["y_position"] + self.cube_sizes["cube_gap"]

    # To start the table contents, and also add two values randonly to the cubes
    def start_cubes_display_info(self) -> None:
        x = self.cube_sizes["x_start"]
        y = self.cube_sizes["y_start"]
        starting_position = [(randint(0, 3), randint(0, 3)), (randint(0, 3), randint(0, 3))]
        # starting_position = [(0, 1), (0, 0), (0, 2), (0, 3)]
        # starting_position = [(1, 0), (0, 0), (2, 0), (3, 0)]
        for i in range(4):
            line = []
            for f in range(4):
                value = 0
                if((f, i) in starting_position):
                    value = 2
                cube_display_info = {
                    "x_position": x,
                    "y_position": y,
                    "width": self.cube_sizes["width"],
                    "heigth": self.cube_sizes["heigth"],
                    "value": value
                }
                line.append(Cube(self.screen, self.screen_size, cube_display_info))
                x += self.cube_sizes["cube_gap"] + self.cube_sizes["width"]
            x = self.cube_sizes["x_start"]
            self.game_cubes.append(line)
            y += self.cube_sizes["cube_gap"] + self.cube_sizes["heigth"]
    
    # To draw the table lines and also the cubes on the screen
    def draw_game_table_and_cubes(self) -> None:
        pygame.draw.rect(
            self.screen, 
            color.blue.value, 
            pygame.Rect(self.game_table["x_position"], 
            self.game_table["y_position"], self.game_table["width"],
            self.game_table["heigth"] ), 2
        )
        [line[i].draw() for line in self.game_cubes  for i in range(len(self.game_cubes[0]))]

    # To send the elements to the end on the direction setted if there is 0 on the way
    def send_elements_to_a_side(self, line_cube :list) -> list:
        for i in range(len(line_cube)):
            if line_cube[i] == 0:
                line_cube.pop(i)
                line_cube.insert(0, 0)
        return line_cube

    # This is to control is there is a conbination and multiplicate that conbination
    def pass_position_till_end(self, cube_lines) -> list:
        line_cubes_values = [cube.get_cube_value() for cube in cube_lines]
        i = 0
        for current_value in line_cubes_values:
            if current_value != 0:
                j = i
                for next_value in line_cubes_values[i+1:len(line_cubes_values)]:
                    if next_value == current_value:
                        line_cubes_values[j+1] = line_cubes_values[i] * 2
                        line_cubes_values[i] = 0                        
                    if next_value != 0:
                        break
                    j += 1
            i+=1
        line_cubes_values = self.send_elements_to_a_side(line_cubes_values)
        return line_cubes_values

    # To verify if there is more equals values on the 
    def verify_equals_cubes_values(self, cubes_values :list) -> bool:
        values_counter = [(value, cubes_values.count(value), index) for value, index in zip(cubes_values, range(len(cubes_values))) if value != 0]
        print(values_counter)
        # for times_repeated in values_counter:
        #     if times_repeated > 1:
        #         return True
        return False

    # To control the right move
    def moving_right(self):
        i = 0
        for cubes in self.game_cubes:
            line_cubes_values = self.pass_position_till_end(self.game_cubes[i])
            [cube.update_cube_value(new_value) for cube, new_value in zip(self.game_cubes[i], line_cubes_values)]
            i += 1

        # Verify if there more possible conbination
        for cubes in self.game_cubes:
            if self.verify_equals_cubes_values([cube.get_cube_value() for cube in cubes]):
                self.moving_right()
                break        
    
    # To control the left move and here is necessary to make list inversion
    def moving_left(self):        
        i = 0
        for cubes in self.game_cubes:
            line_cubes_values = self.pass_position_till_end(self.game_cubes[i][::-1])
            [cube.update_cube_value(new_value) for cube, new_value in zip(self.game_cubes[i], line_cubes_values[::-1])]
            i += 1

        # Verify if there more possible conbination
        for cubes in self.game_cubes:
            if self.verify_equals_cubes_values([cube.get_cube_value() for cube in cubes]):
                self.moving_left()
                break

    # To control the up move and here is necessary to make the matrix transpose and also list inversion
    def moving_up(self):
        there_is_more_changes = False
        self.game_cubes = np.transpose(self.game_cubes)
        i = 0
        for cubes in self.game_cubes:
            line_cubes_values = self.pass_position_till_end(self.game_cubes[i][::-1])
            [cube.update_cube_value(new_value) for cube, new_value in zip(self.game_cubes[i], line_cubes_values[::-1])]
            i += 1
        # Verify if there more possible conbination
        for cubes in self.game_cubes:
            if self.verify_equals_cubes_values([cube.get_cube_value() for cube in cubes]):
                there_is_more_changes = True
                break
        self.game_cubes = np.transpose(self.game_cubes)
        # Verify if there more possible conbination
        if there_is_more_changes:
            self.moving_up()

    # To control the up move and here is necessary to make the matrix transpose 
    def moving_down(self):
        there_is_more_changes = False
        self.game_cubes = np.transpose(self.game_cubes)
        i = 0
        for cubes in self.game_cubes:
            line_cubes_values = self.pass_position_till_end(self.game_cubes[i])
            [cube.update_cube_value(new_value) for cube, new_value in zip(self.game_cubes[i], line_cubes_values)]
            i += 1
        # Verify if there more possible conbination
        for cubes in self.game_cubes:
            if self.verify_equals_cubes_values([cube.get_cube_value() for cube in cubes]):
                there_is_more_changes = True
                break 
        # Verify if there more possible conbination
        self.game_cubes = np.transpose(self.game_cubes) 
        if there_is_more_changes:
            self.moving_down()  
    
    # TO generate a new cube value in a random position
    def generate_new_cube_value(self):
        available_positions = []
        i = 0
        for cubes in self.game_cubes:
            j = 0
            for cube in cubes:
                if cube.get_cube_value() == 0:
                    available_positions.append((i, j))
                j += 1
            i += 1

        random_position = choice(available_positions)
        print(random_position)
        self.game_cubes[random_position[0]][random_position[1]].update_cube_value(2)
    
    # To handle all the keyboard events
    def game_events_handler(self) -> None:
        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.moving_up()
                    self.generate_new_cube_value()
                elif pygame.key.get_pressed()[pygame.K_DOWN]:
                    self.moving_down()
                    self.generate_new_cube_value()
                elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                    self.moving_right()
                    self.generate_new_cube_value()
                elif pygame.key.get_pressed()[pygame.K_LEFT]:
                    self.moving_left()
                    self.generate_new_cube_value()

    # To run this page on the game
    def run_link(self, game_events :pygame.event) -> str:
        self.game_events = game_events
        self.pressed_keys = pygame.key.get_pressed()
        self.draw_game_table_and_cubes()
        self.game_events_handler()
        
        for event in game_events:
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    return "game_pause_menu"

        return "game_loop"
