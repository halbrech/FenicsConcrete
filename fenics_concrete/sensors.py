import dolfin as df
import numpy as np


class Sensors(dict):
    """
    Dict that also allows to access the parameter p["parameter"] via the matching attribute p.parameter
    to make access shorter

    When to sensors with the same name are defined, the next one gets a number added to the name
    """

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        assert key in self
        self[key] = value

    def __setitem__(self, initial_key, value):
        # check if key exists, if so, add a number to the name
        i = 2
        key = initial_key
        if key in self:
            while key in self:
                key = initial_key + str(i)
                i += 1

        super().__setitem__(key, value)


# sensor template
class Sensor:
    """Template for a sensor object"""

    def measure(self, problem, t):
        """Needs to be implemented in child, depending on the sensor"""
        raise NotImplementedError()

    @property
    def name(self):
        return self.__class__.__name__

    def data_max(self, value):
        if self.max: # check for initial value (None is default)
            if value > self.max:
                self.max = value
        else:
            self.max = value



class DisplacementSensor(Sensor):
    """A sensor that measure displacement at a specific point"""

    def __init__(self, where):
        """
        Arguments:
            where : Point
                location where the value is measured
        """
        self.where = where
        self.data = []
        self.time = []

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        # get displacements
        self.data.append(problem.displacement(self.where))
        self.time.append(t)


class TemperatureSensor(Sensor):
    """A sensor that measure temperature at a specific point in celsius"""

    def __init__(self, where):
        """
        Arguments:
            where : Point
                location where the value is measured
        """
        self.where = where
        self.data = []
        self.time = []

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        T = problem.temperature(self.where) - problem.p.zero_C
        self.data.append(T)
        self.time.append(t)


class MaxTemperatureSensor(Sensor):
    """A sensor that measure the maximum temperature at each timestep"""

    def __init__(self):
        self.data = []
        self.time = []
        self.max = None

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        max_T = np.amax(problem.temperature.vector().get_local()) - problem.p.zero_C
        self.data.append(max_T)
        self.data_max(max_T)
        self.time.append(t)


class DOHSensor(Sensor):
    """A sensor that measure the degree of hydration at a point"""

    def __init__(self, where):
        """
        Arguments:
            where : Point
                location where the value is measured
        """
        self.where = where
        self.data = []
        self.time = []

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        # get DOH
        # TODO: problem with projected field onto linear mesh!?!
        alpha = problem.degree_of_hydration(self.where)
        self.data.append(alpha)
        self.time.append(t)


class MinDOHSensor(Sensor):
    """A sensor that measure the minimum degree of hydration at each timestep"""

    def __init__(self):
        self.data = []
        self.time = []

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        # get min DOH
        min_DOH = np.amin(problem.q_degree_of_hydration.vector().get_local())
        self.data.append(min_DOH)
        self.time.append(t)


class MaxYieldSensor(Sensor):
    """A sensor that measure the maximum value of the yield function

    A max value > 0 indicates that at some place the stress exceeds the limits"""

    def __init__(self):
        self.data = []
        self.time = []
        self.max = None

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        max_yield = np.amax(problem.q_yield.vector().get_local())
        self.data.append(max_yield)
        self.time.append(t)
        self.data_max(max_yield)


class ReactionForceSensorBottom(Sensor):
    """A sensor that measure the reaction force at the bottom perpendicular to the surface"""

    def __init__(self):
        self.data = []
        self.time = []

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        # boundary condition
        bottom_surface = problem.experiment.boundary_bottom()

        v_reac = df.Function(problem.V)
        if problem.p.dim == 2:
            bc_z = df.DirichletBC(problem.V.sub(1), df.Constant(1.), bottom_surface)
        elif problem.p.dim == 3:
            bc_z = df.DirichletBC(problem.V.sub(2), df.Constant(1.), bottom_surface)

        bc_z.apply(v_reac.vector())
        computed_force = (-df.assemble(df.action(problem.residual, v_reac)))

        self.data.append(computed_force)
        self.time.append(t)


class StressSensor(Sensor):
    """A sensor that measure the stress tensor in at a point"""

    def __init__(self, where):
        """
        Arguments:
            where : Point
                location where the value is measured
        """
        self.where = where
        self.data = []
        self.time = []

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        # get stress
        stress = df.project(problem.stress, problem.visu_space_T, form_compiler_parameters={'quadrature_degree': problem.p.degree})
        self.data.append(stress(self.where))
        self.time.append(t)

class StrainSensor(Sensor):
    """A sensor that measure the strain tensor in at a point"""

    def __init__(self, where):
        """
        Arguments:
            where : Point
                location where the value is measured
        """
        self.where = where
        self.data = []
        self.time = []

    def measure(self, problem, t=1.0):
        """
        Arguments:
            problem : FEM problem object
            t : float, optional
                time of measurement for time dependent problems
        """
        # get strain
        strain = df.project(problem.strain, problem.visu_space_T, form_compiler_parameters={'quadrature_degree': problem.p.degree})
        self.data.append(strain(self.where))
        self.time.append(t)