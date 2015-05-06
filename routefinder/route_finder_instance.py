from routefinder import MidLinkRouteFinder


from weight_presets import weight_presets

multigraph = None #insert code here to get the multigraph

crs = None 
units2miles = None


rf = MidLinkRouteFinder(multigraph, weight_presets)
