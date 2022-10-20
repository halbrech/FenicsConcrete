

from fenics_concrete.experimental_setups.experiment import Experiment
from fenics_concrete.helpers import Parameters
import dolfin as df
import numpy as np


class ConcreteBeamReinforced2DExperiment(Experiment):
    def __init__(self, parameters = None):
        p = Parameters()
        p['dim'] = 2
        # boundary values...
        p['T_0'] = 20  # inital concrete temperature
        p['T_boundary'] = 30  # temperature boundary value 1
        p['length'] = 5 # m length
        p['height'] = 1 # height
        p['width'] = 0.8 # width
        p['mesh_density'] = 4  # number of elements in vertical direction, the others are set accordingly
        p['bc_setting'] = 'full' # default boundary setting
        p['reinforcment_y_location'] = 0.25 # distance from bottom in m

        p = p + parameters
        super().__init__(p)

        # initialize variable top_displacement
        self.displ_load = df.Constant(0.0)  # applied via fkt: apply_displ_load(...)




    def setup(self):
        # computing the number of elements in each direcction

        # number of elements in y direction (n_height) musst be computed based on 'reinforcment_y_location'
        # x * height/n_height musst equal reinforcment_y_location for x = 1, 2, 3, ...
        # compute minimum
        n_height_min = int(np.rint(self.p['height']/self.p['reinforcment_y_location']))
        # slightly adjust reinfocement location
        self.p['reinforcment_y_location'] = self.p['height']/n_height_min

        # based on mesh density find closest value
        if self.p['mesh_density'] > n_height_min:
            self.n_height = int(np.rint(self.p['mesh_density']/n_height_min) * n_height_min)
        else:
            self.n_height = int(n_height_min)

        # number of elements based on mesh density value
        self.n_length = int(int(self.p['mesh_density'])/self.p.height*self.p.length)
        if (self.n_length % 2) != 0: # check for odd number
            self.n_length += 1 # n_length must be even for loading example

        if self.p.dim == 2:
             self.mesh = df.RectangleMesh(df.Point(0., 0.), df.Point(self.p.length, self.p.height),
                                          self.n_length,
                                          self.n_height, diagonal='right')
        else:
            raise Exception(f'wrong dimension {self.p.dim} for problem setup')

        # define reinforcement
        self.reinforcement_location = [[(0.0,self.p['length'],self.p['reinforcment_y_location'])]]


    def create_temp_bcs(self,V):

        # Temperature boundary conditions
        T_bc1 = df.Expression('t_boundary', t_boundary=self.p.T_boundary+self.p.zero_C, degree=0)

        temp_bcs = []

        if self.p.bc_setting == 'full':
            # bc.append(DirichletBC(temperature_problem.V, T_bc, full_boundary))
            temp_bcs.append(df.DirichletBC(V, T_bc1, self.boundary_full()))
        else:
            raise Exception(f'parameter[\'bc_setting\'] = {self.p.bc_setting} is not implemented as temperature boundary.')

        return temp_bcs


    def create_displ_bcs(self,V):
        if self.p.dim == 2:
            dir_id = 1
            fixed_bc = df.Constant((0, 0))
        elif self.p.dim == 3:
            dir_id = 2
            fixed_bc = df.Constant((0, 0, 0))

        # define surfaces, full, left, right, bottom, top, none
        def left_support(x, on_boundary):
            return df.near(x[0], 0) and df.near(x[dir_id], 0)
        def right_support(x, on_boundary):
            return df.near(x[0], self.p.length) and df.near(x[dir_id], 0)
        def center_top(x, on_boundary):
            return df.near(x[0], self.p.length/2) and df.near(x[dir_id], self.p.height)



        # define displacement boundary
        displ_bcs = []

        displ_bcs.append(df.DirichletBC(V, fixed_bc, left_support, method='pointwise'))
        displ_bcs.append(df.DirichletBC(V.sub(dir_id), df.Constant(0), right_support, method='pointwise'))
        #displ_bcs.append(df.DirichletBC(V.sub(dir_id), self.displ_load, center_top, method='pointwise'))

        return displ_bcs


    def apply_displ_load(self, displacement_load):
        """Updates the applied displacement load

        Parameters
        ----------
        top_displacement : float
            Displacement of the top boundary in mm, > 0 ; tension, < 0 ; compression
        """

        self.displ_load.assign(df.Constant(displacement_load))
