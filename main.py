import os
import sys
import numpy as np
import math
# dimensions of result image
W = 1200
H = 900
CHANNEL_NUM = 3  # we work with rgb images
MAX_VALUE = 255  # max pixel value, required by ppm header

MATHCING = []

def read_image(path):
    # second line of header contains image dimensions
    w, h = np.loadtxt(path, skiprows=1, max_rows=1, dtype=np.int32)
    # skip 3 lines reserved for header and read image
    image = np.loadtxt(path, skiprows=3, dtype=np.uint8).reshape((h, w, CHANNEL_NUM))
    return image


def write_image(path, img):
    h, w = img.shape[:2]
    # ppm format requires header in special format
    header = f'P3\n{w} {h}\n{MAX_VALUE}\n'
    with open(path, 'w') as f:
        f.write(header)
        for r, g, b in img.reshape((-1, CHANNEL_NUM)):
            f.write(f'{r} {g} {b} ')


# def solve_puzzle(tiles_folder):
#     # create placeholder for result image
#     # read all tiles in list
#     tiles = [read_image(os.path.join(tiles_folder, t)) for t in sorted(os.listdir(tiles_folder))]
#     result_img = np.zeros((H, W, CHANNEL_NUM), dtype=np.uint8)
#     # scan dimensions of all tiles and find minimal height and width
#     dims = np.array([t.shape[:2] for t in tiles])
#     h, w = np.min(dims, axis=0)
#     # compute grid that will cover image
#     # spacing between grid rows = min h
#     # spacing between grid columns = min w
#     x_nodes = np.arange(0, W, w)
#     y_nodes = np.arange(0, H, h)
#     xx, yy = np.meshgrid(x_nodes, y_nodes)
#     nodes = np.vstack((xx.flatten(), yy.flatten())).T
#     # fill grid with tiles
#     for (x, y), tile in zip(nodes, tiles):
#         result_img[y: y + h, x: x + w] = tile[:h, :w]
#
#     output_path = "image.ppm"
#     write_image(output_path, result_img)


def solve_puzzle(tiles_folder):
    tiles = [read_image(os.path.join(tiles_folder, t)) for t in sorted(os.listdir(tiles_folder))]
    tiles_counts = len(tiles)
    while tiles_counts != 5:
        tile_num = 0
        while tile_num < tiles_counts:
            for compare_tile_index in range(len(tiles)):
                is_concatenated = False
                if compare_tile_index == tile_num:
                    continue
                if tiles[compare_tile_index].shape[0] != tiles[tile_num].shape[0] \
                        and tiles[compare_tile_index].shape[1] != tiles[tile_num].shape[1]:
                    continue
                for i in range(4):
                    for j in range(4):
                        avg_division_pixel = 0
                        red = 0
                        green = 0
                        blue = 0
                        x = tiles[tile_num].shape[1]-1
                        for y in range(tiles[tile_num].shape[0]-1):
                            red += math.fabs(int(tiles[tile_num][y][x][0]) - int(tiles[compare_tile_index][y][0][0]))
                            green += math.fabs(int(tiles[tile_num][y][x][1]) - int(tiles[compare_tile_index][y][0][1]))
                            blue += math.fabs(int(tiles[tile_num][y][x][2]) - int(tiles[compare_tile_index][y][0][2]))
                        avg_division_pixel = (red + green + blue) / (3*tiles[tile_num].shape[0]-1)
                        if avg_division_pixel < 20:
                            if tiles[tile_num].shape[1] + tiles[compare_tile_index].shape[1] <= W and \
                                    tiles[tile_num].shape[0] + tiles[compare_tile_index].shape[0] <= H:
                                tiles[tile_num] = np.concatenate((tiles[tile_num], tiles[compare_tile_index]), axis=1)
                                del tiles[compare_tile_index]
                                is_concatenated = True
                                print("match")
                                if [compare_tile_index, tile_num] not in MATHCING:
                                    MATHCING.append([tile_num, compare_tile_index])
                                break
                        else:
                            tiles[tile_num] = np.rot90(tiles[tile_num])
                            if tiles[compare_tile_index].shape[0] != tiles[tile_num].shape[0] or \
                                    tiles[compare_tile_index].shape[1] \
                                    != tiles[tile_num].shape[1]:
                                tiles[tile_num] = np.rot90(tiles[tile_num])
                    if not is_concatenated:
                        tiles[compare_tile_index] = np.rot90(tiles[compare_tile_index])
                        if tiles[compare_tile_index].shape[0] != tiles[tile_num].shape[0] or \
                                tiles[compare_tile_index].shape[1] \
                                != tiles[tile_num].shape[1]:
                            tiles[compare_tile_index] = np.rot90(tiles[compare_tile_index])

                    else:
                        break
                if is_concatenated:
                    break
            tile_num += 1
            tiles_counts = len(tiles)

    write_image("G:\\PycharmProjects\\3DiviTask\\test.ppm", tiles[0])
    write_image("G:\\PycharmProjects\\3DiviTask\\test1.ppm", tiles[1])
    write_image("G:\\PycharmProjects\\3DiviTask\\test2.ppm", tiles[2])
    write_image("G:\\PycharmProjects\\3DiviTask\\test3.ppm", tiles[3])
    write_image("G:\\PycharmProjects\\3DiviTask\\test4.ppm", tiles[4])





if __name__ == "__main__":
    solve_puzzle("G:\\PycharmProjects\\data\\data\\0000_0000_0000\\tiles")
    # img = read_image("G:\\PycharmProjects\\3DiviTask\\test5.ppm")
    # img1 = read_image("G:\\PycharmProjects\\3DiviTask\\test4.ppm")
    # img3 = np.concatenate((img[:, 0:600, :], img1), axis=0)
    #
    # write_image("G:\\PycharmProjects\\3DiviTask\\img3.ppm", img3)

    print(MATHCING)