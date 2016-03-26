#!/usr/bin/env python

# Copyright 2016 - Scott Moreau <oreaus@gmail.com>

import math
import pygame
import collections

LEFT = 1
SCROLL_UP = 4
SCROLL_DOWN = 5

point = collections.namedtuple("point", "x y")
line = collections.namedtuple("line", "a b")

width = 1000
height = 600
line1 = None
line2 = None
intersect = None
line1_drawn = False
bgcolor = 255, 255, 255
running = 1
button_down = False
draw_coords = False
display_help = True
draw_crosshair = False

pygame.init()
font = pygame.font.SysFont("arial", 14)
pygame.font.Font.set_bold(font, True)
screen = pygame.display.set_mode((width, height))
last_time = pygame.time.get_ticks()

def draw_coordinates(color, pt):
	tmp_font = pygame.font.SysFont("arial", 12)
	pygame.font.Font.set_bold(tmp_font, True)
	label = tmp_font.render("%d, %d" % (pt[0], pt[1]), 1, (0, 0, 0))
	screen.blit(label, (pt[0] - 24, pt[1] - 19))
	label = tmp_font.render("%d, %d" % (pt[0], pt[1]), 1, color)
	screen.blit(label, (pt[0] - 25, pt[1] - 20))

def draw_point(color, pt):
	pygame.draw.ellipse(screen, color, [pt[0] - 2, pt[1] - 2, 4, 4])
	if (draw_coords):
		draw_coordinates(color, pt)

def draw_line(color, pt_1, pt_2):
	pygame.draw.line(screen, color, (pt_1[0], pt_1[1]), (pt_2[0], pt_2[1]))

def compute_intersection(A, B):
	if (A is None or B is None):
		return None

	if (A.a.x == A.b.x and A.a.y == A.b.y or B.a.x == B.b.x and B.a.y == B.b.y):
		return None

	# Fail if the segments share an end-point.
	if (A.a.x == B.a.x and A.a.y == B.a.y or A.b.x == B.a.x and A.b.y == B.a.y
	or  A.a.x == B.b.x and A.a.y == B.b.y or A.b.x == B.b.x and A.b.y == B.b.y):
		return None

	# (1) Translate the system so that point A is on the origin.
	A = line(a = point(A.a.x, A.a.y), b = point(x = A.b.x - A.a.x, y = A.b.y - A.a.y))
	B = line(a = point(x = B.a.x - A.a.x, y = B.a.y - A.a.y), b = point(x = B.b.x - A.a.x, y = B.b.y - A.a.y))

	# Discover the length of segment A-B.
	distAB = math.sqrt(A.b.x * A.b.x + A.b.y * A.b.y)

	# (2) Rotate the system so that point B is on the positive X axis.
	theCos = A.b.x / distAB
	theSin = A.b.y / distAB
	newX = B.a.x * theCos + B.a.y * theSin
	B = line(a = point(x = newX, y = B.a.y * theCos - B.a.x * theSin), b = point(x = B.b.x, y = B.b.y))
	newX = B.b.x * theCos + B.b.y * theSin
	B = line(a = point(x = B.a.x, y = B.a.y), b = point(x = newX, y = B.b.y * theCos - B.b.x * theSin))

	# Fail if segment B.a-B.b doesn't cross line A.a-A.b.
	if (B.a.y < 0 and B.b.y < 0 or B.a.y >= 0 and B.b.y >= 0):
		return None

	# (3) Discover the position of the intersection point along line A-B.
	ABpos = B.b.x + (B.a.x - B.b.x) * B.b.y / (B.b.y - B.a.y)

	# Fail if segment C-D crosses line A-B outside of segment A-B.
	if (ABpos < 0 or ABpos > distAB):
		return None

	# (4) Apply the discovered position to line A-B in the original coordinate system.
	intersection = point(x = A.a.x + ABpos * theCos, y = A.a.y + ABpos * theSin)

	return intersection

while running:
	current_time = pygame.time.get_ticks()
	elapsed_time = current_time - last_time
	last_time = current_time

	event = pygame.event.poll()
	if event.type == pygame.QUIT:
		running = 0
		continue
	elif event.type == pygame.MOUSEMOTION:
		current_pos = point(x = event.pos[0], y = event.pos[1])
		if (button_down):
			if (line1 and line2):
				intersect = compute_intersection(line1, line2)
			if (line1_drawn):
				line2 = line(a = line2.a, b = point(event.pos[0], event.pos[1]))
			else:
				line1 = line(a = line1.a, b = point(event.pos[0], event.pos[1]))
	elif event.type == pygame.MOUSEBUTTONDOWN:
		if event.button == LEFT:
			button_down = True
			if (line2 is not None):
				intersect = line1 = line2 = None
				line1_drawn = False
			if (line1_drawn):
				line2 = line(a = point(event.pos[0], event.pos[1]), b = point(event.pos[0], event.pos[1]))
			else:
				line1 = line(a = point(event.pos[0], event.pos[1]), b = point(event.pos[0], event.pos[1]))
	elif event.type == pygame.MOUSEBUTTONUP:
		if event.button == LEFT:
			button_down = False
			if (line1 and not line2):
				line1_drawn = True
			elif (line1 and line2):
				intersect = compute_intersection(line1, line2)
	elif event.type == pygame.KEYDOWN:
		name = pygame.key.name(event.key)
		if (name == "q" or name == "Q" or name == "escape"):
			running = 0
			continue
		elif (name == "h" or name == "H"):
			display_help = not display_help
		elif (name == "c" or name == "C"):
			draw_crosshair = not draw_crosshair
		elif (name == "n" or name == "N"):
			draw_coords = not draw_coords

	screen.fill(bgcolor)

	if (line1 is not None):
		draw_line((0, 255, 0), line1.a, line1.b)
		draw_point((0, 0, 255), line1.a)
		draw_point((0, 0, 255), line1.b)
	if (line2 is not None):
		draw_line((0, 255, 0), line2.a, line2.b)
		draw_point((0, 0, 255), line2.a)
		draw_point((0, 0, 255), line2.b)
	if (intersect is not None):
		draw_point((255, 0, 0), intersect)

	if (draw_crosshair and current_pos is not None):
		draw_line((0, 255, 0), (0, current_pos.y), (width - 1, current_pos.y))
		draw_line((0, 255, 0), (current_pos.x, 0), (current_pos.x, height - 1))

	if (display_help):
		label = font.render("-", 1, (0,0,0))
		screen.blit(label, (130, 50))
		screen.blit(label, (130, 70))
		screen.blit(label, (130, 90))
		screen.blit(label, (130, 110))
		screen.blit(label, (130, 130))
		label = font.render("Circle and line segment intersection demo", 1, (0,0,0))
		screen.blit(label, (25, 20))
		label = font.render("'q' or esc", 1, (0,0,0))
		screen.blit(label, (25, 50))
		label = font.render("quit", 1, (0,255,0))
		screen.blit(label, (150, 50))
		label = font.render("'h'", 1, (0,0,0))
		screen.blit(label, (25, 70))
		label = font.render("toggle help", 1, (0,255,0))
		screen.blit(label, (150, 70))
		label = font.render("'c'", 1, (0,0,0))
		screen.blit(label, (25, 90))
		label = font.render("toggle crosshairs", 1, (0,255,0))
		screen.blit(label, (150, 90))
		label = font.render("'n'", 1, (0,0,0))
		screen.blit(label, (25, 110))
		label = font.render("toggle coordinate values", 1, (0,255,0))
		screen.blit(label, (150, 110))
		label = font.render("mouse drag", 1, (0,0,0))
		screen.blit(label, (25, 130))
		label = font.render("draw line segments", 1, (0,255,0))
		screen.blit(label, (150, 130))
	pygame.display.flip()
