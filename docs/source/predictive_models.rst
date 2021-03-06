.. _erlotinib: https://github.com/DavAug/erlotinib

*****************
Predictive Models
*****************

.. currentmodule:: erlotinib

Predictive models in erlotinib_ can be used to predict observable
pharmacokinetic and pharmacodynamic biomarker values.

Each predictive model consists of a :class:`MechanisticModel` and one
:class:`ErrorModel` for each observable biomarker.

Functional classes
------------------

- :class:`PosteriorPredictiveModel`
- :class:`PredictiveModel`
- :class:`PredictivePopulationModel`
- :class:`PriorPredictiveModel`

Detailed API
^^^^^^^^^^^^

.. autoclass:: PosteriorPredictiveModel
    :members:
    :inherited-members:

.. autoclass:: PredictiveModel
    :members:

.. autoclass:: PredictivePopulationModel
    :members:
    :inherited-members:

.. autoclass:: PriorPredictiveModel
    :members:
    :inherited-members:

Base classes
------------

- :class:`DataDrivenPredictiveModel`

Detailed API
^^^^^^^^^^^^

.. autoclass:: DataDrivenPredictiveModel
    :members: