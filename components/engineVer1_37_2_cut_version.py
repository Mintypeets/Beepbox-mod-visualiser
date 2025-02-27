import pygame
import random
import math
import os
import json


# classes ---------------------------------------------------------------------------------------------------- #

# particle system -------------------------------- #
def get_square_img(size, colour):
    surface = pygame.Surface((size[0], size[1])).convert()
    surface.fill(colour)
    surface.set_colorkey((0, 0, 0))
    return surface


def get_circle_img(size, colour):
    smaller_side = min(size[0], size[1])
    surface = pygame.Surface((smaller_side, smaller_side)).convert()
    pygame.draw.circle(surface, colour, (smaller_side / 2, smaller_side / 2), smaller_side / 2)
    surface.set_colorkey((0, 0, 0))
    return pygame.transform.scale(surface, [size[0], size[1]])


class Particle:
    def __init__(self, life_time, emission_pos, emission_speed, emission_angle, emission_rotation, end_rotation, emission_size, end_size, peak_alpha, emission_colour, end_colour, emission_lighting_colour=(0, 0, 0), end_lighting_colour=(0, 0, 0), life_time_variation=(0, 0), emission_pos_x_variation=(0, 0), emission_pos_y_variation=(0, 0), emission_speed_variation=(0, 0), emission_angle_variation=(0, 0), emission_rotation_variation=(0, 0), end_rotation_variation=(0, 0), emission_size_variation=(0, 0), end_size_variation=(0, 0), peak_alpha_variation=(0, 0), size_fading=(0, 0), colour_fading=(0, 0), lighting_colour_fading=(0, 0), alpha_fading=(0, 0), mirror_rotation_variation=False, mirror_img_variation=(0, 0), img='none', gravity=(0, 0), shape='square', randomization_accuracy=10):
        self.randomization_accuracy = randomization_accuracy

        self.LIFE_TIME = life_time + random.randint(-life_time_variation[0] * self.randomization_accuracy, life_time_variation[1] * self.randomization_accuracy) / self.randomization_accuracy
        self.life_timer = 0

        self.pos = [emission_pos[0] + random.randint(-emission_pos_x_variation[0] * self.randomization_accuracy, emission_pos_x_variation[1] * self.randomization_accuracy) / self.randomization_accuracy,
                    emission_pos[1] + random.randint(-emission_pos_y_variation[0] * self.randomization_accuracy, emission_pos_y_variation[1] * self.randomization_accuracy) / self.randomization_accuracy]
        self.normalized_movement = [math.sin(math.radians(emission_angle - random.randint(-emission_angle_variation[0], emission_angle_variation[1]))), math.cos(math.radians(emission_angle - random.randint(-emission_angle_variation[0], emission_angle_variation[1])))]

        self.speed = emission_speed + random.randint(-emission_speed_variation[0] * self.randomization_accuracy, emission_speed_variation[1] * self.randomization_accuracy) / self.randomization_accuracy

        # size
        self.size_fading = size_fading
        size_variation = random.randint(-emission_size_variation[0] * self.randomization_accuracy, emission_size_variation[1] * self.randomization_accuracy) / self.randomization_accuracy
        self.EMISSION_SIZE = [emission_size[0] + size_variation, emission_size[1] + size_variation]
        if end_size == 'emission size':
            self.END_SIZE = self.EMISSION_SIZE
        else:
            self.END_SIZE = [end_size[0] + random.randint(-end_size_variation[0] * self.randomization_accuracy, end_size_variation[1] * self.randomization_accuracy) / self.randomization_accuracy, end_size[1] + random.randint(-end_size_variation[0] * self.randomization_accuracy, end_size_variation[1] * self.randomization_accuracy) / self.randomization_accuracy]
        self.size = self.EMISSION_SIZE

        # alpha
        self.alpha_fading = alpha_fading
        self.PEAK_ALPHA = peak_alpha + random.randint(-peak_alpha_variation[0] * self.randomization_accuracy, peak_alpha_variation[1] * self.randomization_accuracy) / self.randomization_accuracy
        if self.alpha_fading[0] == 0:
            self.alpha = self.PEAK_ALPHA
        else:
            self.alpha = 0

        # rotation
        mirror_rotation = False
        if mirror_rotation_variation:
            mirror_rotation = random.choice((False, True))
        self.EMISSION_ROTATION = emission_rotation + random.randint(-emission_rotation_variation[0] * self.randomization_accuracy, emission_rotation_variation[1] * self.randomization_accuracy) / self.randomization_accuracy
        self.END_ROTATION = end_rotation + random.randint(-end_rotation_variation[0] * self.randomization_accuracy, end_rotation_variation[1] * self.randomization_accuracy) / self.randomization_accuracy
        if mirror_rotation:
            self.EMISSION_ROTATION = -self.EMISSION_ROTATION
            self.END_ROTATION = -self.END_ROTATION

        self.rotation_angle = self.EMISSION_ROTATION

        # colour
        self.colour_fading = colour_fading
        self.EMISSION_COLOUR = list(emission_colour)
        if end_colour == 'emission colour':
            self.END_COLOUR = list(emission_colour)
        else:
            self.END_COLOUR = list(end_colour)
        self.colour = list(emission_colour)
        self.true_colour = self.colour.copy()

        # lighting colour
        self.lighting_colour_fading = lighting_colour_fading
        self.EMISSION_LIGHTING_COLOUR = list(emission_lighting_colour)
        if end_lighting_colour == 'emission colour':
            self.END_LIGHTING_COLOUR = list(emission_lighting_colour)
        else:
            self.END_LIGHTING_COLOUR = list(end_lighting_colour)
        self.lighting_colour = list(emission_lighting_colour)
        self.true_lighting_colour = self.lighting_colour.copy()

        # misc
        self.gravity = gravity
        self.shape = shape
        self.momentum = [0, 0]
        self.img = img
        self.mirror_img = [random.choice((0, mirror_img_variation[0])),
                           random.choice((0, mirror_img_variation[1]))]

    def update(self, delta_time=1):
        # movement
        self.pos[0] += self.normalized_movement[0] * self.speed * delta_time
        self.pos[1] += self.normalized_movement[1] * self.speed * delta_time

        # applying gravity
        self.momentum[0] += self.gravity[0] * delta_time
        self.pos[0] += self.momentum[0] * delta_time
        self.momentum[1] += self.gravity[1] * delta_time
        self.pos[1] += self.momentum[1] * delta_time

        # applying rotation
        self.rotation_angle += (self.EMISSION_ROTATION - self.END_ROTATION) / self.LIFE_TIME * delta_time

        # lifetime decay
        if self.life_timer < self.LIFE_TIME:
            self.life_timer += delta_time

        # size fading "¯\_"
        if self.LIFE_TIME * self.size_fading[0] / 100 < self.life_timer < self.LIFE_TIME * self.size_fading[1] / 100:
            self.size[0] += (self.END_SIZE[0] - self.EMISSION_SIZE[0]) / (self.LIFE_TIME - self.LIFE_TIME * self.size_fading[0] / 100 - (self.LIFE_TIME - self.LIFE_TIME * self.size_fading[1] / 100)) * delta_time
            self.size[1] += (self.END_SIZE[1] - self.EMISSION_SIZE[1]) / (self.LIFE_TIME - self.LIFE_TIME * self.size_fading[0] / 100 - (self.LIFE_TIME - self.LIFE_TIME * self.size_fading[1] / 100)) * delta_time

        if self.LIFE_TIME * self.size_fading[1] / 100 < self.life_timer:
            self.size = self.END_SIZE

        self.size = [max(0, self.size[0]), max(0, self.size[1])]

        # alpha fading "/¯\"
        if self.LIFE_TIME * self.alpha_fading[0] / 100 > self.life_timer:
            if self.alpha < self.PEAK_ALPHA:
                self.alpha += self.PEAK_ALPHA / (self.LIFE_TIME * self.alpha_fading[0] / 100) * delta_time
        elif self.LIFE_TIME * self.alpha_fading[0] / 100 < self.life_timer < self.LIFE_TIME * self.alpha_fading[1] / 100:
            self.alpha = self.PEAK_ALPHA

        if self.LIFE_TIME * self.alpha_fading[1] / 100 < self.life_timer and self.alpha_fading[1] < 100:  # this check has to be there because if fading is 100, it gets divided by 0
            if self.alpha > 0:
                self.alpha -= self.PEAK_ALPHA / (self.LIFE_TIME - self.LIFE_TIME * self.alpha_fading[1] / 100) * delta_time

        # colour fading "¯\_"
        if self.LIFE_TIME * self.colour_fading[0] / 100 < self.life_timer < self.LIFE_TIME * self.colour_fading[1] / 100:
            self.true_colour[0] -= (self.EMISSION_COLOUR[0] - self.END_COLOUR[0]) / (self.LIFE_TIME * self.colour_fading[1] / 100 - self.LIFE_TIME * self.colour_fading[0] / 100) * delta_time
            self.true_colour[1] -= (self.EMISSION_COLOUR[1] - self.END_COLOUR[1]) / (self.LIFE_TIME * self.colour_fading[1] / 100 - self.LIFE_TIME * self.colour_fading[0] / 100) * delta_time
            self.true_colour[2] -= (self.EMISSION_COLOUR[2] - self.END_COLOUR[2]) / (self.LIFE_TIME * self.colour_fading[1] / 100 - self.LIFE_TIME * self.colour_fading[0] / 100) * delta_time
        elif self.life_timer > self.LIFE_TIME * self.colour_fading[1] / 100:
            self.true_colour = self.END_COLOUR

        for i in range(len(self.colour)):
            self.true_colour[i] = clamp(self.true_colour[i], min(self.EMISSION_COLOUR[i], self.END_COLOUR[i]), max(self.EMISSION_COLOUR[i], self.END_COLOUR[i]))
            self.colour[i] = int(self.true_colour[i])

        # lighting colour fading "¯\_"
        if self.LIFE_TIME * self.lighting_colour_fading[0] / 100 < self.life_timer < self.LIFE_TIME * self.lighting_colour_fading[1] / 100:
            self.true_lighting_colour[0] -= (self.EMISSION_LIGHTING_COLOUR[0] - self.END_LIGHTING_COLOUR[0]) / (self.LIFE_TIME * self.lighting_colour_fading[1] / 100 - self.LIFE_TIME * self.lighting_colour_fading[0] / 100) * delta_time
            self.true_lighting_colour[1] -= (self.EMISSION_LIGHTING_COLOUR[1] - self.END_LIGHTING_COLOUR[1]) / (self.LIFE_TIME * self.lighting_colour_fading[1] / 100 - self.LIFE_TIME * self.lighting_colour_fading[0] / 100) * delta_time
            self.true_lighting_colour[2] -= (self.EMISSION_LIGHTING_COLOUR[2] - self.END_LIGHTING_COLOUR[2]) / (self.LIFE_TIME * self.lighting_colour_fading[1] / 100 - self.LIFE_TIME * self.lighting_colour_fading[0] / 100) * delta_time
        elif self.life_timer > self.LIFE_TIME * self.lighting_colour_fading[1] / 100:
            self.true_lighting_colour = self.END_LIGHTING_COLOUR

        for i in range(len(self.lighting_colour)):
            self.true_lighting_colour[i] = clamp(self.true_lighting_colour[i], min(self.EMISSION_LIGHTING_COLOUR[i], self.END_LIGHTING_COLOUR[i]), max(self.EMISSION_LIGHTING_COLOUR[i], self.END_LIGHTING_COLOUR[i]))
            self.lighting_colour[i] = int(self.true_lighting_colour[i])

    def draw_blending(self, surface, lighting_size_multiplier, dominant_lighting_colour=(0, 0, 0), scroll=(0, 0)):
        if dominant_lighting_colour != (0, 0, 0):
            self.lighting_colour = dominant_lighting_colour
        if self.size > 0:
            if self.img == 'none':
                draw(globals()['get_' + str(self.shape) + '_img'](self.size * lighting_size_multiplier, self.lighting_colour), surface,
                     (self.pos[0] - scroll[0], self.pos[1] - scroll[1]), self.rotation_angle, ('center', 'center'), alpha=self.alpha, blending=True)
            else:
                draw(pygame.transform.scale(pygame.transform.flip(recolour(self.img, self.lighting_colour), self.mirror_img[0], self.mirror_img[1]), (self.img.get_width() * self.size * lighting_size_multiplier,
                                                                                                                                                      self.img.get_height() * self.size * lighting_size_multiplier)),
                     surface, (self.pos[0] - scroll[0], self.pos[1] - scroll[1]), self.rotation_angle, ('center', 'center'), alpha=self.alpha, blending=True)

    def draw(self, surface, scroll=(0, 0), display_mode=False):
        if self.img == 'none':
            draw(globals()['get_' + str(self.shape) + '_img'](self.size, self.colour), surface, (self.pos[0] - scroll[0] + display_mode, self.pos[1] - scroll[1] + display_mode), self.rotation_angle, ('center', 'center'), alpha=self.alpha)
        else:
            draw(pygame.transform.scale(pygame.transform.flip(self.img, self.mirror_img[0], self.mirror_img[1]), (self.img.get_width() * self.size[0], self.img.get_height() * self.size[1])), surface, (self.pos[0] - scroll[0], self.pos[1] - scroll[1]), self.rotation_angle, ('center', 'center'), alpha=self.alpha)

# animation system ------------------------------------- #
class Animation:
    def __init__(self, frames, loops, frame_multiplier=1, start_play_state=False):
        self.timer = 1
        self.is_playing = start_play_state
        self.loops = loops

        self.animation_frames = []
        for frame in frames:  # singular frame = [value, time]
            for i in range(frame[1] * int(frame_multiplier)):
                self.animation_frames.append(frame[0])

    def advance(self, delta_time=1):
        if self.is_playing:
            self.timer += delta_time
            if self.timer >= len(self.animation_frames):
                if self.loops:
                    self.timer = 1
                else:
                    self.timer = len(self.animation_frames)
                    self.is_playing = False

    def get_frame_contents(self):
        return self.animation_frames[int(self.timer) - 1]

    def stop(self):
        self.is_playing = False
        self.timer = 1

# functions ---------------------------------------------------------------------------------------------------------- #

# hex colour code to/from rgb conversion
def hex_to_rgb(hex_code):
    return [int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)]


def rgb_to_hex(rgb_list):
    hex_code_list = list()
    for num in rgb_list:
        hex_code_list.append(backspace_from_front(hex(num), 2))
    for item in range(len(hex_code_list)):
        if len(hex_code_list[item]) == 1:
            hex_code_list[item] = '0' + hex_code_list[item]
    return hex_code_list[0] + hex_code_list[1] + hex_code_list[2]


# reverse string
def reverse(string):
    return string[::-1]


# backspace string
def backspace(string, backspace_amount):
    new_string = str()
    for i in range(len(string) - backspace_amount):
        new_string += string[i]
    return new_string


# reading and writing to a txt file functions
def read_json(path):
    if os.path.isfile(path):
        file = open(path, 'r')
        value = json.loads(file.read())
        file.close()
        return value
    else:
        print(f'path "{path}" doesnt exist')


# random screen shake system --------------------------- #
def get_randomized_screen_shake_anim(power, life_time, start_decaying):
    current_power = power
    pos = pygame.Vector2(random.randint(int(-current_power * 25), int(current_power * 25)) / 10,
                         random.randint(int(-current_power * 25), int(current_power * 25)) / 10)
    timer = life_time
    anim_frames = list()
    anim_frames.append([pos, 2])
    for i in range(int(timer)):
        timer -= 1
        if timer < life_time - start_decaying:
            current_power -= power / (life_time - start_decaying)

        last_pos = pos.copy()
        next_pos = pygame.Vector2(random.randint(int(-current_power * 10), int(current_power * 10)) / 10,
                                  random.randint(int(-current_power * 10), int(current_power * 10)) / 10)

        for i in range(2):
            pos += (next_pos - last_pos) / 1.6
            anim_frames.append([pos.copy(), 1])
    anim_frames.append([pygame.Vector2(0), 1])
    return Animation(anim_frames, False, start_play_state=True)


# directional screen shake system ---------------------- #
def get_directional_screen_shake_anim(angle, power, iterations):
    pos = pygame.Vector2(math.sin(math.radians(angle)) * power,
                         math.cos(math.radians(angle)) * power)
    anim_frames = list()
    anim_frames.append([pos.copy(), 1])
    for iteration in range(iterations):
        next_pos = pos.copy() * -0.75
        last_pos = pos.copy()
        for i in range(3):
            pos += (next_pos - last_pos) / 3
            anim_frames.append([pos.copy(), 1])
    anim_frames.append([pygame.Vector2(0), 1])
    return Animation(anim_frames, False, 1, start_play_state=True)


# custom drawing function --------------------------------------- #
def draw(img, surface, pos, angle=0, alignment=('left', 'top'), blending=False, alpha=255):
    if angle != 0: img = pygame.transform.rotate(img, angle)
    if alpha < 255: img.set_alpha(alpha)

    offset_value = [0, 0]
    if alignment[0] == 'center': offset_value[0] = img.get_width() / 2
    elif alignment[0] == 'right': offset_value[0] = img.get_width()
    if alignment[1] == 'center': offset_value[1] = img.get_height() / 2
    elif alignment[1] == 'bottom': offset_value[1] = img.get_height()

    if blending:
        surface.blit(img, (pos[0] - offset_value[0], pos[1] - offset_value[1]), special_flags=pygame.BLEND_RGBA_ADD)
    else:
        surface.blit(img, (pos[0] - offset_value[0], pos[1] - offset_value[1]))


# number clamping and looping function ----------------------------------- #
def clamp(number, smallest, biggest):
    return max(smallest, min(number, biggest))
