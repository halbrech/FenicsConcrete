import fenics_concrete
import pytest

def test_stiffness_homogenization():
    #input values
    # matrix
    matrix_E = 10 # MPa
    matrix_poissions_ratio = 0.2
    matrix_compressive_strength = 10

    # air
    air_E = 10 # MPa
    air_vol_frac = 0.2

    # aggregates
    aggregate_E = 30
    aggregate_poissions_ratio = 0.25
    aggregate_radius = 2 # mm
    aggregate_vol_frac = 0.3 # volume fraction

    # itz assumptions
    itz_thickness = 0.2 #mm
    itz_factor = 0.8 # percentage of stiffness of matrix

    # testing new code
    homgenized_concrete = fenics_concrete.ConcreteHomogenization(E_matrix=matrix_E, nu_matrix=matrix_poissions_ratio, fc_matrix=matrix_compressive_strength)
    # adding airpores
    homgenized_concrete.add_uncoated_particle(E=air_E,nu=matrix_poissions_ratio,volume_fraction=air_vol_frac)
    # adding agregates
    homgenized_concrete.add_coated_particle(E_inclusion=aggregate_E, nu_inclusion=aggregate_poissions_ratio, itz_ratio=itz_factor, radius=aggregate_radius, coat_thickness=itz_thickness,volume_fraction=aggregate_vol_frac)

    assert homgenized_concrete.E_eff == pytest.approx(13.156471830404511)
    assert homgenized_concrete.nu_eff == pytest.approx(0.21110139111362222)
    assert homgenized_concrete.fc_eff == pytest.approx(11.317889983420725)