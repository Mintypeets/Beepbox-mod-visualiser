from components.engineVer1_37_2_cut_version import *
import time
import colorsys
import os

pygame.init()
pygame.mixer.init()
pygame.mixer.pre_init()

# setup
clock = pygame.time.Clock()

MONITOR_SIZE = pygame.Vector2(pygame.display.Info().current_w, pygame.display.Info().current_h)
SCREEN_SIZE = pygame.Vector2(1920 / 5 * 4, 1080 / 5 * 4)
screen = pygame.display.set_mode(SCREEN_SIZE)

DISPLAY_TO_SCREEN_RATIO = 4

DISPLAY_SIZE = SCREEN_SIZE / DISPLAY_TO_SCREEN_RATIO + pygame.Vector2(1)
display = pygame.Surface(DISPLAY_SIZE).convert()
dest_display = pygame.Surface(DISPLAY_SIZE * DISPLAY_TO_SCREEN_RATIO).convert()
display.set_colorkey((0, 0, 0))
dest_display.set_colorkey((0, 0, 0))

white_surf = pygame.Surface(SCREEN_SIZE).convert()
white_surf.set_colorkey((0, 0, 0))
white_surf_colour = 0
white_surf.fill((white_surf_colour, white_surf_colour, white_surf_colour))
black_surf = pygame.Surface(SCREEN_SIZE).convert()
black_surf.set_colorkey((0, 0, 0))
black_surf_colour = 10
black_surf.fill((black_surf_colour, black_surf_colour, black_surf_colour))

particles = list()

random_screen_shake = pygame.Vector2(0)
directional_screen_shake = pygame.Vector2(0)
random_screen_shake_anim = get_randomized_screen_shake_anim(0, 0, 0)
directional_screen_shake_anim = get_directional_screen_shake_anim(0, 0, 0)
# variables ------------------------------------------------------------- #
for dir in os.listdir("./"):  # current directory
    if dir.endswith('.json'):
        with open(dir, encoding='utf8') as file:
            song_json = json.loads(file.read())

PITCH_NOTES_ON_SCREEN = 8 * 12 + 1
DRUM_NOTES_ON_SCREEN = 12
NOTE_WIDTH = SCREEN_SIZE[1] / PITCH_NOTES_ON_SCREEN
DRUM_NOTE_HEIGHT = SCREEN_SIZE[1] / DRUM_NOTES_ON_SCREEN
FORCED_SONG_TPB = 4  # ticks per beat
# forced_song_tpb_channel_list = [4, 4, 4, 4, 4, 4, 4, 4, 4]
# drum_channel_length_modifier_list = [0.8 + 0.5, 0.85 + 0.5, 0.9 + 0.5]
# base_speed = 0.3
# channel_length_modifier_list = [base_speed + 0.7, base_speed + 0.75, base_speed + 0.8, base_speed + 0.85, base_speed + 0.9,  # percussion
#                                 base_speed + 0.95, base_speed + 1, base_speed + 1.05, base_speed + 1.1, base_speed + 1.15, base_speed + 1.2, base_speed + 1.25, base_speed + 1.3, base_speed + 1.35, base_speed + 1.4, base_speed + 1.45, base_speed + 1.5]  # notes
# channel_length_modifier_list = [base_speed, base_speed, base_speed,  # percussion
#                                 base_speed, base_speed, base_speed, base_speed, base_speed, base_speed]  # notes
# channel_colour_dict = {'pitch': [[hex_to_rgb('34040a'), hex_to_rgb('34240a'), hex_to_rgb('26340a'), hex_to_rgb('08340a'), hex_to_rgb('043428'), hex_to_rgb('04283b'), hex_to_rgb('101758'), hex_to_rgb('20104f'), hex_to_rgb('20104f'), hex_to_rgb('20104f'), hex_to_rgb('20104f'), hex_to_rgb('20104f')],  # off
#                                  [hex_to_rgb('ff5959'), hex_to_rgb('ffc559'), hex_to_rgb('cdff59'), hex_to_rgb('61ff59'), hex_to_rgb('59ffbd'), hex_to_rgb('59d5ff'), hex_to_rgb('5969ff'), hex_to_rgb('9059ff'), hex_to_rgb('9059ff'), hex_to_rgb('9059ff'), hex_to_rgb('9059ff'), hex_to_rgb('9059ff')]], # on
#                        'drum': [[hex_to_rgb('311e27'), hex_to_rgb('302728'), hex_to_rgb('302c23'), hex_to_rgb('302c23'), hex_to_rgb('302c23')],  # off
#                                 [hex_to_rgb('c77a7a'), hex_to_rgb('d3a682'), hex_to_rgb('d3c16a'), hex_to_rgb('d3c16a'), hex_to_rgb('d3c16a')]]} # on

settings_info = read_json('settings.txt')

pitch_channel_count = 0
drum_channel_count = 0
for channel in song_json['channels']:
    if channel['type'] == 'pitch': pitch_channel_count += 1
    elif channel['type'] == 'drum': drum_channel_count += 1

base_note_speed = settings_info['base note speed']
parallax_increment = settings_info['parallax increment']
channel_length_modifier_list = list()
for i in range(drum_channel_count + pitch_channel_count):
    channel_length_modifier_list.append(base_note_speed + parallax_increment * i)
# channel_length_modifier_list = [base_speed + 0.7, base_speed + 0.75, base_speed + 0.8, base_speed + 0.85, base_speed + 0.9,  # percussion
#                                 base_speed + 0.95, base_speed + 1, base_speed + 1.05, base_speed + 1.1, base_speed + 1.15, base_speed + 1.2, base_speed + 1.25, base_speed + 1.3, base_speed + 1.35, base_speed + 1.4, base_speed + 1.45, base_speed + 1.5]  # notes
#
# custom_color_skin_info = 'no custom skin'
# if os.path.isfile('custom color skin.txt'):
#     custom_color_skin_info = read_json('custom color skin.txt')

#                                [off, on]
channel_colour_dict = {'pitch': [list(), list()],
                       'drum': [list(), list()]}

if settings_info['pitch hue increment'] == "default":
    pitch_hue_increment = 20 / 255  # values from beep box (28?)
else: pitch_hue_increment = settings_info['pitch hue increment'] / 255
if settings_info['drum hue increment'] == "default":
    drum_hue_increment = 16 / 255
else: drum_hue_increment = settings_info['drum hue increment'] / 255

darken_notes_factor = settings_info['darken notes factor']

if settings_info['start pitch HSV'] == "default":
    pitch_rainbow_color_HSV = pygame.Vector3(0, 0.65, 1)
else:
    loaded_HSV = settings_info['start pitch HSV']
    pitch_rainbow_color_HSV = pygame.Vector3(loaded_HSV[0] / 360, loaded_HSV[1] * 0.01, loaded_HSV[2] * 0.01)

for i in range(pitch_channel_count):
    print(pitch_rainbow_color_HSV)
    channel_colour_dict['pitch'][0].append(pygame.Vector3(colorsys.hsv_to_rgb(pitch_rainbow_color_HSV[0], pitch_rainbow_color_HSV[1], pitch_rainbow_color_HSV[2] * darken_notes_factor)) * 255)
    channel_colour_dict['pitch'][1].append(pygame.Vector3(colorsys.hsv_to_rgb(pitch_rainbow_color_HSV[0], pitch_rainbow_color_HSV[1], pitch_rainbow_color_HSV[2])) * 255)
    pitch_rainbow_color_HSV[0] += pitch_hue_increment
    pitch_rainbow_color_HSV[0] = pitch_rainbow_color_HSV[0] % 255

if settings_info['start drum HSV'] == "default":
    drum_rainbow_color_HSV = pygame.Vector3(0, 0.32, 0.76)
else:
    loaded_HSV = settings_info['start drum HSV']
    drum_rainbow_color_HSV = pygame.Vector3(loaded_HSV[0] / 360, loaded_HSV[1] * 0.01, loaded_HSV[2] * 0.01)

# drum_rainbow_color = pygame.Vector3(0, 0.28, 0.46)
for i in range(drum_channel_count):
    channel_colour_dict['drum'][0].append(pygame.Vector3(colorsys.hsv_to_rgb(drum_rainbow_color_HSV[0], drum_rainbow_color_HSV[1], drum_rainbow_color_HSV[2] * darken_notes_factor)) * 255)
    channel_colour_dict['drum'][1].append(pygame.Vector3(colorsys.hsv_to_rgb(drum_rainbow_color_HSV[0], drum_rainbow_color_HSV[1], drum_rainbow_color_HSV[2])) * 255)
    drum_rainbow_color_HSV[0] += drum_hue_increment
    drum_rainbow_color_HSV[0] = drum_rainbow_color_HSV[0] % 255

kick_channel_idx = settings_info['kick channels']

snare_drum_channel_idx = 1  # MINT NOTE: currently unused but can be used to make some other effects later

EXPORT_FPS = 30
black_fade_in_frames = 3 * EXPORT_FPS  # currently unused


CURSOR_OFFSET = 250 # SCREEN_SIZE[0] * 0.5
song_pos = 0
cursor_colour = (255, 255, 255)


note_highlight_list = list()
for i in range(9):
    note_highlight_list.append(i * 12 + 1)
note_highlight_colour = hex_to_rgb('130a22')


# classes / functions ------------------------------------------------------- #

def clip_note_into_bar(note, bar_tick_count):
    clipped_note = Note(note.type)
    # print("clip note ------------ #")
    for point_idx in range(len(note.points)):
        # print(note.points[point_idx][0].x, bar_tick_count)
        # if point_idx == 0 and note.points[point_idx][0].x >= bar_tick_count:
        #     clipped_note = list()
        #     print('discard note, first point is past the edge')
        #     break

        if note.points[point_idx][0].x <= bar_tick_count:
            clipped_note.points.append(note.points[point_idx])
            # print('add point, it's before or on the edge') # debug
            if point_idx == 0 and note.points[point_idx][0].x == bar_tick_count:
                clipped_note = list()
                break
            # if note.points[point_idx][0].x == bar_tick_count:
        else:
            t = (bar_tick_count - note.points[point_idx - 1][0].x) / (note.points[point_idx][0].x - note.points[point_idx - 1][0].x)
            lerped_note_height = t * (note.points[point_idx][0].y - note.points[point_idx - 1][0].y) + note.points[point_idx - 1][0].y
            lerped_note_volume = t * (note.points[point_idx][1] - note.points[point_idx - 1][1]) + note.points[point_idx - 1][1]
            # print('point is past edge, lerp a point onto the edge', note.points, t, lerped_note_height, lerped_note_volume)
            clipped_note.points.append([pygame.Vector2(bar_tick_count, lerped_note_height), lerped_note_volume])
            # if point_idx == 0:
            #     clipped_note = list()
            break

        # if note.points[point_idx][0].x >= bar_tick_count: # point is past edge
        #     print('point is past edge')
        #     break
    if not isinstance(clipped_note, list):
        clipped_note = [clipped_note]

    # for clipped in clipped_note:
    #     print('comparison', note.points == clipped.points, note.points, clipped.points)
    return clipped_note

def clip_note_into_gap(note, gap):
    # print('gap', gap)
    new_note = list()
    first_gap_point = False
    last_gap_point = False
    first_gap_point_interpolation_point_idx_list = list()
    last_gap_point_interpolation_point_idx_list = list()
    # last_point = note[0]
    # last_point_inside_gap = gap[0] < last_point[0] < gap[1]
    for point_idx in range(len(note)):  # for some reason this started from 1 before
        if not first_gap_point:
            if not first_gap_point_interpolation_point_idx_list:  # if is empty
                if note[point_idx][0] > gap[0] and point_idx > 0:
                    first_gap_point_interpolation_point_idx_list = [point_idx - 1, point_idx]
        if not last_gap_point:
            if not last_gap_point_interpolation_point_idx_list:  # if is empty
                if note[point_idx][0] > gap[1] and point_idx > 0:
                    last_gap_point_interpolation_point_idx_list = [point_idx - 1, point_idx]

        if gap[0] <= note[point_idx][0] <= gap[1]:
            new_note.append([note[point_idx][0], note[point_idx][1]])
            if note[point_idx][0] == gap[0]:
                first_gap_point = True
            if note[point_idx][0] == gap[1]:
                last_gap_point = True
        # last_point = note[point_idx]

    # print('lll', first_gap_point_interpolation_point_idx_list)
    # print('lll', last_gap_point_interpolation_point_idx_list)

    if not first_gap_point and first_gap_point_interpolation_point_idx_list:
        point_before_first_gap = note[first_gap_point_interpolation_point_idx_list[0]]
        point_after_first_gap = note[first_gap_point_interpolation_point_idx_list[1]]
        t = (gap[0] - point_before_first_gap[0]) / (point_after_first_gap[0] - point_before_first_gap[0])
        # print('first', t)
        if 1 > t > 0:
            new_note.insert(0, [gap[0], t * (point_after_first_gap[1] - point_before_first_gap[1]) + point_before_first_gap[1]])
    if not last_gap_point and last_gap_point_interpolation_point_idx_list:
        point_before_second_gap = note[last_gap_point_interpolation_point_idx_list[0]]
        point_after_second_gap = note[last_gap_point_interpolation_point_idx_list[1]]
        t = (gap[1] - point_before_second_gap[0]) / (point_after_second_gap[0] - point_before_second_gap[0])
        # print('last', t)
        if 1 > t > 0:
            new_note.append([gap[1], t * (point_after_second_gap[1] - point_before_second_gap[1]) + point_before_second_gap[1]])

    # print('new note', new_note)

    return new_note

# borders = [[[x1, t1], [x2, t2]], [[x1, x2], [x3, x4]]]
# clip_note_inside_borders([x1, x4], borders) = [x2, x3]
def clip_note_inbetween_borders(note, border_list, bar_tick_count):
    gap = [0, 0]
    new_border_list = border_list.copy()
    # print('border list at start', border_list)
    for border_note_idx in range(len(border_list) + 1):
        if border_note_idx == len(border_list):
            gap[1] = bar_tick_count
        else:
            gap[1] = border_list[border_note_idx][0][0] # gap right = tick of first note

        # print('border note idx', border_note_idx)

        if gap[0] - gap[1] != 0:
            clipped_note = clip_note_into_gap(note, gap)
            if len(clipped_note) > 1:  # note must have more than 1 points
                new_border_list.insert(border_note_idx + len(new_border_list) - len(border_list), clip_note_into_gap(note, gap))
                # print('border after addition', new_border_list)

        if border_note_idx < len(border_list):
            gap[0] = border_list[border_note_idx][len(border_list[border_note_idx]) - 1][0] # gap left = tick of last note
    return new_border_list

# clip_borders = [[[0, 40], [4, 60]], [[6, 50], [20, 70]]]
# note_for_clip = [[2, 100], [5, 100]]
# print('clipped:', clip_note_inbetween_borders(note_for_clip, clip_borders, 32))
# for clipped_note in clip_note_inbetween_borders(note_for_clip, clip_borders, 32):
#     print('clipped:', clipped_note)
# print('separator # ----------------------------------------------------------------------- #')

# MINT NOTE: I was trying to make mod channel "tempo" setting work, but I gave up
def get_song_pos_from_bpm_graph(time, mod_info, forced_song_tpb):
    if mod_info['tempo'][0] == []:
        return time * song_json['beatsPerMinute'] / 60 * forced_song_tpb
    # bar_idx = 0
    cursor_pos = 0
    for bar_idx in range(len(mod_info['bar tick count'])):
        bar_tick_count = mod_info['bar tick count'][bar_idx]



        # bar_idx += 1

        # beat_count_in_bar = bar_length / FORCED_SONG_TPB
        # beats_per_second = 2  # 120 / 60
        #
        # bar_seconds_counter += beat_count_in_bar / 2
        # if time <= bar_seconds_counter:
        #     break
    # print(bar_idx, bar_seconds_counter)
    return 0#time * 120/60 * FORCED_SONG_TPB


class Note:
    def __init__(self, type):
        self.type = type
        self.points = list()
        self.pulse_colour = 0
        self.is_on_cursor = False
        self.cursor_collision_point = ['pos', 'volume']
        self.particle_timer = 0
        self.PARTICLE_TIME = 4

# for dir in os.listdir("./"):  # current directory
#     if dir.endswith('.json'):
#         with open(dir, encoding='utf8') as file:
#             song_json = json.loads(file.read())

EXPORTED_SONG_TPB = song_json['ticksPerBeat']
#PATTERN_WIDTH = song_json['beatsPerBar'] * FORCED_SONG_TPB * NOTE_WIDTH
pattern_tick_count_list = list()
base_song_bpm = song_json['beatsPerMinute']

# next bar = [bar_len, bar_len, bar_len]
# tempo = [[note_x1, note_x2], [note_x3, note_x4]] with priority already baked in
# prioritize:
# 1.bottom channel to top
# 2.top note to bottom

# wanted_channel_pointers = {'next bar': list(),
#                            'tempo': list()}

bar_tick_count_channel_list = list()
tempo_channel_list = list()

for channel in song_json['channels']:
    if channel['type'] != 'mod':
        continue

    # mod_channel_next_bar_notes_list = list()
    # getting a channels specific setting note list
    next_bar_modulator_idx_list = list()
    tempo_modulator_idx_list = list()
    for i in range(len(channel['instruments'][0]['modChannels'])):
        #print(i)
        if channel['instruments'][0]['modChannels'][i] == -1:  # song mod
            if channel['instruments'][0]['modSettings'][i] == 2:  # tempo setting
                tempo_modulator_idx_list.append(5 - i)  # 5 because there are 6 mod channels
                # pass
                # wanted_channel_pointers['tempo'].append(5 - i)  # 5 because there are 6 mod channels
                # print('tempo', 5 - i)
            elif channel['instruments'][0]['modSettings'][i] == 4:  # next bar setting
                next_bar_modulator_idx_list.append(5 - i)  # 5 because there are 6 mod channels
                # for pattern in channel['patterns']:
                #     # if pattern['notes']:  # if notes list is not empty
                #     #next_bar_pattern_note_list = list()
                #     bar_tick_count = FORCED_SONG_TPB * song_json['beatsPerBar']  # the default song tick per bar
                #     for note_info in pattern['notes']:  # getting the first "next bar" note
                #         if note_info['pitches'][0] == 5 - i:  # 5 because there are 6 mod channels
                #             # bar_tick_count = note_info['points'][0]['tick']
                #             for note_pitch in note_info['pitches']:
                #                 note = Note(channel['type'])
                #                 for point in note_info['points']:
                #                     note.points.append(point['tick'])
                #                 #next_bar_pattern_note_list.append(note)
                #                 break
                    #pattern_tick_count_list.append(bar_tick_count)
                # wanted_channel_pointers['next bar'].append(5 - i)  # 5 because there are 6 mod channels
                # print('next bar', 5 - i)

    # making tempo pattern info
    tempo_patterns_list = list()
    for i in range(len(channel['patterns'])):
        pattern = channel['patterns'][i]
        pattern_notes_list = list()
        for note_info in pattern['notes']:
            if note_info['pitches'][0] in tempo_modulator_idx_list:
                note = Note(channel['type'])
                for point in note_info['points']:                     # +1 because its 0-499
                    note.points.append([point['tick'], point['volume'] + 1, note_info['pitches'][0]])
                pattern_notes_list.append(note)
        tempo_patterns_list.append(pattern_notes_list)

    # making "next bar" pattern info
    tick_count_pattern_list = list()
    for i in range(len(channel['patterns'])):
        pattern = channel['patterns'][i]
        bar_tick_count = song_json['beatsPerBar'] * FORCED_SONG_TPB  # the default song tick per bar
        #print(bar_tick_count, forced_song_tpb_channel_list, forced_song_tpb_channel_list[channel_idx])
        for note in pattern['notes']:
            if note['pitches'][0] in next_bar_modulator_idx_list:
                bar_tick_count = note['points'][0]['tick'] * FORCED_SONG_TPB / EXPORTED_SONG_TPB  # possibly fake (MINT NOTE: what does that mean???? I guess I was skeptical of this approach working?)
                break

        tick_count_pattern_list.append(bar_tick_count)

    # using pattern info to create a list of bar lengths and tempo notes
    tick_count_channel_list = list()
    tempo_channel_notes_list = list()
    for i in range(len(channel['sequence'])):
        # next bar patterns
        bar_tick_count = song_json['beatsPerBar'] * FORCED_SONG_TPB
        if channel['sequence'][i]:
            bar_tick_count = tick_count_pattern_list[channel['sequence'][i] - 1]
        tick_count_channel_list.append(bar_tick_count)
        # tempo patterns
        bar_notes_list = list()
        for i in range(5, -1, -1):  # (5, 4, 3, 2, 1, 0) following the priority of notes from top to bottom  # MINT NOTE: im not sure why I used another "i" in the for loop here, but I don't want to break it, so I'll leave it as is for now, it's for the tempo mod channel thing so it wouldn't really matter anyway
            modulator_notes_list = [note.points for note in tempo_patterns_list[channel['sequence'][i] - 1] if note.points[0][2] == i]
            if modulator_notes_list:  # is not empty:
                bar_notes_list.append(modulator_notes_list)
                #print(modulator_notes_list)
        tempo_channel_notes_list.append(bar_notes_list)

    bar_tick_count_channel_list.append(tick_count_channel_list)
    tempo_channel_list.append(tempo_channel_notes_list)
    # print(wanted_channel_pointers)

mod_channel_info = {'bar tick count': bar_tick_count_channel_list[0].copy(),  #[FORCED_SONG_TPB * song_json['beatsPerBar'] for i in range(len(tick_count_channel_list))]
                    'tempo': list()}

# getting the smallest bar width out of the list for each bar
for i in range(len(bar_tick_count_channel_list)):
    for j in range(len(bar_tick_count_channel_list[i])):
        if bar_tick_count_channel_list[i][j] < mod_channel_info['bar tick count'][j]:
            mod_channel_info['bar tick count'][j] = bar_tick_count_channel_list[i][j]

for bar_idx in range(len(tempo_channel_list[0])):  # going through tempo notes bar per bar
    processed_tempo_bar = list()
    for channel_idx in range(len(tempo_channel_list) - 1, -1, -1):  # going through channels of tempo notes in priority from bottom to top
        for pitch_idx in range(len(tempo_channel_list[channel_idx][bar_idx])):
            notes_list = tempo_channel_list[channel_idx][bar_idx][pitch_idx]
            for note in notes_list:  # note = [[tick_1, tempo_1, pitch_1], [tick_2, tempo_2, pitch_2] ..., [tick_n, tempo_n, pitch_n]]
                processed_tempo_bar = clip_note_inbetween_borders(note, processed_tempo_bar, mod_channel_info['bar tick count'][bar_idx])
    mod_channel_info['tempo'].append(processed_tempo_bar)

# for bar in mod_channel_info['tempo']:
#     print('bar')
#     for note in bar:
#         print(note)
# print(mod_channel_info['tempo'])

# loading in tempo notes from patterns list with tempo notes priority of channels bottom to top and notes top to bottom
#print(range(0, 2))
#print('print pattern')
#print(tempo_patterns_list)
# for i in range(2, -1, -1):  # (2, 1, 0), reverse order because channel priority is reverse for some reason
#     print(tempo_patterns_list[i])
#     pass

channel_note_dict = {'pitch': list(),
                     'drum': list()}

for channel in song_json['channels']:
    if channel['type'] == 'pitch':
        note_height = NOTE_WIDTH
    elif channel['type'] == 'drum':
        note_height = DRUM_NOTE_HEIGHT
    else:
        continue

    pattern_list = list()
    for pattern in channel['patterns']:
        # if pattern['notes']:  # if notes list is not empty
        pattern_note_list = list()
        for note_info in pattern['notes']:
            for note_pitch in note_info['pitches']:
                note = Note(channel['type'])
                for point in note_info['points']:
                    note.points.append([pygame.Vector2(point['tick'], note_height * (note_pitch + point['pitchBend'])) + pygame.Vector2(0, note_height * 0.5), point['volume']])
                pattern_note_list.append(note)
        pattern_list.append(pattern_note_list)

    channels_note_list = list()
    # note_list = list()
    bar_offset = 0
    for i in range(len(channel['sequence'])):
        if channel['sequence'][i]:  # is not 0
            for note_object in pattern_list[channel['sequence'][i] - 1]:
                note = Note(channel['type'])

                for point in note_object.points:
                    note.points.append([pygame.Vector2(point[0].x * FORCED_SONG_TPB / EXPORTED_SONG_TPB, SCREEN_SIZE[1] - point[0].y), point[1]])

                clipped_note = clip_note_into_bar(note, mod_channel_info['bar tick count'][i])

                for clipped in clipped_note:
                    # print(clipped.points)
                    if len(clipped.points) > 1:
                        for point_idx in range(len(clipped.points)):
                            clipped.points[point_idx][0].x = clipped.points[point_idx][0].x * NOTE_WIDTH + bar_offset
                        channels_note_list.append(clipped)
        bar_offset += mod_channel_info['bar tick count'][i] * NOTE_WIDTH #* forced_song_tpb_channel_list[channel_idx] / 4  # <<<< IDK WHY
    channel_note_dict[channel['type']].append(channels_note_list)
            # channels_note_list.extend(note_list)

channel_start_note_dict = dict()
for key in channel_note_dict:
    start_note_list = list()
    for i in range(len(channel_note_dict[key])):
        start_note_list.append(0)
    channel_start_note_dict[key] = start_note_list
# song_json = read_json('components/ultraboks.json')

# MINT NOTE: at first I tried making this visualiser by using midi (.mid files), but decided to switch to .json later
# mid = MidiFile('components/midis/ultraboks crazy speed changer.mid')
#
# # pitch wheel : 340 = 1 note
# # the lowest note is at 12
#
#
# midi_timer = 0
# for msg in mid:
#     midi_timer += msg.time
#     print(midi_timer, msg)
#     # if msg.type == "note_on":
#     #     midi_timer += msg.time
#     #     print('note on time:', midi_timer, msg.note, msg.velocity, msg.channel)
#     # if msg.type == "note_off":
#     #     midi_timer += msg.time
#     #     print('note off time:', midi_timer, msg.note, msg.velocity, msg.channel)
#     # else:
#     #     print('random', msg)


# def parse_midi_file(path):
#     with open(path, 'rb') as file:
#         value = file.read()
#     print(value)
#     for thing in value:
#         print(thing)
#         #print(thing[0])
#         # if thing[0] == x:
#         # print(int(thing, 0))
#     #return value
#
#
# parse_midi_file('simpul.mid')


def drawing():
    screen.fill((4, 4, 16))
    display.fill(pygame.Vector3(0))
    # drawing stuff onto screen behind display ----------------------------------------------------------------------- #

    for note_idx in note_highlight_list:
        pygame.draw.rect(screen, note_highlight_colour, ((0, SCREEN_SIZE[1] - note_idx * NOTE_WIDTH - scroll[1]), (SCREEN_SIZE[0], NOTE_WIDTH + 1)))

    for channel_idx in range(len(channel_note_dict['drum'])):  # going through all channels and drawing notes with corresponding colour
        for note_idx in range(channel_start_note_dict['drum'][channel_idx], len(channel_note_dict['drum'][channel_idx])):
            note = channel_note_dict['drum'][channel_idx][note_idx]
            if channel_length_modifier_list[channel_idx] * (note.points[0][0].x - song_pos * NOTE_WIDTH) + CURSOR_OFFSET > SCREEN_SIZE[0]:
                break

            if note_idx - channel_start_note_dict['drum'][channel_idx] == 0:
                if channel_length_modifier_list[channel_idx] * (note.points[len(note.points) - 1][0].x - song_pos * NOTE_WIDTH) + CURSOR_OFFSET < 0:
                    channel_start_note_dict['drum'][channel_idx] = note_idx + 1

            if len(channel_colour_dict['drum'][True]) < channel_idx:  # possibly bugged
                note_colour = pygame.Vector3(100, 50, 0)
            else:
                note_colour = pygame.Vector3(channel_colour_dict['drum'][True][channel_idx])

            note_colour += pygame.Vector3(note.pulse_colour)
            for colour_channel_idx in range(len(note_colour)):
                note_colour[colour_channel_idx] = clamp(note_colour[colour_channel_idx], 0, 255)

            #song_pos = get_song_pos_from_bpm_graph(time.time() - start_time, mod_channel_info, FORCED_SONG_TPB)# * channel_length_modifier_list[i]

            note_points = list()
            if note.is_on_cursor:
                for point in note.points:
                    if point[0].x > song_pos * NOTE_WIDTH:
                        if len(note_points) == 0:
                            note_points.append(note.cursor_collision_point)
                        note_points.append(point)
            else:
                note_points = note.points

            bottom_points = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx], point[0].y) + pygame.Vector2(0, point[1] * DRUM_NOTE_HEIGHT * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note.points]
            top_points_reversed = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx], point[0].y) - pygame.Vector2(0, point[1] * DRUM_NOTE_HEIGHT * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note.points]
            top_points_reversed.reverse()
            base_points = top_points_reversed
            base_points.extend(bottom_points)

            bottom_shreaded_points = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx], point[0].y) + pygame.Vector2(0, point[1] * DRUM_NOTE_HEIGHT * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note_points]
            top_shreaded_points_reversed = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx], point[0].y) - pygame.Vector2(0, point[1] * DRUM_NOTE_HEIGHT * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note_points]
            top_shreaded_points_reversed.reverse()
            shreaded_points = top_shreaded_points_reversed
            shreaded_points.extend(bottom_shreaded_points)

            #pygame.draw.lines(screen, note_colour, False, bottom_points, int(DRUM_NOTE_HEIGHT))
            if note.pulse_colour > 0:
                pygame.draw.polygon(screen, channel_colour_dict['drum'][False][channel_idx], base_points)

            if note.points[len(note.points) - 1][0].x > song_pos * NOTE_WIDTH:
                pygame.draw.polygon(screen, note_colour, shreaded_points)
            # for point in bottom_points:  # debug
            #     pygame.draw.circle(screen, (255, 0, 0), point, 3)

    # if channel_start_note_dict['pitch'][channel_idx] >= len(channel_note_dict['pitch'][channel_idx]) and len(particles) == 0:
    #     global run
    #     run = False  # MINT NOTE: this was made so that the song stops by itself when it's done, it is faulty, but I was too lazy to fix it

    for channel_idx in range(len(channel_note_dict['pitch'])):  # going through all channels and drawing notes with corresponding colour
        for note_idx in range(channel_start_note_dict['pitch'][channel_idx], len(channel_note_dict['pitch'][channel_idx])):
            note = channel_note_dict['pitch'][channel_idx][note_idx]
            # song_pos = get_song_pos_from_bpm_graph(time.time() - start_time, mod_channel_info, FORCED_SONG_TPB) * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])]  # debug
            if channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])] * (note.points[0][0].x - song_pos * NOTE_WIDTH) + CURSOR_OFFSET > SCREEN_SIZE[0]:
                break

            if note_idx - channel_start_note_dict['pitch'][channel_idx] == 0:
                if channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])] * (note.points[len(note.points) - 1][0].x - song_pos * NOTE_WIDTH) + CURSOR_OFFSET < 0:
                    channel_start_note_dict['pitch'][channel_idx] = note_idx + 1

            if len(channel_colour_dict['pitch'][True]) - 1 < channel_idx:  # MINT NOTE: this line had a "possibly bugged" comment, not sure what that means since it's been so long since I touched this code
                note_colour = pygame.Vector3(100, 0, 0)
            else:
                note_colour = pygame.Vector3(channel_colour_dict['pitch'][True][channel_idx])

            note_colour += pygame.Vector3(note.pulse_colour)
            for colour_channel_idx in range(len(note_colour)):
                note_colour[colour_channel_idx] = clamp(note_colour[colour_channel_idx], 0, 255)
            # 0.01 because volume is 0-100  # i have no idea what this means, it's been so long xd
            # 0.5 because half of the note goes up and the other goes down

            note_points = list()
            if note.is_on_cursor:
                # print('og note', note.points, song_pos * NOTE_WIDTH / channel_length_modifier_list[i + len(channel_note_dict['drum'])])  # debug
                for point in note.points:
                    if point[0].x > song_pos * NOTE_WIDTH:
                        if len(note_points) == 0:
                            note_points.append(note.cursor_collision_point)
                        #     print('first')  # debug
                        # print('add', point[0].x)
                        note_points.append(point)
            else:
                note_points = note.points

            # song_pos = get_song_pos_from_bpm_graph(time.time() - start_time, mod_channel_info, FORCED_SONG_TPB) * channel_length_modifier_list[i + len(channel_note_dict['drum'])]
            bottom_points = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])], point[0].y) + pygame.Vector2(0, point[1] * NOTE_WIDTH * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note.points]
            top_points_reversed = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])], point[0].y) - pygame.Vector2(0, point[1] * NOTE_WIDTH * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note.points]
            top_points_reversed.reverse()
            base_points = top_points_reversed
            base_points.extend(bottom_points)

            bottom_shredded_points = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])], point[0].y) + pygame.Vector2(0, point[1] * NOTE_WIDTH * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note_points]
            top_shredded_points_reversed = [pygame.Vector2(point[0].x * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])], point[0].y) - pygame.Vector2(0, point[1] * NOTE_WIDTH * 0.5 * 0.01) - pygame.Vector2(song_pos * channel_length_modifier_list[channel_idx + len(channel_note_dict['drum'])] * NOTE_WIDTH - CURSOR_OFFSET, 0) - scroll for point in note_points]
            top_shredded_points_reversed.reverse()
            shredded_points = top_shredded_points_reversed
            shredded_points.extend(bottom_shredded_points)

            #pygame.draw.lines(screen, note_colour, False, [point[0] - scroll for point in note.points], int(NOTE_WIDTH))
            # drawing base
            if note.pulse_colour > 0:
                pygame.draw.polygon(screen, channel_colour_dict['pitch'][False][channel_idx], base_points)

            if note.points[len(note.points) - 1][0].x > song_pos * NOTE_WIDTH:
                if len(shredded_points) > 2:
                    pygame.draw.polygon(screen, note_colour, shredded_points)

        # for point in bottom_points:
            #     pygame.draw.circle(screen, (255, 0, 0), point, 3)
    # for i in range(len(channel_note_dict['drum'])):
    #     pygame.draw.lines(screen, (255, 255, 255), False, [point[0] for point in note.points], int(DRUM_NOTE_HEIGHT))

    # drawing stuff onto display, remember to offset anything drawn here by 1 down and to the right (pixel display stuff)
    pygame.draw.line(screen, cursor_colour, pygame.Vector2(CURSOR_OFFSET - scroll[0], 0), pygame.Vector2(CURSOR_OFFSET - scroll[0], SCREEN_SIZE[1]), 3)

    for particle in particles:
        particle.draw(display, display_mode=True, scroll=display_scroll)

    draw(pygame.transform.scale(display, dest_display.get_size(), dest_display), screen, display_draw_offset - pygame.Vector2(DISPLAY_TO_SCREEN_RATIO))
    # drawing stuff onto screen in front of display -------------------------------------------------------- #

    for i in range(len(channel_note_dict['pitch'])):  # going through all channels and drawing notes with corresponding colour
        for note in channel_note_dict['pitch'][i]:
            if note.is_on_cursor:
                circle_radius = note.cursor_collision_point[1] * 0.01 * NOTE_WIDTH * 1.2
                #pygame.draw.ellipse(screen, channel_colour_dict['pitch'][True][i], (CURSOR_OFFSET - circle_radius * 0.5 * 0.5, note.cursor_collision_point[0].y - circle_radius * 0.5, circle_radius * 0.5, circle_radius), 5)
                #pygame.draw.ellipse(display, channel_colour_dict['pitch'][True][i], (CURSOR_OFFSET / DISPLAY_TO_SCREEN_RATIO - circle_radius * 0.5 * 0.5 + 1, note.cursor_collision_point[0].y / DISPLAY_TO_SCREEN_RATIO - circle_radius * 0.5 + 1, circle_radius * 0.5, circle_radius), 2)
                #pygame.draw.circle(screen, note_colour, (CURSOR_OFFSET, note.cursor_collision_point[0].y), note.cursor_collision_point[1] * 0.01 * NOTE_WIDTH)
                pygame.draw.rect(screen, (255, 255, 255), (pygame.Vector2(CURSOR_OFFSET + 1, note.cursor_collision_point[0].y + 1) - pygame.Vector2(6, circle_radius) - scroll, (NOTE_WIDTH + 1, circle_radius * 2)))

    # for i in range(len(channel_note_dict['drum'])):  # going through all channels and drawing notes with corresponding colour
    #     for note in channel_note_dict['drum'][i]:
    #         if note.is_on_cursor:
    #             circle_radius = note.cursor_collision_point[1] * 0.01 * DRUM_NOTE_HEIGHT * 1.2
    #             pygame.draw.rect(screen, (255, 255, 255), (pygame.Vector2(CURSOR_OFFSET, note.cursor_collision_point[0].y) - pygame.Vector2((NOTE_WIDTH + 2) / 2, circle_radius), (NOTE_WIDTH + 2, circle_radius * 2)))
    #             circle_radius = note.cursor_collision_point[1] * 0.01 * DRUM_NOTE_HEIGHT * 0.6
    #             #pygame.draw.ellipse(screen, channel_colour_dict['pitch'][True][i], (CURSOR_OFFSET - circle_radius * 0.5 * 0.5, note.cursor_collision_point[0].y - circle_radius * 0.5, circle_radius * 0.5, circle_radius), 5)
    #             #pygame.draw.ellipse(display, channel_colour_dict['pitch'][True][i], (CURSOR_OFFSET / DISPLAY_TO_SCREEN_RATIO - circle_radius * 0.5 * 0.5 + 1, note.cursor_collision_point[0].y / DISPLAY_TO_SCREEN_RATIO - circle_radius * 0.5 + 1, circle_radius * 0.5, circle_radius), 2)
    #             # pygame.draw.circle(screen, (150, 150, 150), (CURSOR_OFFSET, note.cursor_collision_point[0].y), circle_radius, 8)
    #             pygame.draw.rect(screen, channel_colour_dict['drum'][True][i], (pygame.Vector2(CURSOR_OFFSET, note.cursor_collision_point[0].y) - pygame.Vector2(circle_radius), (circle_radius * 2, circle_radius * 2)), 8)

    # screen.blit(white_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # update ------------------------------------------------------------ #
    pygame.display.update()


true_scroll = pygame.Vector2(0)
scroll = true_scroll.copy()

#start_time = time.time()
anim_time = 0
frame_idx = 0

last_time = time.time()
MAX_DT = 3

if not os.path.isdir("./frames"):
    os.makedirs("frames")

# game loop --------------------------------------------------------- #
run = True
while run:
    dt = time.time() - last_time
    dt *= 60
    last_time = time.time()

    dt = min(dt, MAX_DT)

    # handling inputs ------------------------ #
    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: run = False

    # screen shake -------------------------------------------------------------- #
    # directional_screen_shake_anim.advance(dt)
    # directional_screen_shake = directional_screen_shake_anim.get_frame_contents()

    random_screen_shake_anim.advance(dt)
    random_screen_shake = random_screen_shake_anim.get_frame_contents()

    # particles ----------------------------------------- #
    for particle in particles:
        particle.update(dt)
        if particle.life_timer >= particle.LIFE_TIME:
            particles.remove(particle)

    # camera/display offset --------------------------------------------- #
    # DEBUG_CAM_SPEED = 10
    # if input_dict['left']:
    #     true_scroll[0] -= dt * DEBUG_CAM_SPEED
    # if input_dict['right']:
    #     true_scroll[0] += dt * DEBUG_CAM_SPEED

    scroll = true_scroll + random_screen_shake + directional_screen_shake

    display_scroll = pygame.Vector2(math.ceil(scroll[0] / DISPLAY_TO_SCREEN_RATIO),
                                    math.ceil(scroll[1] / DISPLAY_TO_SCREEN_RATIO))

    display_draw_offset = pygame.Vector2(abs(display_scroll[0] - scroll[0] / DISPLAY_TO_SCREEN_RATIO) * DISPLAY_TO_SCREEN_RATIO,
                                         abs(display_scroll[1] - scroll[1] / DISPLAY_TO_SCREEN_RATIO) * DISPLAY_TO_SCREEN_RATIO)

    # white surf ---------------- #
    # if white_surf_colour > 0:
    #     white_surf_colour -= 10 * dt
    # if white_surf_colour < 0:
    #     white_surf_colour = 0
    # white_surf.fill((white_surf_colour, white_surf_colour, white_surf_colour))

    # game logic ------------------------------------------------------------------ #
    song_pos = get_song_pos_from_bpm_graph(anim_time, mod_channel_info, FORCED_SONG_TPB)
    anim_time += 1 / EXPORT_FPS

    for channel_idx in range(len(channel_note_dict['pitch'])):
        for note in channel_note_dict['pitch'][channel_idx]:
            # print(note.points)
            note.is_on_cursor = False
            if note.points[0][0].x < song_pos * NOTE_WIDTH < note.points[len(note.points)-1][0].x:
                note.is_on_cursor = True
                for point_idx in range(len(note.points)):
                    if note.points[point_idx][0].x > song_pos * NOTE_WIDTH:
                        # print(note.points, channel_idx)
                        t = (song_pos * NOTE_WIDTH - note.points[point_idx - 1][0].x) / (note.points[point_idx][0].x - note.points[point_idx - 1][0].x)
                        lerped_note_height = t * (note.points[point_idx][0].y - note.points[point_idx - 1][0].y) + note.points[point_idx - 1][0].y
                        lerped_note_volume = t * (note.points[point_idx][1] - note.points[point_idx - 1][1]) + note.points[point_idx - 1][1]
                        note.cursor_collision_point = [pygame.Vector2(song_pos * NOTE_WIDTH, lerped_note_height), lerped_note_volume]
                        break

                note.particle_timer -= dt
                if note.particle_timer <= 0:
                    particles.append(Particle(60, pygame.Vector2(CURSOR_OFFSET, lerped_note_height) / DISPLAY_TO_SCREEN_RATIO, 0.9, -90, 0, 0, [4 * note.cursor_collision_point[1] * 0.01, 4 * note.cursor_collision_point[1] * 0.01], [0, 0], 255, [255, 255, 255], channel_colour_dict['pitch'][True][channel_idx], [20, 30, 60], "emission colour", [50, 0], [0, 0], [int(note.cursor_collision_point[1] * 0.01 * NOTE_WIDTH * 0.5 / DISPLAY_TO_SCREEN_RATIO), int(note.cursor_collision_point[1] * 0.01 * NOTE_WIDTH * 0.5 / DISPLAY_TO_SCREEN_RATIO)], [0.2, 0.2], [20, 20], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 100], [0, 60], [0, 100], [0, 100], 1, [0, 0], 'none', [0, 0], "square", 100))
                    note.particle_timer = note.PARTICLE_TIME

            if note.pulse_colour == 0:
                if note.points[0][0].x < song_pos * NOTE_WIDTH:
                    note_col = channel_colour_dict['pitch'][True][channel_idx]
                    note.pulse_colour = 255 - min(note_col)
                    if str(channel_idx) in kick_channel_idx:
                        random_screen_shake_anim = get_randomized_screen_shake_anim(kick_channel_idx[str(channel_idx)], 4, 0)
                        # directional_screen_shake_anim = get_directional_screen_shake_anim(180, 2, 20)
                        # random_screen_shake_anim.is_playing = True
            else:
                if note.pulse_colour > 1:
                    note.pulse_colour -= dt * 3  # decay speed
                if note.pulse_colour < 1:
                    note.pulse_colour = 1

    for channel_idx in range(len(channel_note_dict['drum'])):
        for note in channel_note_dict['drum'][channel_idx]:
            # print(note.points)
            note.is_on_cursor = False
            if note.points[0][0].x < song_pos * NOTE_WIDTH < note.points[len(note.points)-1][0].x:
                note.is_on_cursor = True
                for point_idx in range(len(note.points)):
                    if note.points[point_idx][0].x > song_pos * NOTE_WIDTH:
                        # print(note.points, channel_idx)
                        t = (song_pos * NOTE_WIDTH - note.points[point_idx - 1][0].x) / (note.points[point_idx][0].x - note.points[point_idx - 1][0].x)
                        lerped_note_height = t * (note.points[point_idx][0].y - note.points[point_idx - 1][0].y) + note.points[point_idx - 1][0].y
                        lerped_note_volume = t * (note.points[point_idx][1] - note.points[point_idx - 1][1]) + note.points[point_idx - 1][1]
                        note.cursor_collision_point = [pygame.Vector2(song_pos * NOTE_WIDTH, lerped_note_height), lerped_note_volume]
                        break

                note.particle_timer -= dt
                if note.particle_timer <= 0:
                    for i in range(4):
                        particles.append(Particle(60, pygame.Vector2(CURSOR_OFFSET, lerped_note_height) / DISPLAY_TO_SCREEN_RATIO, 0.9, -90, 0, 0, [8 * note.cursor_collision_point[1] * 0.01, 8 * note.cursor_collision_point[1] * 0.01], [0, 0], 255, [255, 255, 255], channel_colour_dict['drum'][True][channel_idx], [20, 30, 60], "emission colour", [50, 0], [0, 0], [int(note.cursor_collision_point[1] * 0.01 * DRUM_NOTE_HEIGHT * 0.5 / DISPLAY_TO_SCREEN_RATIO), int(note.cursor_collision_point[1] * 0.01 * DRUM_NOTE_HEIGHT * 0.5 / DISPLAY_TO_SCREEN_RATIO)], [0.2, 0.2], [20, 20], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 100], [0, 60], [0, 100], [0, 100], 1, [0, 0], 'none', [0, 0], "square", 100))
                    note.particle_timer = note.PARTICLE_TIME

            if note.pulse_colour == 0:
                if note.points[0][0].x < song_pos * NOTE_WIDTH:
                    note_col = channel_colour_dict['drum'][True][channel_idx]
                    note.pulse_colour = 255 - min(note_col)
                    if channel_idx == snare_drum_channel_idx:
                        white_surf_colour = 100
            else:
                if note.pulse_colour > 1:
                    note.pulse_colour -= dt * 3  # decay speed
                if note.pulse_colour < 1:
                    note.pulse_colour = 1

    # update ------------------------------------------------------------ #
    drawing()
    pygame.image.save(screen, 'frames/' + str(frame_idx) + '.png')
    frame_idx += 1

    clock.tick(EXPORT_FPS)

pygame.quit()
