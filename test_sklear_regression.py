import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


def poly_func(x, params):
    y = params[0] + \
        x[0]*params[1] + \
        x[1]*params[2] + \
        x[2]*params[3] + \
        x[0]**2*params[4] + \
        x[0]*x[1]*params[5] + \
        x[0]*x[2]*params[6] + \
        x[1]**2*params[7] + \
        x[1]*x[2]*params[8] + \
        x[2]**2 * params[9]
    return y

x = np.array([[i, i, i] for i in range(25)])
params = np.arange(10)
y = [poly_func(xdat, params) for xdat in x]


############

poly_feat = PolynomialFeatures(2)
poly = poly_feat.fit_transform(x)

reg = LinearRegression().fit(poly, y)