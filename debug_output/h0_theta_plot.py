import numpy as np
from matplotlib import pyplot as plt

theta_cons, H0_cons = np.loadtxt('./debug_output/consistency_theta_H0.txt', unpack=True)
theta_cons_bf, H0_cons_bf = np.loadtxt('./debug_output/consistency_bf_theta_H0.txt', unpack=True)
theta_camb, H0_camb = np.loadtxt('./debug_output/camb_theta_H0.txt', unpack=True)

plt.figure(1)
plt.plot(theta_cons, H0_cons, label='consistency')
plt.plot(theta_cons_bf, H0_cons_bf, label='consistency w/ odm fix')
plt.plot(theta_camb, H0_camb, label='camb')
plt.legend()
plt.xlabel('cosmomc_theta')
plt.ylabel('H0')
plt.savefig('./debug_output/theta_H0.png')