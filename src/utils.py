import cv2
import pickle
import os
import numpy as np

import algos
import homologies


ORIG_SIZE = 424
CROP_SIZE = 210
RES_SIZE = 70
CUT_MARGIN = (ORIG_SIZE - CROP_SIZE) // 2
ORIGIN = (RES_SIZE // 2, RES_SIZE // 2)


def load_image(name, greyscale=True):
  image = cv2.imread(name)
  image_cropped = image[CUT_MARGIN:-CUT_MARGIN, CUT_MARGIN:-CUT_MARGIN]
  image_resized = cv2.resize(image_cropped, (RES_SIZE, RES_SIZE), interpolation=cv2.INTER_AREA)
  if not greyscale:
    return image_resized
  image_greyscale = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
  return image_greyscale


def pixels_at_least(image, threshold): # more readable then cv2.threshold
  res = np.zeros_like(image, dtype=int)
  for ix, val in np.ndenumerate(image):
    if val >= threshold:
      res[ix] = 1
  return res


def extract_galaxy(image, threshold):
  res = np.copy(image)
  arr = pixels_at_least(image, threshold)
  visited = np.zeros_like(image, dtype=int)
  algos.bfs(ORIGIN, arr, visited)
  for ix, val in np.ndenumerate(visited):
    if val == 0:
      res[ix] = 0
  return res


def distance(p1, p2):
  return np.linalg.norm(np.array(p1) - np.array(p2))


def make_generic_map(image, function):
  res = np.zeros_like(image, dtype=float)
  for ix, val in np.ndenumerate(image):
    if val > 0:
       res[ix] = function(ix, val)
  return res


def make_radial_map(image):
  def fun(ix, _):
    return distance(ORIGIN, ix)
  return make_generic_map(image, fun)


def make_coord_map(image, coord=0):
  def fun(ix, _):
    return ix[coord]
  return make_generic_map(image, fun)


def make_brightness_map(image):
  def fun(_, val):
    return val
  return make_generic_map(image, fun)


def create_poset(min_value, max_value, length):
  assert(min_value < max_value)
  assert(length > 1)
  step = (max_value - min_value) / (length - 1)
  return [min_value + i * step for i in range(length)]


def get_diagram(image, poset):
  ranks = homologies.get_ranks(image, poset)
  n = len(poset)
  diagram = np.zeros((n, n), dtype=int)
  
  for i in range(0, n):
    for j in range(i + 1, n):
      diagram[i,j] = ranks[i,j-1] - ranks[i,j]
      if i > 0:
        diagram[i,j] += ranks[i-1,j] - ranks[i-1,j-1]

  return diagram


def write_diagram(diag, poset, _per_type, output_file):
  pickle.dump((diag, poset), open(output_file, "wb"))


def read_diagram(input_file):
  diag, _ = pickle.load(open(input_file, "rb"))
  return diag


def get_bname(path):
  return os.path.splitext(os.path.basename(path))[0]


def get_class(diag_name):
  bname = get_bname(diag_name)
  return int(bname.split('_')[1])
