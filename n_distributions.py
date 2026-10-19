import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

min_sza=105
n_pix=6
pearson_r=0.5
coUVD=12.7

orb_start=2000 #usually 2000
orb_stop=15500 #usually 15500


master_path=r'E:/nightglow/master_cnn.csv' #Huge csv with all data merged
data=pd.read_csv(master_path)
data = data[
    (data['orbit_number'] >= 0) & 
    (data['orbit_number'] < 24600) &
    (data['sza'] >= 105) &
    (data['count'] >= 6) &
    (data['pearson_r_muv'] >= 0.6) &
    (data['color_flag_muv'] == 'green') &
    (data['type']!='NON-DET') &
    (data['type'] != 'NONE') &
    (data['type'] != 'SEP')
]
data = data.drop_duplicates(subset=["nick_number"])

def gauss_pdf(x, mu, sig):
    pxi = np.exp(-0.5 * ((x - mu) / sig)**2) / (sig * np.sqrt(2*np.pi))
    return pxi


def two_dist(data, bins=30, min=0, max=100):

    # Step 1: Prepare Data
    data=data['CO/CO2p'].dropna() #take initial ratios
    data=data[(data >= min) & (data <= max)].values #limit to 0 -> 100

    target = 12.7

    # Determine histogram bin edges exactly as plt.hist will use
    #bin_edges = np.histogram_bin_edges(data, bins=bins)

    # Find which bin contains 1/12.7
    #bin_idx = np.searchsorted(bin_edges, target) - 1

    # Get bin limits
    #bin_lo = bin_edges[bin_idx]
    #bin_hi = bin_edges[bin_idx + 1]

    #print(f"Removing bin {bin_idx}: [{bin_lo:.4f}, {bin_hi:.4f})")

    # Remove all data points in that bin
    #data = data[(data < bin_lo) | (data >= bin_hi)]

    # Step 2: Fit 1 Gaussian
    N=len(data)
    mu1=np.sum(data)/N
    sig1_sq = np.sum((data - mu1)**2) / N

    x = np.linspace(min, max, 500) #Fit using data, plot using just some values
    pxi_data = gauss_pdf(data, mu1, np.sqrt(sig1_sq)) #use data to calculate log-likelihood
    lnL_1 = np.sum(np.log(pxi_data + 1e-12)) #log-likelihood
    pxi_plot = gauss_pdf(x, mu1, np.sqrt(sig1_sq)) #use x to plot

    plt.figure()
    plt.plot(x,pxi_plot, label=f"Guassian Fit: μ={mu1:.2f}, σ={np.sqrt(sig1_sq):.2f}")
    plt.hist(data, bins=bins, density=True, alpha=0.5, label="UVD/CAM Ratio")
    plt.ylabel("Probability Density")
    plt.xlabel("UVD/CAM Ratio")
    plt.legend()
    plt.show()

    # Step 3: Fit 2 Guassians, use EM algo
    epsilon = 1e-6 #convergence parameter
    max_iter = 1000 #maximum iterations
    old_lnL = -np.inf

    mus = np.array([np.percentile(data, 10), np.percentile(data, 90)])
    sigmas = np.array([np.std(data), np.std(data)])
    weights = np.array([0.5, 0.5])


    for i in range(max_iter):

        # E-step (calculate responsibilities)
        p0 = weights[0] * gauss_pdf(data, mus[0], sigmas[0])
        p1 = weights[1] * gauss_pdf(data, mus[1], sigmas[1])

        denom = p0 + p1 + 1e-12 #Add overflow buffer
        r0 = p0 / denom
        r1 = p1 / denom

        # M-step (update parameters using responsibilities)
        mus = np.array([
            np.sum(r0 * data) / np.sum(r0),
            np.sum(r1 * data) / np.sum(r1)
        ])

        sigmas = np.array([
            np.sqrt(np.sum(r0 * (data - mus[0])**2) / np.sum(r0)),
            np.sqrt(np.sum(r1 * (data - mus[1])**2) / np.sum(r1))
        ])

        weights = np.array([
            np.sum(r0) / N,
            np.sum(r1) / N
        ])

        # recompute likelihood using updated parameters
        p0 = weights[0] * gauss_pdf(data, mus[0], sigmas[0])
        p1 = weights[1] * gauss_pdf(data, mus[1], sigmas[1])

        lnL = np.sum(np.log(p0 + p1 + 1e-12))

        print(
            f"Iter {i:4d} | "
            f"mu=({mus[0]:6.2f}, {mus[1]:6.2f}) | "
            f"std=({sigmas[0]:6.2f}, {sigmas[1]:6.2f}) | "
            f"w=({weights[0]:.3f}, {weights[1]:.3f}) | "
            f"lnL={lnL:.2f}",
            end="\r"
        )

        if abs(lnL - old_lnL) < epsilon:
            break

        old_lnL = lnL

    print()

    # Step 4: Compute AIC, BIC
    k1=2 #num of parameters for 1 Guassian
    k2=5 #num for 2 Gaussians
    AIC1 = 2*k1 - 2*lnL_1
    BIC1 = k1*np.log(N) - 2*lnL_1

    AIC2 = 2*k2 - 2*lnL
    BIC2 = k2*np.log(N) - 2*lnL
    print(f"Old AIC: {AIC1:.4f} | Old BIC: {BIC1:.4f}")
    print(f"New AIC: {AIC2:.4f} | New BIC: {BIC2:.4f}")
    print(f"Del AIC: {AIC1-AIC2:.4f}  | Del BIC: {BIC1-BIC2:.4f}")

    # Step 5: Plot them
    pxi_0=weights[0]*gauss_pdf(x, mus[0], sigmas[0])
    pxi_1=weights[1]*gauss_pdf(x, mus[1], sigmas[1])

    plt.figure()
    plt.plot(x,pxi_0,label=f"Gaussian 1: μ={mus[0]:.2f}, σ={sigmas[0]:.2f}")
    plt.plot(x,pxi_1,label=f"Gaussian 2: μ={mus[1]:.2f}, σ={sigmas[1]:.2f}")
    plt.plot(x, pxi_0 + pxi_1, label="Total fit")
    plt.hist(data, bins=bins, density=True, alpha=0.5, label="UVD/CAM Ratio")
    plt.ylabel("Probability Density")
    plt.xlabel("UVD/CAM Ratio")
    plt.legend()
    plt.show()


    return

two_dist(data, bins=30, min=0, max=60)
