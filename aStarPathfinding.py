import pygame
import math
from queue import PriorityQueue

# window
WIDTH = 800
WINDOW = pygame.display.set_mode((WIDTH, WIDTH))

# colors
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)
purple = (128, 0, 128)
orange = (255, 128, 128)
grey = (128, 128, 128)
turquoise = (0, 255, 255)

# nodes for cubes / boxes on grid
class cube:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.width = width
		self.total_rows = total_rows
		self.x = row * width
		self.y = col * width
		self.color = white

	def getPosition(self):
		return self.row, self.col

	def isClose(self):
		return self.color == turquoise

	def isOpen(self):
		return self.color == orange

	def isObstacle(self):
		return self.color == black

	def isStart(self):
		return self.color == blue

	def isEnd(self):
		return self.color == red

	def reset(self):
		self.color = white

	def makeClosed(self):
		self.color = turquoise

	def makeStart(self):
		self.color = blue

	def makeOpen(self):
		self.color = orange

	def makeObstacle(self):
		self.color = black

	def makeEnd(self):
		self.color = red

	def makePath(self):
		self.color = purple

	def draw(self, window):
		pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []

		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isObstacle(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].isObstacle(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isObstacle(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.row > 0 and not grid[self.row][self.col - 1].isObstacle(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

# functions
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2

	return abs(x1 - x2) + abs(y1 - y2)

def reconstructPath(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.makePath()
		draw()

def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {cube: float("inf") for row in grid for cube in row}
	g_score[start] = 0
	f_score = {cube: float("inf") for row in grid for cube in row}
	f_score[start] = h(start.getPosition(), end.getPosition())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstructPath(came_from, end, draw)
			end.makeEnd()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.getPosition(), end.getPosition())

				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.makeOpen()

		draw()

		if current != start:
			current.makeClosed()

	return False

def createGrid(rows, width):
	grid = []
	gap = width // rows

	for i in range(rows):
		grid.append([])

		for j in range(rows):
			Cube = cube(i, j, gap, rows)
			grid[i].append(Cube)

	return grid

def drawGrid(window, rows, width):
	gap = width // rows

	for i in range(rows):
		pygame.draw.line(window, grey, (0, i * gap), (width, i * gap))

		for j in range(rows):
			pygame.draw.line(window, grey, (j * gap, 0), (j * gap, width))

def draw(window, grid, rows, width):
	window.fill(white)

	for row in grid:
		for cube in row:
			#cube = cube(window)
			cube.draw(window)

	drawGrid(window, rows, width)
	pygame.display.update()

def getClickedPosition(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col

def main(window, width):
	ROWS = 50
	grid = createGrid(ROWS, width)

	start = None
	end = None

	run = True 
	started = False

	while run:
		draw(window, grid, ROWS, width)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if started:
				continue

			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()
				row, col = getClickedPosition(pos, ROWS, width)
				cube = grid[row][col]

				if not start and cube != end:
					start = cube
					start.makeStart()

				elif not end and cube != start:
					end = cube
					end.makeEnd()

				elif cube != end and cube != start:
					cube.makeObstacle()

			elif pygame.mouse.get_pressed()[2]:
				pos = pygame.mouse.get_pos()
				row, col = getClickedPosition(pos, ROWS, width)
				cube = grid[row][col]
				cube.reset()

				if cube == start:
					start = None

				if cube == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and not started:
					for row in grid:
						for cube in row:
							cube.update_neighbors(grid)

					algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)

	pygame.quit()

main(WINDOW, WIDTH)