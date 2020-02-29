"""Miscellaneous utility functions."""

from functools import reduce

from PIL import Image
import numpy as np
import cv2
from collections import deque
import itertools


def compose(*funcs):
    """Compose arbitrarily many functions, evaluated left to right.
    Reference: https://mathieularose.com/function-composition-in-python/
    """
    # return lambda x: reduce(lambda v, f: f(v), funcs, x)
    if funcs:
        return reduce(lambda f, g: lambda *a, **kw: g(f(*a, **kw)), funcs)
    else:
        raise ValueError('Composition of empty sequence not supported.')


def letterbox_image(image, size):
    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)

    image = image.resize((nw, nh), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128, 128, 128))
    new_image.paste(image, ((w-nw)//2, (h-nh)//2))
    return new_image


def calc_distance(point_one, point_two):
    x_axis = (point_one[0] + point_two[0])**2
    y_axis = (point_one[1] + point_two[1]) ** 2
    return abs(x_axis - y_axis)**0.5


def check_bridge(buffer):
    counter = 0
    ready = False

    output_list = []
    for index, frame in enumerate(buffer):
        if len(frame[0]) > 0 and not ready:
            ready = True
        if len(frame[0]) <= 0 and ready:
            counter += 1
        if len(frame[0]) > 0:
            if 0 < counter <= 3:
                output_list.append([index - 1, counter])
            counter = 0

    return output_list


def blur_img(bboxs, img):
    for bbox in bboxs:
        bbs = np.array(bbox[:4], dtype=np.int32)
        frame_rio = img[bbs[0]: bbs[2], bbs[1]: bbs[3]]
        img[bbs[0]: bbs[2], bbs[1]: bbs[3]] = cv2.GaussianBlur(
            frame_rio, (0, 0), cv2.BORDER_DEFAULT)
    return img


def fill_bridges(bridge_buffer):
    bridges = check_bridge(bridge_buffer)
    changes = False

    for cc in bridges:
        index, counter = cc
        start = index - counter + 1
        print(len(bridge_buffer[start - 1][0]))
        print(len(bridge_buffer[index + 1][0]))
        for left_bb in bridge_buffer[start - 1][0]:
            for right_bb in bridge_buffer[index + 1][0]:
                if calc_distance(left_bb, right_bb) <= 1500:
                    distances = []

                    for i in range(4):
                        dist = (
                            right_bb[i] - left_bb[i]) / (counter + 1)
                        distances.append(dist)

                    for i in range(counter):
                        buffer_cords = []

                        for j in range(4):
                            buffer_cords.append(
                                bridge_buffer[start - 1][0][0][j] + distances[j])

                        bridge_buffer[start + i][0].append(buffer_cords)
                        changes = True

        if changes:
            changes = False
            for i in range(counter):
                bridge_buffer[start + i][1] = blur_img(
                    bridge_buffer[start + i][0], bridge_buffer[start + i][1])

    return bridge_buffer
