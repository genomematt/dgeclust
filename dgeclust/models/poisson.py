from __future__ import division

import numpy as np
import numpy.random as rn

import dgeclust.stats as st

########################################################################################################################


def _compute_loglik(theta, counts, lib_sizes):
    """Computes the log-likelihood of each element of counts for each element of phi and mu"""

    ## prepare data
    counts = counts.T
    counts = counts[:, :, np.newaxis]

    lib_sizes = lib_sizes.T
    lib_sizes = lib_sizes[:, :, np.newaxis]

    ## return
    return st.poissonln(counts, lib_sizes * theta)


########################################################################################################################


def compute_loglik(j, data, state):
    """Computes the log-likelihood of each element of counts for each element of theta"""

    ## read data
    group = data.groups.values()[j]
    counts = data.counts[group].values
    lib_sizes = data.lib_sizes[group].values

    ## return
    return _compute_loglik(state.theta, counts, lib_sizes)

########################################################################################################################


def sample_prior(size, shape, scale):
    """Samples theta from its prior"""

    ## return    
    return rn.gamma(shape, scale, size)
    
########################################################################################################################


def sample_params(theta, shape, scale):
    """Samples the shape and scale of the gamma distribution from its posterior, given theta"""

    ## compute sufficient statistics
    s = theta.sum()
    ls = np.log(theta).sum()
    n = theta.size

    ## sample scale, then sample shape
    shape = st.sample_gamma_shape(ls, n, shape, scale)
    scale = st.sample_gamma_scale(s, n, shape)

    ## return
    return shape, scale


########################################################################################################################


def sample_posterior(idx, data, state):
    """Sample theta from its posterior, given counts"""

    ## fetch all data points that belong to cluster idx
    groups = data.groups.values()
    counts = [data.counts[group][zz == idx].values for group, zz in zip(groups, state.zz)]
    lib_sizes = [np.sum(data.lib_sizes[group].values) for group in groups]

    s = np.sum([cnts.sum() for cnts in counts])
    n = np.asarray([cnts.size for cnts in counts])

    m = np.sum(lib_sizes * n)

    ## parameters
    shape, scale = state.pars

    ## return
    return rn.gamma(shape + s, scale / (m * scale + 1))
    
########################################################################################################################
