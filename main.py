from socket import has_dualstack_ipv6
import time
from asyncio.windows_events import NULL
import tkinter as tk
import tkinter.font
from traceback import print_tb
from typing_extensions import IntVar, runtime
from PIL import ImageTk, Image
import numpy as np
import pygame
import os
import sys
from knight_tour import KnightTour
import csv

class Application(tk.Frame):

    def __init__(self, master=None):
        # create window frame
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.protocol('WM_DELETE_WINDOW', self.close)
        self.master.title('A Knights Tour')
        self.display_width = 800
        self.display_height  = 800
        self.board_size_x = 6
        self.board_size_y = 6
        self.pack()
        self.create_widgets()

        # fills game_display with black, these will be the black tiles
    def draw_background(self):
        self.game_display.fill(self.blackTileColour)
        if self.display_width // self.board_size_y >= self.display_height  // self.board_size_x:
            self.tileSize = self.display_height  // self.board_size_x
        else:
            self.tileSize = self.display_width // self.board_size_y
        # iterate through tile positions
        for i in range(self.board_size_x):
            for j in range(self.board_size_y):
                # draws in the white tiles, entire screen is filled in with the black tile colour, leaving us with the appearance of black and white tiles
                if (i + j) % 2 == 0:
                    pygame.draw.rect(self.game_display, self.whiteTileColour, (self.tileSize * j, self.tileSize * i, self.tileSize, self.tileSize), 0)
                # draw knights as a circle
                pygame.draw.circle(self.game_display, self.knightTileColour,(self.tileSize * j + self.tileSize / 2, self.tileSize * i + self.tileSize / 2), self.tileSize / 8, 0)

    def draw_line(self, start, end):
        # draws a line from each move in the game, indicating the path of the knights tour
        pygame.draw.line(self.game_display, self.lineColour,
                        (self.tileSize * start[1] + self.tileSize / 2, self.tileSize * start[0] + self.tileSize / 2),
                        (self.tileSize * end[1] + self.tileSize / 2, self.tileSize * end[0] + self.tileSize / 2), 4)

    

    def close(self):
        pygame.quit()
        self.master.destroy()
        sys.exit()

    def change_game(self):
        self.board_size_x = self.x_dimension.get()
        self.board_size_y = self.y_dimension.get()


    def create_widgets(self):
        std_font = tkinter.font.Font(family= 'Helvetica', size = 12)
        head_font = tkinter.font.Font(family= 'Helvetica', size = 16, weight="bold")
        ## Widgets
        
        #embed pygame window
        

        self.whiteTileColour      = (238, 238, 238)
        self.blackTileColour      = (106, 106, 106)
        self.visitedTileColour    = (110, 55, 55)
        self.knightTileColour     = (37, 89, 147)
        self.lineColour           = (51, 120, 199)


        if self.display_width // self.board_size_x >= self.display_height  // self.board_size_y:
            self.tileSize = self.display_height  // self.board_size_x
        else:
            self.tileSize = self.display_width // self.board_size_y
        
        game_frame = tk.Frame(self.master)
        embed = tk.Frame(game_frame, width = self.display_width, height = self.display_height)
        embed.pack(side='right')
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        self.game_display = pygame.display.set_mode((self.tileSize * self.board_size_y, self.tileSize * self.board_size_x))
        
        self.clock = pygame.time.Clock()
        self.crashed = False
        self.fps = 60
        self.draw_background()

        self.skip = True
        self.runUpdate = True
        self.even = False

        pygame.init()
        embed.pack()
        widgets = tk.Frame(self.master)
        buttons = tk.Frame(self.master)

        self.x_dimension = tk.IntVar()
        self.y_dimension = tk.IntVar()
        self.x_dimension.set(6)
        self.y_dimension.set(6)
        tk.Label(widgets, text='Board X Dimension', font=std_font).pack()
        tk.Spinbox(
                widgets,
                textvariable=self.x_dimension,
                from_=6,
                to=12,
                font=('sans-serif', 18),
                ).pack(pady=20)
        tk.Label(widgets, text='Board Y Dimension', font=std_font).pack()
        tk.Spinbox(
                widgets,
                textvariable=self.y_dimension,
                from_=6,
                to=12,
                font=('sans-serif', 18),
                ).pack(pady=20)

        widgets.pack(padx=15, pady=15)
        
        start_button = tk.Button(buttons, text='Start Tour', font=std_font, command=lambda : start_tour(), height=1,width=8 )
        start_button.pack(side='top', pady=15)

        # Close
        exit_button = tk.Button(buttons, text='Exit', font=std_font, command = self.close, height=1,width=8 )
        exit_button.pack(side='top', pady=15)

        buttons.pack(side='top', fill='x', pady=15)

        
        


def start_tour():
    global startTour
    global runUpdate
    global tourStarted
    global tourCompleted
    tourStarted = False
    startTour = True
    runUpdate = True
    tourCompleted = False
    



# logging of times
header = ['m','n','time to complete ms']


root = tk.Tk()
app = Application(master=root)
runUpdate = False
startTour = False
tourStarted = False
tourCompleted = False
even = False
start = 0
runTime = 0
previousTime = 0
knight_tour = KnightTour

while True:
    iterations = 0
    if (tourStarted and runUpdate): knight_tour.initialise_neurons()
    while True:
        if start == 0: start = time.perf_counter_ns()
        elapsed = time.perf_counter_ns() - start
        start = time.perf_counter_ns()
        runTime += elapsed
        if (runTime - previousTime) > 1000*1000*1000 and tourCompleted == False: 
            print("Run Time:",round((runTime/1000/1000), 3),"ms")
            previousTime = runTime
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                csvfile.close()
                app.close()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if runUpdate:
                            runUpdate = False
                        else:
                            runUpdate = True
                    if event.key == pygame.K_q:
                        app.fps += 1
                    if event.key == pygame.K_a:
                        app.fps -= 1
                        if app.fps == 0:
                            app.fps = 1
                    if event.key == pygame.K_UP:
                        app.board_size_x += 1
                    if event.key == pygame.K_DOWN:
                        app.board_size_x -= 1
                    if event.key == pygame.K_RIGHT:
                        app.board_size_y += 1
                    if event.key == pygame.K_LEFT:
                        app.board_size_y -= 1
        if startTour == True and tourStarted == False:
            print("starting tour")
            runTime = 0
            previousTime = 0
            knight_tour = KnightTour(board_size=(app.board_size_x, app.board_size_y))
            knight_tour.initialise_neurons()
            tourStarted = True
        if runUpdate:
            num_of_active, num_of_changes = knight_tour.update_neurons()
            app.draw_background()
            app.update()
            for vertex_set in knight_tour.get_active_neurons_vertices():
                    vertex1, vertex2 = vertex_set
                    app.draw_line(vertex1, vertex2)
            if num_of_changes == 0:
                    break
            if knight_tour.check_degree():
                even = True
                break
            iterations += 1
            if iterations == 20:
                break 
        if  runUpdate == False: 
            app.change_game()
            #if (tourCompleted == False ): app.draw_background()  
            app.update()
            pygame.display.update()
    if even:
        print('all vertices have degree=2')
        if knight_tour.check_connected_components():
            elapsed = time.perf_counter_ns() - start
            start = time.perf_counter_ns()
            runTime += elapsed
            print('solution found in',round((runTime/1000/1000), 3),"ms")
            print(knight_tour.get_solution())
            logData = [app.x_dimension.get(), app.y_dimension.get(),(runTime/1000/1000)]
            #logData = ('{},{},{}'.format(app.x_dimension.get(), app.y_dimension.get(),(runTime/1000/1000)))
            with open('knights_tour_log.csv', 'a', encoding='UTF8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(logData)
            runUpdate = False
            startTour = False
            tourStarted = False
            tourCompleted = True
        else:
            even = False
            app.update()
    app.update()
    pygame.display.set_caption("Knight\'s Tour " + str(app.fps) + "fps")
    app.update()
    pygame.display.update()
    #msElapsed = clock.tick(fps)
