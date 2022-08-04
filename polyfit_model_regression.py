import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline


def write_results_file(regs, variables: list):
    filename = 'result_file.txt'
    var_list = ['u', 'v', 'w']
    coefs = ['k'+str(i) for i in range(10)]
    with open(filename, 'w') as f:
        f.write('Polynomial regression of VCSpbx simulation\n')
        f.write('---\n')
        f.write('Y(u,v,w) = k0 + k1*u + k2*v + k3*w + k4*u^2 + k5*u*v + k6*u*w + k7*v^2 + k8*v*w + k9*w^2\n')
        f.write('---\n')
        for i in range(3):
            f.write('{} = {}\n'.format(var_list[i], variables[i]))
        f.write('---\n')
        for reg in regs:
            f.write(reg.target+'\n')
            f.write('score = {}\n'.format(reg.score_calc))
            f.write('intercept = {}\n'.format(reg.intercept_))
            for i in range(10):
                f.write('{} =\t{}\n'.format(coefs[i], reg.coef_[i]))
            f.write('---\n')


data_raw = pd.read_pickle('data_cleared.pkl')

# generate training data.csv
x_data = data_raw[['T_hotside_in', 'T_coldside_in', 'cpr_speed']]
# x_data = x_data.values
Q0_data = data_raw['Q0']
Pel_data = data_raw['Pel']

poly_feat = PolynomialFeatures(degree=2)
poly = poly_feat.fit_transform(x_data)

Q0_reg = LinearRegression().fit(poly, Q0_data)
Q0_reg.target = 'Q0'
Q0_reg.score_calc = Q0_reg.score(poly, Q0_data)

Pel_reg = LinearRegression().fit(poly, Pel_data)
Pel_reg.target = 'Pel'
Pel_reg.score_calc = Pel_reg.score(poly, Pel_data)

# print('Score: {}'.format(Q0_reg.score(poly, Q0_data)))

write_results_file([Q0_reg, Pel_reg], x_data.columns)
