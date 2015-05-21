from django.conf import settings

from routefinder import MidLinkRouteFinder

import cPickle

path = settings.ROUTEFINDER['graph_path']

multigraph, weight_presets, crs = cPickle.load(open(path))

rf = MidLinkRouteFinder(multigraph, weight_presets)