from routefinder import MidLinkRouteFinder
from weight_presets import weight_presets

import cPickle

multigraph, crs = cPickle.load(open('multigraph.pickle'))


rf = MidLinkRouteFinder(multigraph, weight_presets)
