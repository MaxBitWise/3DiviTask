import os
import sys
import numpy as np
import math
from enum import Enum
# dimensions of result image
W = 1200
H = 900
CHANNEL_NUM = 3  # we work with rgb images
MAX_VALUE = 255  # max pixel value, required by ppm header


class ChosenSide(Enum):
    RIGHT = 0
    LEFT = 2
    UP = 1
    DOWN = 3


class CompareSide(Enum):
    RIGHT = 2
    LEFT = 0
    UP = 3
    DOWN = 1


def read_image(path):
    # second line of header contains image dimensions
    w, h = np.loadtxt(path, skiprows=1, max_rows=1, dtype=np.int32)
    # skip 3 lines reserved for header and read image
    image = np.loadtxt(path, skiprows=3, dtype=np.uint8).reshape((h, w, CHANNEL_NUM))
    return image


def find_dest(chosen_pixel, compare_pixel):
    division_pixel = ((float(compare_pixel[0]) - float(chosen_pixel[0]))**2 +
                      (float(compare_pixel[1]) - float(chosen_pixel[1]))**2 +
                      (float(compare_pixel[2]) - float(chosen_pixel[2]))**2) ** 0.5
    return division_pixel



def write_image(path, img):
    h, w = img.shape[:2]
    # ppm format requires header in special format
    header = f'P3\n{w} {h}\n{MAX_VALUE}\n'
    with open(path, 'w') as f:
        f.write(header)
        for r, g, b in img.reshape((-1, CHANNEL_NUM)):
            f.write(f'{r} {g} {b} ')


def find_neighbours(path):
    tiles = [read_image(os.path.join(path, t)) for t in sorted(os.listdir(path))]
    tiles_counts = len(tiles)
    tile_mathches = []
    h, w = tiles[0].shape[:2]
    tiles_sides = [
                   {"x1": [w-1], "y1": [i for i in range(h)],
                    "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(0), CompareSide(0)]},
                   {"x1": [w-1], "y1": [i for i in range(h)],
                    "x2": [i for i in range(w)], "y2": [h-1], "sides": [ChosenSide(0), CompareSide(1)]},
                   {"x1": [w-1], "y1": [i for i in range(h)],
                    "x2": [w-1], "y2": [i for i in range(h-1, 0, -1)], "sides": [ChosenSide(0), CompareSide(2)]},
                   {"x1": [w-1], "y1": [i for i in range(h)],
                    "x2": [i for i in range(w-1, 0, -1)], "y2": [0], "sides": [ChosenSide(0), CompareSide(3)]},

                   {"x1": [i for i in range(w)], "y1": [0],
                    "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(1), CompareSide(0)]},
                   {"x1": [i for i in range(w)], "y1": [0],
                    "x2": [i for i in range(w)], "y2": [h - 1], "sides": [ChosenSide(1), CompareSide(1)]},
                   {"x1": [i for i in range(w)], "y1": [0],
                    "x2": [w - 1], "y2": [i for i in range(h-1, 0, -1)], "sides": [ChosenSide(1), CompareSide(2)]},
                   {"x1": [i for i in range(w)], "y1": [0],
                    "x2": [i for i in range(w-1, 0, -1)], "y2": [0], "sides": [ChosenSide(1), CompareSide(3)]},

                   {"x1": [0], "y1": [i for i in range(h-1, 0, -1)],
                    "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(2), CompareSide(0)]},
                   {"x1": [0], "y1": [i for i in range(h-1, 0, -1)],
                    "x2": [i for i in range(w)], "y2": [h - 1], "sides": [ChosenSide(2), CompareSide(1)]},
                   {"x1": [0], "y1": [i for i in range(h-1, 0, -1)],
                    "x2": [w - 1], "y2": [i for i in range(h-1, 0, -1)], "sides": [ChosenSide(2), CompareSide(2)]},
                   {"x1": [0], "y1": [i for i in range(h-1, 0, -1)],
                    "x2": [i for i in range(w-1, 0, -1)], "y2": [0], "sides": [ChosenSide(2), CompareSide(3)]},

                   {"x1": [i for i in range(w-1, 0, -1)], "y1": [h - 1],
                    "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(3), CompareSide(0)]},
                   {"x1": [i for i in range(w-1, 0, -1)], "y1": [h - 1],
                    "x2": [i for i in range(w)], "y2": [h - 1], "sides": [ChosenSide(3), CompareSide(1)]},
                   {"x1": [i for i in range(w-1, 0, -1)], "y1": [h - 1],
                    "x2": [w - 1], "y2": [i for i in range(h-1, 0, -1)], "sides": [ChosenSide(3), CompareSide(2)]},
                   {"x1": [i for i in range(w-1, 0, -1)], "y1": [h - 1],
                    "x2": [i for i in range(w-1, 0, -1)], "y2": [0], "sides": [ChosenSide(3), CompareSide(3)]},
                   ]
    for chosen_tile_index in range(tiles_counts):
        for compare_tile_index in range(tiles_counts):
            if chosen_tile_index == compare_tile_index:
                continue
            is_continue = True
            for j in range(len(tile_mathches)):
                if [compare_tile_index, chosen_tile_index] == tile_mathches[j][0]:
                    is_continue = False
            if not is_continue:
                continue

            for i in range(len(tiles_sides)):
                chosen_tile_x = tiles_sides[i]["x1"]
                chosen_tile_y = tiles_sides[i]["y1"]
                compare_tile_x = tiles_sides[i]["x2"]
                compare_tile_y = tiles_sides[i]["y2"]
                chosen_tile_x_index = 0
                chosen_tile_y_index = 0
                compare_tile_x_index = 0
                compare_tile_y_index = 0
                division_pixel = 0
                while chosen_tile_y_index < len(chosen_tile_y)-1 or compare_tile_y_index < len(compare_tile_y)-1 \
                        or chosen_tile_x_index < len(chosen_tile_x)-1 or compare_tile_x_index < len(compare_tile_x)-1:
                    division_pixel += find_dest(tiles[chosen_tile_index][chosen_tile_y[chosen_tile_y_index]]
                                                     [chosen_tile_x[chosen_tile_x_index]],
                                                tiles[compare_tile_index][compare_tile_y[compare_tile_y_index]]
                                                     [compare_tile_x[compare_tile_x_index]])

                    if chosen_tile_y_index < len(chosen_tile_y)-1:
                        chosen_tile_y_index += 1
                    if compare_tile_y_index < len(compare_tile_y)-1:
                        compare_tile_y_index += 1
                    if chosen_tile_x_index < len(chosen_tile_x)-1:
                        chosen_tile_x_index += 1
                    if compare_tile_x_index < len(compare_tile_x)-1:
                        compare_tile_x_index += 1
                avg_division_pixel = division_pixel / (h)
                if avg_division_pixel < 60:
                    tile_mathches.append([[chosen_tile_index, compare_tile_index], {"sides": tiles_sides[i]["sides"]}])
                    break

    return tile_mathches


if __name__ == "__main__":
    for i in find_neighbours("G:\\PycharmProjects\\data\\data\\0000_0000_0000\\tiles"):
        print(i)
    # img1 = np.rot90(img1)
    # img2 = read_image("G:\\PycharmProjects\\data\\data\\0000_0000_0000\\tiles\\0006.ppm")
    # h, w = img1.shape[:2]
    # tiles_sides = [
    #     {"x1": [w - 1], "y1": [i for i in range(h)],
    #      "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(0), CompareSide(0)]},
    #     {"x1": [w - 1], "y1": [i for i in range(h)],
    #      "x2": [i for i in range(w)], "y2": [h - 1], "sides": [ChosenSide(0), CompareSide(1)]},
    #     {"x1": [w - 1], "y1": [i for i in range(h)],
    #      "x2": [w - 1], "y2": [i for i in range(h - 1, 0, -1)], "sides": [ChosenSide(0), CompareSide(2)]},
    #     {"x1": [w - 1], "y1": [i for i in range(h)],
    #      "x2": [i for i in range(w - 1, 0, -1)], "y2": [0], "sides": [ChosenSide(0), CompareSide(3)]},
    #
    #     {"x1": [i for i in range(w)], "y1": [0],
    #      "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(1), CompareSide(0)]},
    #     {"x1": [i for i in range(w)], "y1": [0],
    #      "x2": [i for i in range(w)], "y2": [h - 1], "sides": [ChosenSide(1), CompareSide(1)]},
    #     {"x1": [i for i in range(w)], "y1": [0],
    #      "x2": [w - 1], "y2": [i for i in range(h - 1, 0, -1)], "sides": [ChosenSide(1), CompareSide(2)]},
    #     {"x1": [i for i in range(w)], "y1": [0],
    #      "x2": [i for i in range(w - 1, 0, -1)], "y2": [0], "sides": [ChosenSide(1), CompareSide(3)]},
    #
    #     {"x1": [0], "y1": [i for i in range(h - 1, 0, -1)],
    #      "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(2), CompareSide(0)]},
    #     {"x1": [0], "y1": [i for i in range(h - 1, 0, -1)],
    #      "x2": [i for i in range(w)], "y2": [h - 1], "sides": [ChosenSide(2), CompareSide(1)]},
    #     {"x1": [0], "y1": [i for i in range(h - 1, 0, -1)],
    #      "x2": [w - 1], "y2": [i for i in range(h - 1, 0, -1)], "sides": [ChosenSide(2), CompareSide(2)]},
    #     {"x1": [0], "y1": [i for i in range(h - 1, 0, -1)],
    #      "x2": [i for i in range(w - 1, 0, -1)], "y2": [0], "sides": [ChosenSide(2), CompareSide(3)]},
    #
    #     {"x1": [i for i in range(w - 1, 0, -1)], "y1": [h - 1],
    #      "x2": [0], "y2": [i for i in range(h)], "sides": [ChosenSide(3), CompareSide(0)]},
    #     {"x1": [i for i in range(w - 1, 0, -1)], "y1": [h - 1],
    #      "x2": [i for i in range(w)], "y2": [h - 1], "sides": [ChosenSide(3), CompareSide(1)]},
    #     {"x1": [i for i in range(w - 1, 0, -1)], "y1": [h - 1],
    #      "x2": [w - 1], "y2": [i for i in range(h - 1, 0, -1)], "sides": [ChosenSide(3), CompareSide(2)]},
    #     {"x1": [i for i in range(w - 1, 0, -1)], "y1": [h - 1],
    #      "x2": [i for i in range(w - 1, 0, -1)], "y2": [0], "sides": [ChosenSide(3), CompareSide(3)]},
    # ]
    #
    # chosen_tile_x = tiles_sides[0]["x1"]
    # chosen_tile_y = tiles_sides[0]["y1"]
    # compare_tile_x = tiles_sides[0]["x2"]
    # compare_tile_y = tiles_sides[0]["y2"]
    # chosen_tile_x_index = 0
    # chosen_tile_y_index = 0
    # compare_tile_x_index = 0
    # compare_tile_y_index = 0
    # division_pixel = 0
    # while chosen_tile_y_index < len(chosen_tile_y) - 1 or compare_tile_y_index < len(compare_tile_y) - 1 \
    #         or chosen_tile_x_index < len(chosen_tile_x) - 1 or compare_tile_x_index < len(compare_tile_x) - 1:
    #     division_pixel += find_dest(img1[chosen_tile_y[chosen_tile_y_index]]
    #                                 [chosen_tile_x[chosen_tile_x_index]],
    #                                 img2[compare_tile_y[compare_tile_y_index]]
    #                                 [compare_tile_x[compare_tile_x_index]])
    #
    #     if chosen_tile_y_index < len(chosen_tile_y) - 1:
    #         chosen_tile_y_index += 1
    #     if compare_tile_y_index < len(compare_tile_y) - 1:
    #         compare_tile_y_index += 1
    #     if chosen_tile_x_index < len(chosen_tile_x) - 1:
    #         chosen_tile_x_index += 1
    #     if compare_tile_x_index < len(compare_tile_x) - 1:
    #         compare_tile_x_index += 1
    # avg_division_pixel = division_pixel / (h)
    # print(avg_division_pixel)

