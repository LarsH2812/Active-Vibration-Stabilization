import sqlite3, numpy as np, matplotlib.pyplot as plt, itertools

print(sqlite3.version, "\n", np.version.full_version, "\n")
for p in itertools.permutations(['northY','northZ','eastX','eastZ','topX','topY'], 6):
    print(p)
    with sqlite3.connect("Meetfiles/data/2023-04-18/2023-04-18 - 165819 (3.00).db") as db:
        result = np.transpose(db.cursor().execute(f'SELECT t,{p[0]},{p[1]},{p[2]},{p[3]},{p[4]},{p[5]} FROM guralp').fetchall())

    DISTANCES = {
    'gnx':1.3750, 'gex':0.0000, 'gtx':0.0559,
    'gny':0.0000, 'gey':1.3750, 'gty':0.3449,
    'gnz':0.7528, 'gez':0.7528, 'gtz':3.2772,
    }

    AMAT = np.matrix([
    #    x | y | z |        rx         |        ry         |          rz
        [0 , 1 , 0 , -DISTANCES['gnz'] ,                 0 , -DISTANCES['gnx']],    # northY
        [0 , 0 , 1 , -DISTANCES['gny'] ,  DISTANCES['gnx'] ,                 0],    # northZ
        [1 , 0 , 0 ,                 0 ,  DISTANCES['gez'] ,  DISTANCES['gey']],    # eastX
        [0 , 0 , 1 , -DISTANCES['gey'] ,  DISTANCES['gex'] ,                 0],    # eastZ
        [1 , 0 , 0 ,                 0 , -DISTANCES['gtz'] ,  DISTANCES['gty']],    # topX
        [0 , 1 , 0 ,  DISTANCES['gtz'] ,                 0 , -DISTANCES['gtx']],    # topY
    ])
    AMAT_INV = np.linalg.inv(AMAT)

    meas = np.matrix(result[1:])
    out = np.array(AMAT_INV * meas)

    fig, axs = plt.subplots(6,1,sharex = True, sharey = True, gridspec_kw=(dict(hspace = 0)))
    for i, ax in enumerate(zip(axs,'x y z rx ry rz'.split())):
        ax[0].plot(result[0],out[i], label= ax[1])
    plt.legend()
    plt.show(block=False)
    plt.pause(2)
    plt.close()

