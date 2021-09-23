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
                avg_division_pixel = division_pixel / h
                if avg_division_pixel < 50:

                    tile_mathches.append([[chosen_tile_index, compare_tile_index], {"sides": tiles_sides[i]["sides"]},
                                          {"avg_dest": avg_division_pixel}])
                    break

    return tile_mathches


def tile_concat(tile_matches):
    tiles = np.zeros((3, 4, 2))
    index = 0
    for i in range(tiles.shape[0]):
        for j in range(tiles.shape[1]):
            tiles[i][j][0] = index
            index += 1

    for tile_match in tile_matches:
        for i in range(tiles.shape[0]):
            for j in range(tiles.shape[1]):
                if tiles[i][j][0] == tile_match[0][0]:
                    for k in range(tiles.shape[0]):
                        for z in range(tiles.shape[1]):
                            if tiles[k][z][0] == tile_match[0][1]:
                                side = tile_match[1]["sides"][0].value + tiles[i][j][1]
                                if side >= 4:
                                    side = side - 4
                                if ChosenSide(side) == ChosenSide.RIGHT:
                                    if j < tiles.shape[1]-1:
                                        tmp = np.copy(tiles[i][j+1])
                                        tiles[i][j+1] = np.copy(tiles[k][z])
                                        tiles[k][z] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j + 1][1] = rotates
                                    else:
                                        tiles = shift_left(tiles)
                                        tmp = np.copy(tiles[i][j])
                                        if z-1 >= 0:
                                            tiles[i][j] = np.copy(tiles[k][z-1])
                                            tiles[k][z-1] = np.copy(tmp)
                                        else:
                                            tiles[i][j] = np.copy(tiles[k][tiles.shape[1]-1])
                                            tiles[k][tiles.shape[1]-1] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j][1] = rotates
                                if ChosenSide(side) == ChosenSide.LEFT:
                                    if j > 0:
                                        tmp = np.copy(tiles[i][j-1])
                                        tiles[i][j-1] = np.copy(tiles[k][z])
                                        tiles[k][z] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j-1][1] = rotates
                                    else:
                                        tiles = shift_right(tiles)
                                        tmp = np.copy(tiles[i][j])
                                        if z+1 <= tiles.shape[1]:
                                            tiles[i][j] = np.copy(tiles[k][z+1])
                                            tiles[k][z+1] = np.copy(tmp)
                                        else:
                                            tiles[i][j] = np.copy(tiles[k][0])
                                            tiles[k][0] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j][1] = rotates
                                if ChosenSide(side) == ChosenSide.UP:
                                    if i > 0:
                                        tmp = np.copy(tiles[i-1][j])
                                        tiles[i-1][j] = np.copy(tiles[k][z])
                                        tiles[k][z] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j][1] = rotates
                                    else:
                                        tiles = shift_down(tiles)
                                        tmp = np.copy(tiles[i][j])
                                        if k+1 <= tiles.shape[0]:
                                            tiles[i][j] = np.copy(tiles[k][z])
                                            tiles[k][z] = np.copy(tmp)
                                        else:
                                            tiles[i][j] = np.copy(tiles[0][z])
                                            tiles[0][z] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j][1] = rotates
                                if ChosenSide(side) == ChosenSide.DOWN:
                                    if i < tiles.shape[0]-1:
                                        tmp = np.copy(tiles[i+1][j])
                                        tiles[i+1][j] = np.copy(tiles[k][z])
                                        tiles[k][z] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j][1] = rotates
                                    else:
                                        tiles = shift_up(tiles)
                                        tmp = np.copy(tiles[i][j])
                                        if k-1 >= 0:
                                            tiles[i][j] = np.copy(tiles[k][z])
                                            tiles[k][z] = np.copy(tmp)
                                        else:
                                            tiles[i][j] = np.copy(tiles[tiles.shape[0]-1][z])
                                            tiles[tiles.shape[0]-1][z] = np.copy(tmp)
                                        rotates = (tile_match[1]["sides"][1].value - ChosenSide(side).value + 4) % 4
                                        tiles[i][j][1] = rotates
    return tiles


def shift_right(arr):
    arr = np.roll(arr, 1, axis=1)
    return arr


def shift_left(arr):
    arr = np.roll(arr, -1, axis=1)
    return arr


def shift_up(arr):
    arr = np.roll(arr, -1, axis=0)
    return arr


def shift_down(arr):
    arr = np.roll(arr, 1, axis=0)
    return arr


def solve_puzzle(tiles_folder):
    # create placeholder for result image
    # read all tiles in list
    tiles = [read_image(os.path.join(tiles_folder, t)) for t in sorted(os.listdir(tiles_folder))]
    result_img = np.zeros((H, W, CHANNEL_NUM), dtype=np.uint8)
    # scan dimensions of all tiles and find minimal height and width
    dims = np.array([t.shape[:2] for t in tiles])
    h, w = np.min(dims, axis=0)
    # compute grid that will cover image
    # spacing between grid rows = min h
    # spacing between grid columns = min w
    x_nodes = np.arange(0, W, w)
    y_nodes = np.arange(0, H, h)
    xx, yy = np.meshgrid(x_nodes, y_nodes)
    nodes = np.vstack((xx.flatten(), yy.flatten())).T
    # fill grid with tiles
    right_tiles = tile_concat(find_neighbours(tiles_folder)).reshape(1,12,2)
    index = 0
    for (x, y), tile in zip(nodes, tiles):
        i = int(right_tiles[0][index][0])
        tile = np.rot90(tiles[i], int(right_tiles[0][index][1]))
        result_img[y: y + h, x: x + w] = tile[:h, :w]
        index += 1
    output_path = "image.ppm"
    write_image(output_path, result_img)


if __name__ == "__main__":
    # print(tile_concat(find_neighbours("G:\\PycharmProjects\\data\\data\\0000_0000_0000\\tiles")))
    solve_puzzle("G:\\PycharmProjects\\data\\data\\0000_0000_0000\\tiles")
# [[[ 5.  3.]
#   [11.  2.]
#   [ 3.  2.]
#   [10.  0.]
#   [ 1.  3.]
#   [ 7.  1.]
#   [ 0.  1.]
#   [ 9.  1.]
#   [ 6.  2.]
#   [ 8.  2.]
#   [ 4.  1.]
#   [ 2.  2.]]]