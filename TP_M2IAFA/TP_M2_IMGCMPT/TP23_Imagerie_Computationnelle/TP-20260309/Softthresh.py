def Softthresh(x,lamda):
    return np.sign(x) * np.where(np.abs(x) < lamda, 0, np.abs(x) - lamda)