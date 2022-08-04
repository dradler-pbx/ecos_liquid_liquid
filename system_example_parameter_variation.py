import VCSpbx as vcs
from CoolProp.CoolProp import PropsSI as CPPSI
import numpy as np
from tqdm import tqdm
from pandas import DataFrame, to_pickle
import matplotlib.pyplot as plt

# parameter setting
cpr_speed = 4000.0  # rpm
ref = 'R290'
superheat = 6.0  # K

coolant = 'INCOMP::MEG[0.5]'
p_coolant = 1e5  # Pa
mdot_coldside = 0.35  # kg/s
T_coldside_in = 4. + 273.15  # K
h_coldside_in = CPPSI('H', 'T', T_coldside_in, 'P', p_coolant, coolant)

mdot_hotside = 0.5  # kg/s
T_hotside_in = 50 + 273.15  # K
h_hotside_in = CPPSI("H", "T", T_hotside_in, "P", 1e5, coolant)

# initital guesses
mdot_ref_init = 5.e-3
pc_init = 18e5
Tc_init = CPPSI('T', 'P', pc_init, 'Q', 0, ref)
h2_init = CPPSI('H', 'P', pc_init, 'T', 60+273.15, ref)
h3_init = CPPSI('H', 'P', pc_init, 'Q', 0, ref)
h4_init = CPPSI('H', 'P', pc_init, 'T', Tc_init-2., ref)
p0_init = 3.0e5
T0_init = CPPSI('T', 'P', p0_init, 'Q', 1, ref)
h5_init = CPPSI('H', 'P', p0_init, 'T', T0_init+superheat, ref)
h1_init = CPPSI('H', 'P', p0_init, 'T', T0_init+superheat+2., ref)


# Instantiate components
system = vcs.System(id='system', tolerance=1.)
cpr = vcs.Compressor_efficiency(id='cpr', system=system, etaS=0.645, etaV=0.82, etaEL=0.775, stroke=16.1e-6, speed=cpr_speed)
cond = vcs.CondenserBPHE('cond', system, k=[300., 300., 300.], area=0.8, subcooling=0.1, initial_areafractions=[0.1, 0.8, 0.1])
ihx = vcs.IHX(id='ihx', system=system, UA=5.3)
evap = vcs.Evaporator(id='evap', system=system, k=[420., 420.], area=1., superheat=superheat, boundary_switch=True, limit_temp=True)
snkcold = vcs.Sink(id='snk_air', system=system)
srccold = vcs.Source(id='src_air', system=system, mdot=mdot_coldside, p=p_coolant, h=h_coldside_in)
snkhot = vcs.Sink('snkhot', system)
srchot = vcs.Source('srchot', system, mdot_hotside, 1e5, h_hotside_in)

# connections
cpr_cond = vcs.Junction('cpr_cond', system, ref, cpr, 'outlet_A', cond, 'inlet_A', mdot_ref_init, pc_init, h2_init)
cond_ihx = vcs.Junction('cond_ihx', system, ref, cond, 'outlet_A', ihx, 'inlet_A', mdot_ref_init, pc_init, h3_init)
srchot_cond = vcs.Junction("srchot_cond", system, coolant, srchot, 'outlet_A', cond, 'inlet_B', mdot_hotside, 1e5, h_hotside_in)
cond_snkhot = vcs.Junction("cond_snkhot", system, coolant, cond, 'outlet_B', snkhot, 'inlet_A', mdot_hotside, 1e5, h_hotside_in)
ihx_evap = vcs.Junction(id='ihx_evap', system=system, medium=ref, upstream_component=ihx, upstream_id='outlet_A', downstream_component=evap, downstream_id='inlet_A', mdot_init= mdot_ref_init, p_init=p0_init, h_init=h4_init)
evap_ihx = vcs.Junction(id='evap_ihx', system=system, medium=ref, upstream_component=evap, upstream_id='outlet_A', downstream_component=ihx, downstream_id='inlet_B', mdot_init=mdot_ref_init, p_init=p0_init, h_init=h5_init)
ihx_cpr = vcs.Junction(id='ihx_cpr', system=system, medium=ref, upstream_component=ihx, upstream_id='outlet_B', downstream_component=cpr, downstream_id='inlet_A', mdot_init=mdot_ref_init, p_init=p0_init, h_init=h1_init)
srccold_evap = vcs.Junction(id='srccold_evap', system=system, medium=coolant, upstream_component=srccold, upstream_id='outlet_A', downstream_component=evap, downstream_id='inlet_B', mdot_init=mdot_coldside, p_init=p_coolant, h_init=h_coldside_in)
evap_snkcold = vcs.Junction(id='evap_snkcold', system=system, medium=coolant, upstream_component=evap, upstream_id='outlet_B', downstream_component=snkcold, downstream_id='inlet_A', mdot_init=mdot_coldside, p_init=p_coolant, h_init=h_coldside_in)

T_hotside_range = np.array([16, 18, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65]) + 273.15
T_coldside_range = np.arange(-10, 6.1, 1) + 273.15
cpr_speed_range = np.arange(1000, 5100, 200)
result_list = []
count = 1
runs = T_coldside_range.shape[0] * T_hotside_range.shape[0] * cpr_speed_range.shape[0]
srchot.set_enthalpy(CPPSI("H", "T", T_hotside_range[0], "P", 1e5, coolant))
srccold.set_enthalpy(CPPSI("H", "T", T_coldside_range[0], "P", 1e5, coolant))
for i in range(len(T_hotside_range)):
    if i > 0:
        print('Transition T_hotside {} -> {}'.format(T_hotside_range[i - 1], T_hotside_range[i]))
        transition_values = np.linspace(T_hotside_range[i-1], T_hotside_range[i], 10)
        for val in transition_values:
            srchot.set_enthalpy(CPPSI("H", "T", val, "P", 1e5, coolant))
            try:
                run_return = system.run()
            except:
                raise ValueError('Transition failed! T_hotside {} -> {} at {}'.format(T_hotside_range[i-1], T_hotside_range[i], val))
    for j in range(len(T_coldside_range)):
        if j > 0:
            transition_values = np.linspace(T_coldside_range[j-1], T_coldside_range[j], 20)
            print('Transition T_coldside {} -> {}'.format(T_coldside_range[j - 1], T_coldside_range[j]))
            for val in transition_values:
                srccold.set_enthalpy(CPPSI("H", "T", val, "P", 1e5, coolant))
                try:
                    run_return = system.run()
                except:
                    raise ValueError(
                        'Transition failed! T_coldside {} -> {} at {}'.format(T_coldside_range[j - 1], T_coldside_range[j], val))

        for cpr_speed in cpr_speed_range:
            cpr.set_speed(cpr_speed)
            res_dict = dict()
            res_dict['T_hotside_in'] = T_hotside_in
            res_dict['T_coldside_in'] = T_coldside_in
            res_dict['cpr_speed'] = cpr_speed

            try:
                run_return = system.run()
                res_dict['results'] = True
            except:
                res_dict['results'] = False
                print('no result')

            res_dict['Q0'] = (ihx_evap.get_enthalpy()-evap_ihx.get_enthalpy())*evap_ihx.get_massflow()
            res_dict['QC'] = (cpr_cond.get_enthalpy()-cond_ihx.get_enthalpy())*cond_ihx.get_massflow()
            res_dict['Pel'] = cpr.get_power()
            res_dict['p0'] = evap_ihx.get_pressure()
            res_dict['pC'] = cond_ihx.get_pressure()
            res_dict['residual_enthaplies'] = system.residual_enthalpy.copy()
            res_dict['run_return'] = run_return
            result_list.append(res_dict)
            print("{} of {}".format(count, runs))
            count += 1
        cpr_speed_range = np.flip(cpr_speed_range)
    T_coldside_range = np.flip(T_coldside_range)
data = DataFrame(result_list)
data.to_pickle('data.pkl')

