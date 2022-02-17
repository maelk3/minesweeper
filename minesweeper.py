#!/bin/env python3

import random
import sys
import curses

# enum board cells states
NOTHING, BOMB = 0, -1
UNDISCOVERED, DISCOVERED, FLAG = -1, -2, -3

class Game:
    def __init__(self, width, height, nb_bombs):
        self.width = width
        self.height = height
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
            stdscr.addch(x, y, str(nb_neighboring_bombs) if nb_neighboring_bombs != 0 else " ", curses.color_pair(nb_neighboring_bombs+1))
        
    def toggle_flag(self, x, y, stdscr):
        if self.board[x][y] == UNDISCOVERED:
            self.board[x][y] = FLAG
            self.nb_flags += 1
            if self.bomb_map[x][y] == BOMB:
                self.nb_correct_flags += 1
            stdscr.addch(x, y,'^', curses.color_pair(11))
        elif self.board[x][y] == FLAG:
            self.board[x][y] = UNDISCOVERED
            self.nb_flags -= 1
            if self.bomb_map[x][y] == BOMB:
                self.nb_correct_flags -= 1
            stdscr.addch(x, y, ' ', curses.color_pair(1) | curses.A_REVERSE)

    def win(self):
        return self.nb_flags == self.nb_bombs and self.nb_correct_flags == self.nb_bombs

    def win_screen(self, stdscr):
        stdscr.clear()
        stdscr.addstr(curses.LINES//2, curses.COLS//2-5, "You won!", curses.color_pair(2))
        stdscr.refresh()
        
    def game_over_screen(self, x, y, stdscr):
        stdscr.clear()
        stdscr.addstr(curses.LINES//2, curses.COLS//2-5, "Game over!", curses.color_pair(11))
        stdscr.refresh()
        
    def run_game_loop(self, stdscr):

        stdscr.addstr((" "*self.width+"\n")*self.height, curses.A_REVERSE)
        stdscr.refresh()

        while True:
            event = stdscr.getch()
            if event == curses.KEY_MOUSE:
                _, my, mx, _, code = curses.getmouse()

                if mx<self.height and my<self.width:
                    if curses.BUTTON1_CLICKED & code != 0 and self.board[mx][my] == UNDISCOVERED:
                        if self.bomb_map[mx][my] != BOMB:
                            self.uncover_cell(mx, my, stdscr)
                            stdscr.refresh()
                        else:
                            self.game_over_screen(mx, my, stdscr)
                            stdscr.getch()
                            return
                        
                    elif curses.BUTTON3_CLICKED & code != 0 and self.board[mx][my] != DISCOVERED:
                        self.toggle_flag(mx, my, stdscr)
                        stdscr.refresh()                        
                        if self.win():
                            self.win_screen(stdscr)
                            stdscr.getch()
                            return

def main(stdscr):
    # screen setup
    stdscr.clear()
    curses.curs_set(False)
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

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
              curses.COLOR_RED]     # flag
    for i in range(len(colors)):
        curses.init_pair(i+1, colors[i], curses.COLOR_BLACK)
    
    # game constants
    WIDTH = curses.COLS-1
    HEIGHT = curses.LINES-1
    NB_BOMBS = int(0.11*HEIGHT*WIDTH)

    # create game instance
    game = Game(WIDTH, HEIGHT, NB_BOMBS)

    game.run_game_loop(stdscr)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print('game interrupted!')
        sys.exit(0)
