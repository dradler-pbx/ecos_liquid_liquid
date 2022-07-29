import VCSpbx as vcs
from CoolProp.CoolProp import PropsSI as CPPSI

# PARAMETERS
coolant = 'INCOMP::MEG[0.5]'
ref = 'R290'
# Refrigeration cylce
superheat = 7.0
mdot_ref_init = 0.01

# Evaporator coolant interface
mdot_c_evap = 0.3
p_c_evap = 1e5
t_c_evap_in = 3. + 273.15
h_c_evap_in = CPPSI('H', 'T', t_c_evap_in, 'P', p_c_evap, coolant)

# Condenser coolant interface
mdot_c_cond = 0.5
p_c_cond = 1e5
t_c_cond_in = 35. + 273.15
h_c_cond_in = CPPSI('H', 'T', t_c_cond_in, 'P', p_c_cond, coolant)

# INITIAL GUESSES
p0_init = 3.5e5
t0_init = CPPSI("T", "P", p0_init, "Q", 0, ref)
pC_init = 15e5
h2_init = CPPSI("H", "P", pC_init, "T", 80.+273.15, ref)
h3_init = CPPSI("H", "P", pC_init, "Q", 0, ref)
h4_init = CPPSI("H", "P", p0_init, "Q", 1, ref)
h5_init = CPPSI("H", "T", t0_init-superheat, "P", p0_init, ref)



# SYSTEM
system = vcs.System('system', tolerance=1e-4)

# COMPONENTS
cpr = vcs.Compressor_efficiency('cpr', system, etaS=0.6, etaV=0.9, stroke=16.1e-6, speed=3000)
cond = vcs.CondenserBPHE('cond', system, k=[300., 300., 300.], area=0.8, subcooling=0.1, initial_areafractions=[0.1, 0.8, 0.1])
ihx = vcs.IHX('ihx', system, 5.3)
evap = vcs.Evaporator(id='evap', system=system, k=[420., 420.], area=1., superheat=superheat, boundary_switch=True, limit_temp=True)

snkCcond = vcs.Sink(id='snkCcond', system=system)
srcCcond = vcs.Source(id='srcCcond', system=system, mdot=mdot_c_cond, p=p_c_cond, h=h_c_cond_in)

snkCevap = vcs.Sink(id='snkCevap', system=system)
srcCevap = vcs.Source(id='srcCevap', system=system, mdot=mdot_c_cond, p=p_c_cond, h=h_c_cond_in)


# JUNCTIONS
cpr_cond = vcs.Junction('cpr_cond', system, ref, cpr, 'outlet_A', cond, 'inlet_A', mdot_ref_init, pC_init, h2_init)
cond_ihx = vcs.Junction('cond_ihx', system, ref, cond, 'outlet_A', ihx, 'inlet_A', mdot_ref_init, pC_init, h3_init-1000)
ihx_evap = vcs.Junction('ihx_evap', system, ref, ihx, 'outlet_A', evap, 'inlet_A', mdot_ref_init, pC_init, h3_init-2000)
evap_ihx = vcs.Junction('evap_ihx', system, ref, evap, 'outlet_A', ihx, 'inlet_B', mdot_ref_init, p0_init, h4_init+1000)
ihx_cpr = vcs.Junction('ihx_cpr', system, ref, ihx, 'outlet_B', cpr, 'inlet_A', mdot_ref_init, p0_init, h5_init)

srcCcond_cond = vcs.Junction('srcCcond_cond', system, coolant, srcCcond, 'outlet_A', cond, 'inlet_B', mdot_c_cond, p_c_cond, h_c_cond_in)
cond_snkCcond = vcs.Junction('cond_snkCcond', system, coolant, cond, 'outlet_B', snkCcond, 'inlet_A', mdot_c_cond, p_c_cond, h_c_cond_in)

srcCevap_evap = vcs.Junction('srcCevap_evap', system, coolant, srcCevap, 'outlet_A', evap, 'inlet_B', mdot_c_evap, p_c_evap, h_c_evap_in)
evap_snkCevap = vcs.Junction('evap_snkCevap', system, coolant, evap, 'outlet_B', snkCevap, 'inlet_A', mdot_c_evap, p_c_evap, h_c_evap_in)

if __name__ == '__main__':
    system.run()
