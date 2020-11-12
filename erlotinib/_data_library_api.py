#
# This file is part of the erlotinib repository
# (https://github.com/DavAug/erlotinib/) which is released under the
# BSD 3-clause license. See accompanying LICENSE.md for copyright notice and
# full license details.
#

import os

import pandas as pd


class DataLibrary(object):
    r"""
    A collection of Erlotinib PKPD datasets.

    Each method corresponds to a separate dataset, which will return
    the corresponding dataset in form of a :class:`pandas.DataFrame`.
    """

    def __init__(self):
        # Get path to data library
        self._path = os.path.dirname(os.path.abspath(__file__))
        self._path += '/data_library/'

    def lung_cancer_control_group(self, standardised=False):
        r"""
        Returns the lung cancer control group data published in [1]_ as a
        :class:`pandas.DataFrame`.

        The dataset contains the time series data of 8 mice with
        patient-derived lung cancer implants. The tumour volume of each
        mouse was monitored over a period of 30 days and measured a couple
        times a week.

        The original column keys are '#ID', 'TIME in day' and 'TUMOUR VOLUME in
        cm^3'. If ``standardised=True`` those column keys are changed to the
        generic keys 'ID', 'Time', and 'Biomarker', which are also used by
        other classes.

        .. [1] Eigenmann, M. J. et al., Combining Nonclinical Experiments with
               Translational PKPD Modeling to Differentiate Erlotinib and
               Gefitinib, Mol Cancer Ther. 2016; 15(12):3110-3119.

        Parameters
        ----------
        standardised
            A boolean flag indicating whether the columns are supposed to be
            standardised.

        """
        file_name = 'lxf_control_growth.csv'
        data = pd.read_csv(self._path + file_name)

        if standardised:
            data = data.rename(columns={
                '#ID': 'ID',
                'TIME in day': 'Time',
                'TUMOUR VOLUME in cm^3': 'Biomarker'})

        return data
