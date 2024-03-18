"""Helper functions for week 5, which are not relevant for the tutorial."""

import cebra.datasets
import statsmodels.api as sm
import numpy as np

class HippocampusDataset():

    def __init__(self):
        self.raw_data = cebra.datasets.init('rat-hippocampus-single-achilles')

    def get_neuron_spikes(self, neuron_idx):
        return self.raw_data.neural[:, neuron_idx].numpy()
    
    @property
    def all_spikes_binned(self):
        return self.raw_data.neural.numpy()

    @property
    def position(self):
        return self.raw_data.index[:, 0].numpy()

    @property
    def direction(self):
        return self.raw_data.index[:, 1].numpy()

    @property
    def shape(self):
        return self.all_spikes_binned.shape

    @property
    def sampling_rate_hz(self):
        return 100.

    @property
    def num_neurons(self):
        return self.shape[1]

    @property
    def time(self):
        return np.arange(len(self)) / self.sampling_rate_hz

    def __len__(self):
        return len(self.all_spikes_binned)


class GLMModel():
    """The class for our GLM model.
    
    We split the functionality into different parts:
    - fitting the model
    - computing the goodness of fit (the pseudo-R2)
    - making predictions on the dataset
    """

    def __init__(self):
        self.link_function = sm.families.links.Log()
        self.family = sm.families.Poisson(link = self.link_function)

    def fit(self, design_matrix, spikes):
        design_mat_offset = np.hstack((np.ones((len(design_matrix),1)), design_matrix))
        self._model = sm.GLM(
            endog=spikes,
            exog=design_mat_offset,
            family=self.family
        )
        self._results = self._model.fit(max_iter=100, tol=1e-6, tol_criterion='params')

    def predict(self, design_mat):
        return np.exp(self.constant_params + design_mat @ self.filter_params)

    def score(self):
        return self._results.pseudo_rsquared(kind='mcf') 

    @property
    def filter_params(self):
        return self._results.params[1:]

    @property
    def constant_params(self):
        return self._results.params[0]