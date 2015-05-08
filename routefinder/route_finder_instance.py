from django.conf import settings

from routefinder import MidLinkRouteFinder
from weight_presets import weight_presets

import cPickle

path = settings.ROUTEFINDER['graph_path']

multigraph, crs = cPickle.load(open(path))

rf = MidLinkRouteFinder(multigraph, weight_presets)
