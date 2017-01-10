import argparse
import glob
import utils
from matplotlib import pyplot as plt

import bottleneck

HEAD_NUM = 10

def get_args():
  parser = argparse.ArgumentParser(description='Find closest persistence diagram')
  parser.add_argument('--galaxy-diag', dest='galaxy_diag', default='train/diags/galaxy.p')
  parser.add_argument('--diagrams-dir', dest='diag_dir', default='train/diags/')
  parser.add_argument('--secondary-diagrams-dir', dest='sec_diag_dir', default=None)
  parser.add_argument('--images-dir', dest='img_dir', default='train/img/')
  parser.add_argument('--show-figures', dest='show', action='store_true')
  parser.add_argument('--threshold', dest='threshold', type=int, default=40)
  parser.add_argument('--ignore-near-diag', dest='ignore_near_diag', action='store_true')

  return parser.parse_args()


def get_sorted_candidates(galaxy_diag, diag_dir, exclude_target=True, ignore_near_diag=False,
                          sec_diag_dir=None):
  target_diag = utils.read_diagram(galaxy_diag)
 
  candidates = []

  for fname in glob.glob('{}/*.p'.format(diag_dir)):
    if not exclude_target or utils.get_bname(fname) != utils.get_bname(galaxy_diag):
      other_diag = utils.read_diagram(fname)
      dist = bottleneck.get_distance(target_diag, other_diag, ignore_near_diag=ignore_near_diag)
      if sec_diag_dir:
        sec_fname = '{}/{}.p'.format(sec_diag_dir, utils.get_bname(fname))
        sec_other_diag = utils.read_diagram(sec_fname)
        dist += bottleneck.get_distance(target_diag, sec_other_diag,
                                        ignore_near_diag=ignore_near_diag)

      candidates += [(dist, fname)]
  
  candidates.sort()
  return candidates


if __name__ == '__main__':
  args = get_args()

  print(args.galaxy_diag)
  candidates = get_sorted_candidates(args.galaxy_diag, args.diag_dir,
                                     ignore_near_diag=args.ignore_near_diag,
                                     sec_diag_dir=args.sec_diag_dir)

  for dist, name in candidates[:HEAD_NUM]:
    print(dist, name)

  if args.show:
    for path in (args.galaxy_diag, candidates[0][1]):
      bname = utils.get_bname(path)
      fname = "{}/{}.jpg".format(args.img_dir, bname)
      diag_fname = "{}/{}.p".format(args.diag_dir, bname)
      print(fname)
      img = utils.load_image(fname, greyscale=False)
      img_gr = utils.load_image(fname, greyscale=True)
      img_map = utils.extract_galaxy(img_gr, args.threshold)
      plt.figure()
      plt.imshow(img)
      plt.figure()
      plt.imshow(img_map)
      diag = utils.read_diagram(diag_fname)
      print(diag)
    plt.show()
