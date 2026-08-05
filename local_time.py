import matplotlib.pyplot as plt

def plot_local_time(data,key):
    plt.figure()
    plt.hist(data['local_time'],bins=20,edgecolor='black',alpha=.6)
    plt.title(f'Distribution of Local Time ({key})')
    plt.xlabel('Local Time')
    plt.show()
    
    plt.figure()
    plt.hist(data['hours_from_midnight'],bins=20,edgecolor='black',alpha=.6)
    plt.title(f'Hours from midnight ({key})')
    plt.xlabel('Time')
    plt.show()
    return