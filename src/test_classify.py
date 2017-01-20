import argparse
import glob

import utils
import knn

def get_args():
  parser = argparse.ArgumentParser(description="Classify every diagram in [diag_dir] using all the \
           other ones in [diag_dir] (k Nearest Nieghbors)")
  parser.add_argument('--diagrams-dir', dest='diag_dir', default='train/diags/radial')
  parser.add_argument('--secondary-diagrams-dir', dest='sec_diag_dir', default=None,
                      help="When this option is set, use the sum of distances between \
                      corresponding diagrams")
  parser.add_argument('-k', dest='k', type=int, default=10)
  parser.add_argument('--weight-function', dest='weight_fun', default="simple",
                      help="Choose from simple (constant), position (1 / position among \
                      closest neighbors), distance (1 / (1 + bottleneck distance))")
  parser.add_argument('--ignore-near-diag', dest='ignore_near_diag', action='store_true',
                      help="Ignore entries just above diagonal")
  return parser.parse_args()


if __name__ == '__main__':
  args = get_args()

  conf_matrix = [[0, 0], [0, 0]]
  weight_fun = {
                "simple": knn.simple_weight,
                "position": knn.one_over_pos,
                "distance": knn.one_over_dist
               }[args.weight_fun]
  
  for fname in glob.glob('{}/*.p'.format(args.diag_dir)):
    prob_class_1 = knn.classify_knn(fname, args.diag_dir, k=args.k, weight_fun=weight_fun,
                                    sec_diag_dir=args.sec_diag_dir,
                                    ignore_near_diag=args.ignore_near_diag)
    pred_cls = 1 if prob_class_1 >= 0.5 else 0
    real_cls = utils.get_class(fname)
    conf_matrix[pred_cls][real_cls] += 1
    print("{}: pred={} real={}".format(utils.get_bname(fname), pred_cls, real_cls))

  print("Confusion matrix:")
  print(conf_matrix)
  
  all_samples = sum(sum(row) for row in conf_matrix)
  accuracy = (conf_matrix[0][0] + conf_matrix[1][1]) / all_samples
  print("Accuracy:")
  print(accuracy)
