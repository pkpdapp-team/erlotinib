#
# This file is part of the erlotinib repository
# (https://github.com/DavAug/erlotinib/) which is released under the
# BSD 3-clause license. See accompanying LICENSE.md for copyright notice and
# full license details.
#

import numpy as np


class PopulationModel(object):
    """
    A base class for population models.

    Parameters
    ----------
    n_ids
        Number of individual bottom level models.
    """

    def __init__(self, n_ids):
        super(PopulationModel, self).__init__()

        # This is going to be used to define the number of parameters.
        self._n_ids = n_ids

        # Set defaults
        self._ids = None
        self._bottom_parameter_name = 'Bottom param'

    def __call__(self, parameters):
        """
        Returns the log-likelihood score of the population model.

        The parameters are expected to be of length :meth:`n_parameters`. The
        first :meth:`n_bottom_parameters` parameters are treated as the
        'observations' of the individual model parameters, and the remaining
        :meth:`n_top_parameters` specify the values of the population
        model parameters.
        """
        raise NotImplementedError

    def get_bottom_parameter_name(self):
        """
        Returns the name of the the modelled bottom parameter. If name was not
        set, ``None`` is returned.
        """
        return self._bottom_parameter_name

    def get_ids(self):
        """
        Returns the IDs of the modelled individuals. If IDs were not set,
        ``None`` is returned.
        """
        return self._ids

    def get_top_parameter_names(self):
        """
        Returns the name of the the population model parameters. If name were
        not set, defaults are returned.
        """
        raise NotImplementedError

    def n_bottom_parameters(self):
        """
        Returns the number of bottom-level parameters of the population model.

        This is the total number of input parameters from the individual
        likelihoods.
        """
        raise NotImplementedError

    def n_ids(self):
        """
        Returns the number of modelled individuals of the population model.
        """
        return self._n_ids

    def n_parameters(self):
        """
        Returns the number of parameters of the population model.
        """
        raise NotImplementedError

    def n_parameters_per_id(self):
        """
        Returns the number of parameters per likelihood that are modelled by
        the population model.
        """
        return 1

    def n_top_parameters(self):
        """
        Returns the number of top parameters of the population.

        This is the number of population parameters.
        """
        raise NotImplementedError

    def sample(self, top_parameters, n=None):
        r"""
        Returns `n` random samples from the underlying population distribution.

        The returned value is a numpy array with shape :math:`(n,)` where
        :math:`n` is the requested number of samples.
        """
        raise NotImplementedError

    def set_bottom_parameter_name(self, name):
        """
        Sets the name of the input parameter from each individual bottom model.
        """
        self._bottom_parameter_name = str(name)

    def set_ids(self, ids):
        """
        Sets the IDs of the modelled individuals.

        Parameters
        ----------
        ids
            A list of ids of length ``n_ids``.
        """
        if len(ids) != self._n_ids:
            raise ValueError(
                'Length of IDs does not match n_ids.')

        self._ids = [str(label) for label in ids]

    def set_top_parameter_names(self, names):
        """
        Sets the names of the population model parameters.
        """
        raise NotImplementedError


class HeterogeneousModel(PopulationModel):
    """
    A population model that imposes no relationship on the model parameters
    across individuals.

    A heterogeneous model assumes that the parameters across individuals are
    independent.

    Calling the HeterogenousModel returns a constant, irrespective of the
    parameter values. We chose this constant to be ``0``.

    Extends :class:`erlotinib.PopulationModel`.

    Parameters
    ----------
    n_ids
        Number of individual bottom level models.
    """

    def __init__(self, n_ids):
        super(HeterogeneousModel, self).__init__(n_ids)

        # Set number of input individual parameters
        self._n_bottom_parameters = n_ids

        # Set number of population parameters
        self._n_top_parameters = 0

        # Set number of parameters
        self._n_parameters = self._n_bottom_parameters + self._n_top_parameters

        # Set default top-level parameter names
        self._top_parameter_names = None

    def __call__(self, parameters):
        """
        Returns the log-likelihood score of the population model.

        The log-likelihood score of a PooledModel is independent of the input
        parameters. We choose to return a score of ``0``.

        The parameters are expected to be of length :meth:`n_parameters`. The
        first :meth:`nids` parameters are treated as the 'observations' of the
        individual model parameters, and the remaining
        :meth:`n_top_parameters` specify the values of the population
        model parameters.
        """
        return 0

    def get_top_parameter_names(self):
        """
        Returns the name of the the population model parameters. If name were
        not set, defaults are returned.
        """
        return self._top_parameter_names

    def n_bottom_parameters(self):
        """
        Returns the number of bottom-level parameters of the population model.

        This is the total number of input parameters from the individual
        likelihoods.
        """
        return self._n_bottom_parameters

    def n_parameters(self):
        """
        Returns the number of parameters of the population model.
        """
        return self._n_parameters

    def n_top_parameters(self):
        """
        Returns the number of top parameters of the population.

        This is the number of population parameters.
        """
        return self._n_top_parameters

    def set_top_parameter_names(self, names):
        """
        Sets the names of the population model parameters.

        This method raises an error for a heterogenous population model as
        no top-level model parameter exist.
        """
        raise ValueError(
            'A heterogeneous population model has no top-level parameters.')


class LogNormalModel(PopulationModel):
    r"""
    A population model that assumes that model parameters across individuals
    are log-normally distributed.

    A log-normal population model assumes that a model parameter :math:`\psi`
    varies across individuals such that :math:`\psi` is log-normally
    distributed in the population

    .. math::
        p(\psi |\mu _{\text{log}}, \sigma _{\text{log}}) =
        \frac{1}{\psi} \frac{1}{\sqrt{2\pi} \sigma _{\text{log}}}
        \exp\left(-\frac{(\log \psi - \mu _{\text{log}})^2}
        {2 \sigma ^2_{\text{log}}}\right).

    Here :math:`\mu _{\text{log}}` and :math:`\sigma ^2_{\text{log}}` are the
    mean and variance of :math:`\log \psi` in the population, respectively.

    The mean and variance of the parameter :math:`\psi` itself,
    :math:`\mu = \mathbb{E}\left[ \psi \right]` and
    :math:`\sigma ^2 = \text{Var}\left[ \psi \right]`, are given by

    .. math::
        \mu = \mathrm{e}^{\mu _{\text{log}} + \sigma ^2_{\text{log}} / 2}
        \quad \text{and} \quad
        \sigma ^2 =
        \mu ^2 \left( \mathrm{e}^{\sigma ^2_{\text{log}}} - 1\right) .

    As a result, any observed individual with parameter :math:`\psi _i` is
    assumed to be a realisation of the random variable :math:`\psi`.

    Calling the LogNormalModel returns the log-likelihood score of the model,
    assuming that the first ``n_ids`` parameters are the realisations of
    :math:`\psi` for the observed individuals, and the remaining 2 parameters
    are :math:`\mu _{\text{log}}` and :math:`\sigma ^2_{\text{log}}`.

    Extends :class:`erlotinib.PopulationModel`.

    Parameters
    ----------
    n_ids
        Number of individual bottom level models.
    """

    def __init__(self, n_ids):
        super(LogNormalModel, self).__init__(n_ids)

        # Set number of input individual parameters
        self._n_bottom_parameters = n_ids

        # Set number of population parameters
        self._n_top_parameters = 2

        # Set number of parameters
        self._n_parameters = self._n_bottom_parameters + self._n_top_parameters

        # Set default top-level parameter names
        self._top_parameter_names = ['Mean', 'Std.']
        # TODO: Reparametrise by mean and std (simply easier to understand)

    def __call__(self, parameters):
        r"""
        Returns the unnormalised log-likelihood score of the population model.

        The log-likelihood score of a LogNormalModel is the log-pdf evaluated
        at the population model parameters

        .. math::
            L(\mu _{\text{log}}, \sigma _{\text{log}} | \Psi) =
            \sum _{i=1}^N
            \log p(\psi _i |\mu _{\text{log}}, \sigma _{\text{log}}) ,

        where
        :math:`\Psi := (\psi ^{\text{obs}}_1, \ldots , \psi ^{\text{obs}}_N`)
        are the observed :math:`\psi` from :math:`N` individuals.

        The first ``n_ids`` parameters are the realisations of :math:`\psi`
        for the observed individuals, and the remaining 2 parameters are the
        mean and standard deviation of :math:`\log \psi` in the population,
        :math:`\mu _{\text{log}}` and :math:`\sigma _{\text{log}}`.

        .. note::
            All constant terms that do not depend on the model parameters are
            dropped when computing the log-likelihood score.

        Parameters
        ----------
        parameters
            An array-like object with the model parameter values,
            :math:`\psi ^{\text{obs}}_1, \ldots , \psi ^{\text{obs}}_N`,
            :math:`\mu _{\text{log}}` and :math:`\sigma _{\text{log}}`.
        """
        log_psis = np.log(parameters[:self._n_ids])
        mean_log, std_log = parameters[self._n_ids:]

        if mean_log <= 0 or std_log <= 0:
            # The mean and var of log psi are strictly positive
            return -np.inf

        # Compute log-likelihood score
        score = -self._n_ids * np.log(std_log) - np.sum(log_psis) \
            - np.sum((log_psis - mean_log) ** 2) / (2 * std_log ** 2)

        return score

    def get_top_parameter_names(self):
        """
        Returns the name of the the population model parameters. If name were
        not set, defaults are returned.
        """
        return self._top_parameter_names

    def n_bottom_parameters(self):
        """
        Returns the number of bottom-level parameters of the population model.

        This is the total number of input parameters from the individual
        likelihoods.
        """
        return self._n_bottom_parameters

    def n_parameters(self):
        """
        Returns the number of parameters of the population model.
        """
        return self._n_parameters

    def n_top_parameters(self):
        """
        Returns the number of top parameters of the population.

        This is the number of population parameters.
        """
        return self._n_top_parameters

    def sample(self, top_parameters, n=None):
        r"""
        Returns :math:`n` random samples from the underlying population
        distribution.

        For a LogNormalModel :math:`n` random samples from a log-normal
        distribution are returned, where the population model parameters
        :math:`\mu _{\text{log}}` and :math:`\sigma _{\text{log}}` are
        given by ``top_parameters``.

        The returned value is a numpy array with shape :math:`(n,)` where
        :math:`n` is the requested number of samples.
        """
        if len(top_parameters) != self._n_top_parameters:
            raise ValueError(
                'The number of provided parameters does not match the expected'
                ' number of top-level parameters.')

    def set_top_parameter_names(self, names):
        """
        Sets the names of the population model parameters.

        This method raises an error for a heterogenous population model as
        no top-level model parameter exist.
        """
        if len(names) != self._n_top_parameters:
            raise ValueError(
                'Length of names does not match n_top_parameters.')

        self._top_parameter_names = [str(label) for label in names]


class PooledModel(PopulationModel):
    """
    A population model that pools the model parameters across individuals.

    A pooled model assumes that the parameters across individuals do not vary.
    As a result, all individual parameters are set to the same value.

    Calling the PooledModel returns a constant, irrespective of the parameter
    values. We chose this constant to be ``0``.

    Extends :class:`erlotinib.PopulationModel`.

    Parameters
    ----------
    n_ids
        Number of individual bottom level models.
    """

    def __init__(self, n_ids):
        super(PooledModel, self).__init__(n_ids)

        # Set number of input individual parameters
        self._n_bottom_parameters = 0

        # Set number of population parameters
        self._n_top_parameters = 1

        # Set number of parameters
        self._n_parameters = self._n_bottom_parameters + self._n_top_parameters

        # Set default top-level parameter names
        self._top_parameter_names = ['Pooled']

    def __call__(self, parameters):
        """
        Returns the log-likelihood score of the population model.

        The log-likelihood score of a PooledModel is independent of the input
        parameters. We choose to return a score of ``0``.

        The parameters are expected to be of length :meth:`n_parameters`. The
        first :meth:`nids` parameters are treated as the 'observations' of the
        individual model parameters, and the remaining
        :meth:`n_top_parameters` specify the values of the population
        model parameters.
        """
        return 0

    def get_top_parameter_names(self):
        """
        Returns the name of the the population model parameters. If name were
        not set, defaults are returned.
        """
        return self._top_parameter_names

    def n_bottom_parameters(self):
        """
        Returns the number of bottom-level parameters of the population model.

        This is the total number of input parameters from the individual
        likelihoods.
        """
        return self._n_bottom_parameters

    def n_parameters(self):
        """
        Returns the number of parameters of the population model.
        """
        return self._n_parameters

    def n_top_parameters(self):
        """
        Returns the number of top parameters of the population.

        This is the number of population parameters.
        """
        return self._n_top_parameters

    def sample(self, top_parameters, n=None):
        r"""
        Returns :math:`n` random samples from the underlying population
        distribution.

        For a PooledModel the input top-level parameters are copied for each
        individual and are returned :math:`n` times.

        The returned value is a numpy array with shape :math:`(n, d)` where
        :math:`n` is the requested number of samples.
        """
        if len(top_parameters) != self._n_top_parameters:
            raise ValueError(
                'The number of provided parameters does not match the expected'
                ' number of top-level parameters.')
        samples = np.asarray(top_parameters)

        # If only one sample is wanted, return input parameter
        if n is None:
            return samples

        # If more samples are wanted, broadcast input parameter to shape (n,)
        samples = np.broadcast_to(samples, shape=(n,))
        return samples

    def set_top_parameter_names(self, names):
        """
        Sets the names of the population model parameters.
        """
        if len(names) != self._n_top_parameters:
            raise ValueError(
                'Length of names does not match n_top_parameters.')

        self._top_parameter_names = [str(label) for label in names]
