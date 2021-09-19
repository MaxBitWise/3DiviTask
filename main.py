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
    division_pixel = math.sqrt((int(chosen_pixel[0]) - int(compare_pixel[0]))**2 +
                               (int(chosen_pixel[1]) - int(compare_pixel[1]))**2 +
                               (int(chosen_pixel[2]) - int(compare_pixel[2]))**2)
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
    for chosen_tile_index in range(tiles_counts):
        for compare_tile_index in range(tiles_counts):
            if chosen_tile_index == compare_tile_index:
                continue
            for side_chosen_tile in range(4):
                for side_compare_tile in range(4):
                    division_pixel = 0
                    x = tiles[chosen_tile_index].shape[1] - 1
                    for y in range(tiles[chosen_tile_index].shape[0]):
                        division_pixel += find_dest(tiles[chosen_tile_index][y][x], tiles[compare_tile_index][y][0])
                    avg_division_pixel = division_pixel / (3 * tiles[chosen_tile_index].shape[0] - 1)
                    if avg_division_pixel < 15:
                        tile_mathches.append({"compare tiles": [chosen_tile_index, compare_tile_index],
                                              "sides": [ChosenSide(side_chosen_tile), CompareSide(side_compare_tile)]})
                    tiles[compare_tile_index] = np.rot90(tiles[compare_tile_index])
                    # if side_compare_tile == 3:
                    #     tiles[compare_tile_index] = np.rot90(tiles[compare_tile_index])
                tiles[side_chosen_tile] = np.rot90(tiles[side_chosen_tile])
    return tile_mathches


if __name__ == "__main__":
    tes = find_neighbours("G:\\PycharmProjects\\data\\data\\0000_0000_0000\\tiles")
    for i in range(len(tes)):
        print(tes[0])
