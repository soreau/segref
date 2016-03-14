#!/usr/bin/env python

# Copyright 2016 - Scott Moreau <oreaus@gmail.com>

import math
import pygame
import collections

LEFT = 1
SCROLL_UP = 4
SCROLL_DOWN = 5

point = collections.namedtuple("point", "x y")

width = 1000
height = 600
ball_radius = 75
ball_progression = 0.0
bgcolor = 255, 255, 255
corner_pos = point(x = width * 0.5, y = height * 0.5)
running = 1
playing = False
draw_rect = False
draw_extra = True
button_down = False
draw_coords = False
display_help = True
draw_crosshair = False
circle_grabbed = False
reflect = None
new_pos = None
contact = None
last_pos = None
current_pos = None
reflect_plane_1 = None
reflect_plane_2 = None
last_to_corner_vec = None

pygame.init()
font = pygame.font.SysFont("arial", 14)
pygame.font.Font.set_bold(font, True)
screen = pygame.display.set_mode((width, height))
last_time = pygame.time.get_ticks()

def draw_point(color, pt):
	pygame.draw.ellipse(screen, color, [pt[0] - 2, pt[1] - 2, 4, 4])
	if (draw_coords):
		tmp_font = pygame.font.SysFont("arial", 12)
		pygame.font.Font.set_bold(tmp_font, True)
		label = tmp_font.render("%d, %d" % (pt[0], pt[1]), 1, (0, 0, 0))
		screen.blit(label, (pt[0] - 24, pt[1] - 19))
		label = tmp_font.render("%d, %d" % (pt[0], pt[1]), 1, color)
		screen.blit(label, (pt[0] - 25, pt[1] - 20))
		

def draw_line(color, pt_1, pt_2):
	pygame.draw.line(screen, color, (pt_1[0], pt_1[1]), (pt_2[0], pt_2[1]))

def compute_intersection(center, radius, last, new):
	if (last is None or new is None):
		return None, None, None, None
	d = point(x = new.x - last.x, y = new.y - last.y)

	A = d.x * d.x + d.y * d.y
	B = 2 * (d.x * (last.x - center.x) + d.y * (last.y - center.y))
	C = math.pow(last.x - center.x, 2) + math.pow(last.y - center.y, 2) - radius * radius

	det = B * B - 4 * A * C

	if ((A <= 0.0000001) or (det < 0)):
		# Miss
		return None, None, None, None

	discriminant = math.sqrt(det);

	t = (-B - discriminant) / (2 * A)

	if (t < 0 or t > 1):
		# Miss
		return None, None, None, None

	if (det == 0):
		# Tangent
		hit = point(x = last.x + t * d.x, y = last.y + t * d.y)
	else:
		# Hit
		t = (-B + math.sqrt(det)) / (2 * A)
		i_1 = point(last.x + t * d.x, last.y + t * d.y)
		t = (-B - math.sqrt(det)) / (2 * A)
		i_2 = point(last.x + t * d.x, last.y + t * d.y)
		len_1 = (math.pow(i_1.x - last.x, 2) + math.pow(i_1.y - last.y, 2))
		len_2 = (math.pow(i_2.x - last.x, 2) + math.pow(i_2.y - last.y, 2))
		if (len_1 < len_2):
			hit = i_1
		else:
			hit = i_2
	# Compute reflected position
	hit_vec = point(x = hit.x - center.x, y = hit.y - center.y)
	rp_1 = point(x = -hit_vec.y * 0.5 + center.x + hit_vec.x, y = hit_vec.x * 0.5 + center.y + hit_vec.y)
	rp_2 = point(x = hit_vec.y * 0.5 + center.x + hit_vec.x, y = -hit_vec.x * 0.5 + center.y + hit_vec.y)
	hit_vec_len = math.sqrt(hit_vec.x * hit_vec.x + hit_vec.y * hit_vec.y)
	hit_vec_unit = point(x = hit_vec.x / hit_vec_len, y = hit_vec.y / hit_vec_len)
	vec_len = math.sqrt(A)
	vec_unit = point(x = d.x / vec_len, y = d.y / vec_len)
	dot = hit_vec_unit.x * vec_unit.x + hit_vec_unit.y * vec_unit.y
	reflect_vec = point(x = vec_unit.x - 2 * dot * hit_vec_unit.x, y = vec_unit.y - 2 * dot * hit_vec_unit.y)
	reflect_len = vec_len - math.sqrt((hit.x - last.x) * (hit.x - last.x) + (hit.y - last.y) * (hit.y - last.y))
	reflect_pos = point(x = hit.x + reflect_vec.x * reflect_len, y = hit.y + reflect_vec.y * reflect_len)
	return hit, rp_1, rp_2, reflect_pos

while running:
	current_time = pygame.time.get_ticks()
	elapsed_time = current_time - last_time
	last_time = current_time

	event = pygame.event.poll()
	if event.type == pygame.QUIT:
		running = 0
		continue
	elif event.type == pygame.MOUSEMOTION:
		if (circle_grabbed):
			corner_pos = point(x = event.pos[0] - last_to_corner_vec.x, y = event.pos[1] - last_to_corner_vec.y)
		else:
			current_pos = point(x = event.pos[0], y = event.pos[1])
		if (button_down):
			contact, reflect_plane_1, reflect_plane_2, reflect = compute_intersection(corner_pos, ball_radius, last_pos, current_pos)
	elif event.type == pygame.MOUSEBUTTONDOWN:
		if event.button == LEFT:
			button_down = True
			last_to_corner_vec = point(x = event.pos[0] - corner_pos.x, y = event.pos[1] - corner_pos.y)
			last_to_corner_len = math.sqrt(math.pow(last_to_corner_vec.x, 2) + math.pow(last_to_corner_vec.y, 2))
			if (last_to_corner_len < ball_radius):
				corner_pos = point(x = event.pos[0] - last_to_corner_vec.x, y = event.pos[1] - last_to_corner_vec.y)
				current_pos = new_pos
				circle_grabbed = True
			else:
				last_pos = point(x = event.pos[0], y = event.pos[1])
				contact = None
		elif event.button == SCROLL_UP:
			ball_radius = ball_radius + 1
		elif event.button == SCROLL_DOWN:
			ball_radius = ball_radius - 1
			if ball_radius < 2:
				ball_radius = 2
	elif event.type == pygame.MOUSEBUTTONUP:
		if event.button == LEFT:
			if (not circle_grabbed):
				new_pos = point(x = event.pos[0], y = event.pos[1])
			circle_grabbed = False
			button_down = False
		contact, reflect_plane_1, reflect_plane_2, reflect = compute_intersection(corner_pos, ball_radius, last_pos, new_pos)
	elif event.type == pygame.KEYDOWN:
		name = pygame.key.name(event.key)
		if (name == "q" or name == "Q" or name == "escape"):
			running = 0
			continue
		elif (name == "h" or name == "H"):
			display_help = not display_help
		elif (name == "c" or name == "C"):
			draw_crosshair = not draw_crosshair
		elif (name == "p" or name == "P"):
			ball_progression = 0.0
			playing = not playing
		elif (name == "r" or name == "R"):
			draw_rect = not draw_rect
		elif (name == "d" or name == "D"):
			draw_extra = not draw_extra
		elif (name == "n" or name == "N"):
			draw_coords = not draw_coords

	screen.fill(bgcolor)
	# Circle fill
	pygame.draw.ellipse(screen, (255, 255, 200), [corner_pos.x - ball_radius, corner_pos.y - ball_radius, ball_radius * 2, ball_radius * 2])
	if (draw_extra):
		# Circle outline
		pygame.draw.ellipse(screen, (0, 0, 0), [corner_pos.x - ball_radius, corner_pos.y - ball_radius, ball_radius * 2, ball_radius * 2], 1)
		if (contact is not None):
			# Incoming vector
			draw_line((0, 255, 0), last_pos, contact)
			# Reflect normal
			draw_line((255, 0, 0), corner_pos, contact)
			if (reflect is not None):
				# Inverse reflected vector
				if (button_down):
					draw_line((200, 200, 200), contact, current_pos)
				else:
					draw_line((150, 150, 255), new_pos, contact)
				# Reflected vector
				draw_line((0, 255, 0), contact, reflect)
				draw_point((0, 0, 255), reflect)
			if (reflect_plane_1 is not None and reflect_plane_2 is not None):
				# Reflect plane
				draw_line((255, 100, 0), reflect_plane_1, reflect_plane_2)
			# Point of contact
			draw_point((255, 0, 0), contact)
		elif (new_pos is not None and last_pos is not None and not button_down):
			# Line segment with no intersection
			draw_line((0, 255, 0), last_pos, new_pos)
			draw_point((0, 0, 255), last_pos)
			draw_point((0, 0, 255), new_pos)
		else:
			if (current_pos is not None):
				if (button_down and last_pos is not None):
					draw_line((0, 255, 0), last_pos, current_pos)
				draw_point((0, 0, 255), current_pos)
		if (last_pos is not None):
			draw_point((0, 0, 255), last_pos)
		draw_point((255, 0, 0), corner_pos)
	else:
		if (contact is not None and reflect is not None):
			# Incoming vector
			draw_line((200, 200, 200), last_pos, contact)
			# Reflected vector
			draw_line((200, 200, 200), contact, reflect)
			draw_point((100, 100, 100), reflect)
			# Point of contact
			draw_point((100, 100, 100), contact)
		elif (new_pos is not None and last_pos is not None and not button_down):
			# Line segment with no intersection
			draw_line((200, 200, 200), last_pos, new_pos)
			draw_point((100, 100, 100), last_pos)
			draw_point((100, 100, 100), new_pos)
		else:
			if (current_pos is not None):
				if (button_down and last_pos is not None):
					draw_line((200, 200, 200), last_pos, current_pos)
				draw_point((100, 100, 100), current_pos)
		if (last_pos is not None):
			draw_point((100, 100, 100), last_pos)

	if (draw_rect):
		pygame.draw.rect(screen, (0, 0, 0), [corner_pos.x - ball_radius * 4, corner_pos.y, ball_radius * 4, ball_radius * 16], 1)

	if (playing):
		if (last_pos is not None and current_pos is not None):
			if (ball_progression < 1.5):
				ball_progression = ball_progression + elapsed_time * 0.0005
			else:
				ball_progression = 0.0
			progression = ball_progression
			if (ball_progression > 1.0):
				progression = 1.0
			if (button_down):
				target_pos = current_pos
			else:
				target_pos = new_pos
			target_to_last_vec = point(x = target_pos.x - last_pos.x, y = target_pos.y - last_pos.y)
			if (reflect is not None and contact is not None):
				prog_vec_len = math.sqrt(math.pow(target_pos.x - last_pos.x, 2) + math.pow(target_pos.y - last_pos.y, 2)) * progression
				last_to_contact_len = math.sqrt(math.pow(last_pos.x - contact.x, 2) + math.pow(last_pos.y - contact.y, 2))
				reflect_to_contact_len = math.sqrt(math.pow(reflect.x - contact.x, 2) + math.pow(reflect.y - contact.y, 2))
				reflect_vec = point(x = contact.x - reflect.x, y = contact.y - reflect.y)
				if (prog_vec_len < last_to_contact_len):
					ball_pos = point(target_to_last_vec.x * progression + last_pos.x, y = target_to_last_vec.y * progression + last_pos.y)
				else:
					inverse_reflect = point(x = last_to_contact_len * (reflect_vec.x / reflect_to_contact_len) + contact.x,
								y = last_to_contact_len * (reflect_vec.y / reflect_to_contact_len) + contact.y)
					ball_pos = point(x = (reflect.x - inverse_reflect.x) * progression + inverse_reflect.x,
							y = (reflect.y - inverse_reflect.y) * progression + inverse_reflect.y)
			else:
				ball_pos = point(target_to_last_vec.x * progression + last_pos.x, y = target_to_last_vec.y * progression + last_pos.y)
			pygame.draw.ellipse(screen, (0, 0, 0), [ball_pos.x - ball_radius, ball_pos.y - ball_radius, ball_radius * 2, ball_radius * 2], 1)
			draw_point((0, 0, 255), ball_pos)

	if (draw_crosshair and current_pos is not None):
		# Mouse crosshair
		draw_line((0, 255, 0), (0, current_pos.y), (width - 1, current_pos.y))
		draw_line((0, 255, 0), (current_pos.x, 0), (current_pos.x, height - 1))

	if (display_help):
		label = font.render("-", 1, (0,0,0))
		screen.blit(label, (130, 50))
		screen.blit(label, (130, 70))
		screen.blit(label, (130, 90))
		screen.blit(label, (130, 110))
		screen.blit(label, (130, 130))
		screen.blit(label, (130, 150))
		screen.blit(label, (130, 170))
		screen.blit(label, (130, 190))
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
		label = font.render("'r'", 1, (0,0,0))
		screen.blit(label, (25, 110))
		label = font.render("toggle rectangle", 1, (0,255,0))
		screen.blit(label, (150, 110))
		label = font.render("'p'", 1, (0,0,0))
		screen.blit(label, (25, 130))
		label = font.render("toggle animation", 1, (0,255,0))
		screen.blit(label, (150, 130))
		label = font.render("'d'", 1, (0,0,0))
		screen.blit(label, (25, 150))
		label = font.render("toggle simple draw", 1, (0,255,0))
		screen.blit(label, (150, 150))
		label = font.render("'n'", 1, (0,0,0))
		screen.blit(label, (25, 170))
		label = font.render("toggle coordinate values", 1, (0,255,0))
		screen.blit(label, (150, 170))
		label = font.render("mouse scroll", 1, (0,0,0))
		screen.blit(label, (25, 190))
		label = font.render("change radius", 1, (0,255,0))
		screen.blit(label, (150, 190))
		label = font.render("mouse drag", 1, (0,0,0))
		screen.blit(label, (25, 210))
		label = font.render("draw line segment / move circle", 1, (0,255,0))
		screen.blit(label, (150, 210))
	pygame.display.flip()
