from .simple import SimpleOptimizer
from .scipy import ScipyOptimizer

# TODO: Optimize the Optimizer (see note below)
# Key limitation of both: they assume CPC is fixed regardless
# of how much you spend on a channel. In reality, spending more 
# on a channel changes its CPC — that's exactly what saturation 
# models. So the optimizer is currently using a point estimate 
# of CPC from historical spend levels, not a response curve.

# The more sophisticated version would feed the saturation curve 
# itself into the optimizer so it can reason about diminishing 
# returns as it increases allocation — e.g. "search is efficient
# now but if I triple the budget there, CPC will rise.""

# That's the natural next evolution of the optimizer.