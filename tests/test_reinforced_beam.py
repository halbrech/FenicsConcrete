import numpy as np

import fenics_concrete

import pytest


def test_reinforced_beam_2D():

    parameters = fenics_concrete.Parameters()  # using the current default values

    parameters['log_level'] = 'WARNING'
    parameters['mesh_density'] = 4  # number of elements in vertical direction, the others are set accordingly
    parameters['degree'] = 1  # reinforcement currently just linear

    # geometry
    parameters['length'] = 5 # m length
    parameters['height'] = 1 # height
    parameters['width'] = 0.8 # width

    # reinforcement
    parameters['reinforcment_y_location'] = 0.2 # distance from bottom in m
    parameters['A_reinforcement'] = 0.001  # m^2
    parameters['E_reinforcement'] = 200e9  # in Pa

    parameters['density'] = 2350  # in kg/m^3 density of concrete
    parameters['themal_cond'] = 2.0  # effective thermal conductivity, approx in Wm^-3K^-1, concrete!
    parameters['vol_heat_cap'] = 2.4e6  # volumetric heat cap J/m3

    # parameters for mechanics problem
    parameters['E_28'] = 25e9  # Youngs Modulus in Pa
    parameters['nu'] = 0.2  # Poissons Ratio

    # required parameters for alpha to E mapping
    parameters['alpha_t'] = 0.2
    parameters['alpha_0'] = 0.05
    parameters['a_E'] = 0.6

    # required parameters for alpha to tensile and compressive stiffness mapping
    parameters['fc_inf'] = 30e6  # in Pa
    parameters['a_fc'] = 1.5
    parameters['ft_inf'] = 4e6  # in Pa
    parameters['a_ft'] = 1.2

    # temperature setings:
    parameters['T_0'] = 20  # initial temperature of concrete
    parameters['T_boundary'] = 20  # constant boundary temperature

    # values for hydration
    # Q_inf: computed as Q_pot (heat release in J/kg of binder) * density binder * vol_frac. of binder
    parameters['Q_inf'] = 240000000  # potential heat per volume of concrete in J/m^3
    parameters['B1'] = 2.916E-4  # in 1/s
    parameters['B2'] = 0.0024229  # -
    parameters['eta'] = 5.554  # something about diffusion
    parameters['alpha_max'] = 0.875  # also possible to approximate based on equation with w/c
    parameters['E_act'] = 5653 * 8.3145  # activation energy in Jmol^-1
    parameters['T_ref'] = 25  # reference temperature in degree celsius

    displacement = -.1 # in meter


    experiment = fenics_concrete.ConcreteBeamReinforced2DExperiment(parameters)

    problem = fenics_concrete.ConcreteThermoMechanicalReinforced2D(experiment, parameters)

    # data for time stepping
    dt = 1200  # 20 min step
    time = dt * 100  # total simulation time in s

    # set time step
    problem.set_timestep(dt)  # for time integration scheme
    problem.experiment.apply_displ_load(displacement)

    # initialize time
    t = dt  # first time step time

    while t <= time:  # time
        # solve temp-hydration-mechanics
        problem.solve(t=t)  # solving this
        problem.pv_plot(t=t)

        # prepare next timestep
        t += dt


if __name__ == "__main__":
    test_reinforced_beam_2D()
