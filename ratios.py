"""Analyze and plot CO Cameron-to-UVD emission ratios."""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.mixture import GaussianMixture

def bimodal_test(data):
    """Fit one-, two-, and three-component Gaussian mixture models.

    Prints each model's AIC, BIC, means, standard deviations, and weights for
    ratios in the inclusive range from 0 to 100.
    """
    x = data['CO/CO2p'].dropna().values
    x2 = x[(x >= 0) & (x <= 100)].reshape(-1, 1)

    models = []
    for k in [1, 2, 3]:
        gmm = GaussianMixture(n_components=k, random_state=0)
        gmm.fit(x2)
        models.append((k, gmm.aic(x2), gmm.bic(x2), gmm))

        print(f"{k} components:")
        print("AIC =", gmm.aic(x2))
        print("BIC =", gmm.bic(x2))
        print("Means =", gmm.means_.flatten())
        print("Sigmas =", np.sqrt(gmm.covariances_.flatten()))
        print("Weights =", gmm.weights_)
        print()

    

def plot_ratio(data, mode='normal'):
    """Plot the direct or inverse emission-ratio distribution.

    Args:
        data: DataFrame containing the ``CO/CO2p`` ratio column.
        mode: ``normal`` plots CO Cameron/UVD; any other value plots UVD/CO
            Cameron.
    """
    plt.figure(figsize=(10,6))

    if mode == 'normal':
        n, bins, _=plt.hist(data['CO/CO2p'],bins=30, range=((0,100)),edgecolor='black',alpha=.6)
        errs=np.sqrt(n)
        bin_centers=0.5*(bins[:-1]+bins[1:])
        plt.axvline(12.7,ls='--',c='black',label='12.7 cutoff')
        plt.title('CO Cameron / UVD Emission Ratios')
    
    else:
        n, bins, _=plt.hist(1/data['CO/CO2p'],bins=30, range=((-0.1,0.6)),edgecolor='black',alpha=.6)
        errs=np.sqrt(n)
        bin_centers=0.5*(bins[:-1]+bins[1:])
        plt.axvline(1/12.7,ls='--',c='black',label='1/12.7 cutoff')
        plt.title('UVD / CO Cameron Emission Ratios')

    plt.errorbar(bin_centers,n,yerr=errs,fmt='none')
    plt.legend()
    plt.xlabel('Ratio')
    plt.ylabel('Counts')
    plt.show()

    #bimodal_test(data)
    return
