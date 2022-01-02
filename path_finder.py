import pygame
import math
from queue import PriorityQueue

from pygame.mouse import get_pressed

WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))



#colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 164, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

pygame.display.set_caption("Path Finder")

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.width = width
        self.total_rows = total_rows
        #used for painting squares
        self.x = row * width
        self.y = col * width
        #init square to white
        self.color = WHITE
        #neighbours array is used to store nearby nodes
        self.neighbours = []
    
    def get_pos(self):
        #return tuple
        return self.row, self.col

    #getters

    def is_checked(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    #setters

    def set_closed(self):
        self.color = RED

    def set_open(self):
        self.color = GREEN
    
    def set_start(self):
        self.color = ORANGE

    def set_barrier(self):
        self.color = BLACK
    
    def set_end(self):
        self.color = PURPLE

    def set_path(self):
        self.color = TURQUOISE
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # down
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # up
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # left
            self.neighbours.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # right
            self.neighbours.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False

# point1, point 2 (row, col)
def h(p1, p2):
    # manhattan distance (L distance)
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def construct_path(origin, current, draw):
    while current in origin:
        current = origin[current]
        current.set_path()
        draw()

def astar_algorithm(draw, grid, start, end):
    count = 0
    #priority queue is an efficient way to find the smallest element - uses heap sort
    # https://www.geeksforgeeks.org/priority-queue-in-python/
    open_set = PriorityQueue()
    # add start node to PriorityQueue
    open_set.put((0, count, start))
    origin = {}
    g_score = {node: float("inf") for row in grid for node in row} #infinity
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row} #infinity
    f_score[start] = h(start.get_pos(), end.get_pos())

    #keeps track of items in priority queue
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit

        current = open_set.get()[2]
        open_set_hash.remove(current)

        #shortest path found
        if current == end:
            construct_path(origin, end, draw)
            end.set_end()
            start.set_start()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            #if more efficient path found
            if temp_g_score < g_score[neighbour]:
                origin[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())

                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.set_open()

        draw()

        if current != start:
            current.set_closed()     
    
    return False



def init_grid(rows, width):
    grid = []
    #integer division 
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
            
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        #draw horizantal lines
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))    
        for j in range(rows):
            #draw vertical lines
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))   

#redraws everything each frame (common practice in pygame)  
def draw(win, grid, rows, width):
    #paint over canvas
    win.fill(WHITE)

    #for each node
    for row in grid:
        for node in row:
            #draw the square
            node.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()    

#function to find which node has been clicked by mouse
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos

    row = x // gap
    col = y // gap

    return row, col


def main(win, width):
    ROWS = 100
    grid = init_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    #game loop
    while run:
        draw(win, grid, ROWS, width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
            #if left mouse button clicked
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos() #returns x,y coordinate of mouse
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.set_start()

                elif not end and node != start:
                    end = node
                    end.set_end()
                
                elif node != end and node != start:
                    node.set_barrier()


            
            #if right mouse button clicked
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos() #returns x,y coordinate of mouse
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    astar_algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end) # anon function
            
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = init_grid(ROWS, width)


    pygame.quit()
    print("Game ended...")

main (WINDOW, WIDTH)


