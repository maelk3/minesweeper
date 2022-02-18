#!/bin/env python3

import argparse
import random
import sys
import curses

# enum board cells states
NOTHING, BOMB = 0, -1
UNDISCOVERED, DISCOVERED, FLAG = -1, -2, -3

# flags and CLI arguments
WIDTH = None
HEIGHT = None

class Game:
    def __init__(self, width, height, x_offset, y_offset, nb_bombs):
        self.width = width
        self.height = height
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.nb_bombs = nb_bombs
        self.bomb_map = [[0 for j in range(width)] for i in range(height)]
        for k in range(self.nb_bombs):
            i, j = random.randrange(0, height), random.randrange(0, width)
            while(self.bomb_map[i][j] == BOMB):
                i, j = random.randrange(0, height), random.randrange(0, width)
            self.bomb_map[i][j] = BOMB

        self.board = [[-1 for j in range(width)] for i in range(height)]
        self.nb_flags = 0
        self.nb_correct_flags = 0

    def uncover_cell(self, mx, my, stdscr):
        queue = [(mx, my)]

        while len(queue) > 0:
            x, y = queue.pop()
            self.board[x][y] = DISCOVERED
            nb_neighboring_bombs = 0
            xmin = max(0, x-1)
            xmax = min(self.height-1, x+1)
            ymin = max(0, y-1)
            ymax = min(self.width-1, y+1)             
            for i in range(xmin, xmax+1):
                for j in range(ymin, ymax+1):
                    if self.bomb_map[i][j] == BOMB:
                        nb_neighboring_bombs += 1
            if nb_neighboring_bombs == 0:
                for i in range(xmin, xmax+1):
                    for j in range(ymin, ymax+1):
                        if self.board[i][j] != DISCOVERED and self.bomb_map[i][j] != BOMB:
                            queue.append((i, j))
            stdscr.addch(self.x_offset+x, self.y_offset+y, str(nb_neighboring_bombs) if nb_neighboring_bombs != 0 else " ", curses.color_pair(nb_neighboring_bombs+1))
        
    def toggle_flag(self, x, y, stdscr):
        if self.board[x][y] == UNDISCOVERED:
            self.board[x][y] = FLAG
            self.nb_flags += 1
            if self.bomb_map[x][y] == BOMB:
                self.nb_correct_flags += 1
            stdscr.addch(self.x_offset+x, self.y_offset+y,'F', curses.color_pair(11) | curses.A_REVERSE)
        elif self.board[x][y] == FLAG:
            self.board[x][y] = UNDISCOVERED
            self.nb_flags -= 1
            if self.bomb_map[x][y] == BOMB:
                self.nb_correct_flags -= 1
            stdscr.addch(self.x_offset+x, self.y_offset+y, ' ', curses.color_pair(12) | curses.A_REVERSE)

    def win(self):
        return self.nb_flags == self.nb_bombs and self.nb_correct_flags == self.nb_bombs

    def win_screen(self, stdscr):
        stdscr.addstr(self.x_offset+self.height//2, self.y_offset+self.width//2-5, "You won!", curses.color_pair(2))
        stdscr.refresh()
        
    def game_over_screen(self, x, y, stdscr):
        stdscr.clear()
        stdscr.addstr(self.x_offset+self.height//2, self.y_offset+self.width//2-5, "Game over!", curses.color_pair(11))
        stdscr.refresh()

    def run_game_loop(self, stdscr):

        curses.mousemask(curses.ALL_MOUSE_EVENTS)

        for i in range(self.height):
            stdscr.addstr(self.x_offset+i, self.y_offset," "*self.width, curses.A_REVERSE | curses.color_pair(12))
        stdscr.refresh()

        mx, my = HEIGHT//2, WIDTH//2
        stdscr.move(self.x_offset+mx, self.y_offset+my)

        while True:
            event = stdscr.getch()
            if (event == curses.KEY_ENTER or event == 10 or event == 13 or event == 103) and self.board[mx][my] == UNDISCOVERED:
                if self.bomb_map[mx][my] != BOMB:
                    self.uncover_cell(mx, my, stdscr)
                    stdscr.move(self.x_offset+mx, self.y_offset+my)
                    stdscr.refresh()
                else:
                    self.game_over_screen(mx, my, stdscr)
                    stdscr.getch()
                    return
            elif event == 102 and self.board[mx][my] != DISCOVERED:
                self.toggle_flag(mx, my, stdscr)
                stdscr.move(self.x_offset+mx, self.y_offset+my)
                stdscr.refresh()                        
                if self.win():
                    self.win_screen(stdscr)
                    stdscr.getch()
                    return
            elif event == curses.KEY_LEFT or event == 113:
                my = max(0, my-1)
                stdscr.move(self.x_offset+mx, self.y_offset+my)
            elif event == curses.KEY_RIGHT or event == 100:
                my = min(my+1, WIDTH-1)
                stdscr.move(self.x_offset+mx, self.y_offset+my)
            elif event == curses.KEY_UP or event == 122:
                mx = max(0, mx-1)
                stdscr.move(self.x_offset+mx, self.y_offset+my)
            elif event == curses.KEY_DOWN or event == 115:
                mx = min(mx+1, HEIGHT-1)
                stdscr.move(self.x_offset+mx, self.y_offset+my)
            elif event == curses.KEY_MOUSE:
                _, cy, cx, _, code = curses.getmouse()
                mx = cx - self.x_offset
                my = cy - self.y_offset

                if mx<self.height and my<self.width:
                    if curses.BUTTON1_CLICKED & code != 0 and self.board[mx][my] == UNDISCOVERED:
                        if self.bomb_map[mx][my] != BOMB:
                            self.uncover_cell(mx, my, stdscr)
                            stdscr.move(self.x_offset+mx, self.y_offset+my)
                            stdscr.refresh()
                        else:
                            self.game_over_screen(mx, my, stdscr)
                            stdscr.getch()
                            return
                        
                    elif curses.BUTTON3_CLICKED & code != 0 and self.board[mx][my] != DISCOVERED:
                        self.toggle_flag(mx, my, stdscr)
                        stdscr.move(self.x_offset+mx, self.y_offset+my)                        
                        stdscr.refresh()                        
                        if self.win():
                            self.win_screen(stdscr)
                            stdscr.getch()
                            return
                                        
def main(stdscr):
    
    # screen setup
    stdscr.clear()

    global WIDTH, HEIGHT
    WIDTH = WIDTH if WIDTH != None else curses.COLS-2
    HEIGHT = HEIGHT if HEIGHT != None else curses.LINES-2
    X_OFFSET = ((curses.LINES)-HEIGHT)//2
    Y_OFFSET = ((curses.COLS)-WIDTH)//2

    colors = [curses.COLOR_WHITE,   # 0
              curses.COLOR_BLUE,    # 1
              curses.COLOR_CYAN,    # 2
              curses.COLOR_GREEN,   # 3
              curses.COLOR_MAGENTA, # 4
              curses.COLOR_RED,     # 5
              curses.COLOR_YELLOW,  # 6
              curses.COLOR_YELLOW,  # 7
              curses.COLOR_YELLOW,  # 8
              curses.COLOR_YELLOW,  # 9
              curses.COLOR_RED,     # flag
              curses.COLOR_MAGENTA] # undiscovered cell
    for i in range(len(colors)):
        curses.init_pair(i+1, colors[i], curses.COLOR_BLACK)
    
    # game constants
    NB_BOMBS = int(0.11*HEIGHT*WIDTH)
    
    # create game instance
    game = Game(WIDTH, HEIGHT, X_OFFSET, Y_OFFSET, NB_BOMBS)
    game.run_game_loop(stdscr)   

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-l", "--lines", help="specify a height", type=int)
        parser.add_argument("-c", "--cols", help="specify a width", type=int)
        args = parser.parse_args()

        HEIGHT = args.lines
        WIDTH = args.cols
        
        curses.wrapper(main)
    except KeyboardInterrupt:
        print('game interrupted!')
        sys.exit(0)
