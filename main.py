import numpy as np
import matplotlib.pyplot as plt
import subprocess as sp
from time import sleep


WIND_SPEED = 7  # in meters per second
REYNOLDS = 200000
turbine_angles = {.2: (61., .700),  # Element twist angles and chord lengths by radius
                  1.: (74.3, .71),
                  2.: (84.9, .44),
                  3.: (89.1, .30),
                  4.: (91.3, .23),
                  5.: (92.6, .19)}

# avoid xfoil shell overhead
startupinfo = sp.STARTUPINFO()
startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW

ps = sp.Popen(['xfoil.exe'],
              stdin=sp.PIPE,
              stdout=0,
              stderr=None,
              startupinfo=startupinfo,
              encoding='utf8')


def issue_cmd(cmd, echo=False):
    ps.stdin.write(cmd + '\n')
    if echo: print(cmd)


issue_cmd('naca0012')
issue_cmd('pane')
issue_cmd('oper')
issue_cmd('visc')
issue_cmd(str(REYNOLDS))
issue_cmd('iter')
issue_cmd('200')
issue_cmd('pacc')
issue_cmd('try')
issue_cmd('dump')
issue_cmd('aseq')
issue_cmd('21.12')
issue_cmd('21.12')
issue_cmd('0')
issue_cmd('')
issue_cmd('QUIT')


class Turbine:

    def __init__(self, no_blades=3, radius=5, tsr=8, aerofoil="naca0012", elements=turbine_angles):
        self.radius = radius
        self.no_blades = no_blades
        self.tip_speed_ratio = tsr
        self.aerofoil = aerofoil
        self.xfoil = {}
        self.elements = elements
        self.induction = {}

    # read lift and drag coefficients data
    def read_xfoil(self, filename, header_lines=11):
        with open(filename) as f:
            lines = f.readlines()[header_lines:]
            for line in lines:
                alpha, lift_coeff, drag_coeff = line.strip().split()[:3]
                self.xfoil[np.deg2rad(float(alpha))] = (float(lift_coeff), float(drag_coeff))

    def get_coeffs_for_alpha(self, alpha):
        # alpha in radians
        try:
            return self.xfoil[alpha]
        except KeyError:
            # Si l'angle d'incidence est hors le domaine
            if min(self.xfoil.keys()) > alpha or max(self.xfoil.keys()) < alpha:
                print("Angle d'incidence non-inclu dans les données")
                return 0, 0
            else:
                # Prendre la valeur la plus proche de l'angle d'incidence
                return self.xfoil[min(self.xfoil.keys(), key=lambda x: abs(x - alpha))]

    def bem_calculate(self, iterations):

        # data is a tuple: (twist angle, chord length)
        for radius, (twist_angle, chord) in self.elements.items():
            # Initialize iteration
            twist_angle = np.deg2rad(twist_angle)
            sigma = (self.no_blades * chord) / (2 * np.pi * radius)
            beta = (np.pi / 2) - ((2 / 3) * np.arctan(1 / self.tip_speed_ratio))
            alpha = round(twist_angle - beta, 2)
            # lift_coeff =

            # Guess initial axial and angular induction coefficients
            # axial_a = 1 / (1 + (4 * np.cos(beta) ** 2) / (sigma * lift_coeff * np.sin(beta)))
            # angular_a = (1 - 3 * axial_a) / (4 * axial_a - 1)
            # self.induction[radius] = [(axial_a, angular_a)]

            # Iteration
            # for it in range(iterations):
            #     beta = np.arctan(1 / ((self.tip_speed_ratio * (1 + angular_a)) / (1 - axial_a)))
            #     alpha = round(twist_angle - beta, 2)
                # lift_coeff =
                #
                # axial_a = 1 / (1 + (4 * np.cos(beta) ** 2) / (sigma * lift_coeff * np.sin(beta)))
                # angular_a = (1 - axial_a) * (sigma * lift_coeff) / (4 * self.tip_speed_ratio * np.cos(beta))

                # Store steps for convergence analysis
                # self.induction[radius].append((axial_a, angular_a))


turb = Turbine()
turb.read_xfoil("xfoil_data")
turb.bem_calculate(40)

# plt.plot([i[0] for i in turb.induction[5]], 'r')
# plt.plot([i[1] for i in turb.induction[5]], 'g')
# plt.show()
exit()

# print(find_coefficients(airfoil='naca0012', alpha=0.45, Reynolds=REYNOLDS, NACA=True)['CL'])
