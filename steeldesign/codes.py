class DesignCode:
    """a"""

    def __init__(self):
        """a"""

        self.name = 'AS4100-1998'
        self.phi_member = 0.9
        self.elastic_modulus = 200e3
        self.shear_modulus = 80e3

    def plate_slenderness_bending(self, plate_type, res_stress):
        """Returns the plate slenderness limits for bending given a plate type and a residual
        stress class.

        T.5.2 AS4100-1998

        :param string plate_type: Type of plate - 'Uniform1', 'Bending1', 'Uniform2', 'Bending2',
            'CHS'
        :param string res_stress: Residual stress class - 'SR', 'HR', 'LW, 'CF', 'HW'
        :returns: Plate slenderness limits for bending *(plasticity limit, yield limit, deformation
            limit)*
        :rtype: tuple(float, float, float)
        """

        slender_dict = {
            'Uniform1': {
                'SR': (10, 16, 35),
                'HR': (9, 16, 35),
                'LW': (8, 15, 35),
                'CF': (8, 15, 35),
                'HW': (8, 14, 35),
            },
            'Bending1': {
                'SR': (10, 25, None),
                'HR': (9, 25, None),
                'LW': (8, 22, None),
                'CF': (8, 22, None),
                'HW': (8, 22, None),
            },
            'Uniform2': {
                'SR': (30, 45, 90),
                'HR': (30, 45, 90),
                'LW': (30, 40, 90),
                'CF': (30, 40, 90),
                'HW': (30, 35, 90),
            },
            'Bending2': {
                'SR': (82, 115, None),
                'HR': (82, 115, None),
                'LW': (82, 115, None),
                'CF': (82, 115, None),
                'HW': (82, 115, None),
            },
            'CHS': {
                'SR': (50, 120, None),
                'HR': (50, 120, None),
                'LW': (42, 120, None),
                'CF': (42, 120, None),
                'HW': (42, 120, None),
            },
        }

        return slender_dict[plate_type][res_stress]


class SteelGrade:
    """a"""

    def __init__(self, grade):
        """a"""

        self.grade = grade

    def get_yield_stress(self, t):
        """a"""

        if self.grade == '3679.1-350':
            if t <= 11:
                return 360
            elif t < 40:
                return 340
            elif t >= 40:
                return 330
        elif self.grade == '3679.1-300':
            if t < 11:
                return 320
            elif t <= 17:
                return 300
            elif t >= 17:
                return 280

    def get_tensile_strength(self):
        """a"""

        if self.grade == '3679.1-350':
            return 480
        elif self.grade == '3679.1-300':
            return 440


class Restraint:
    """a"""

    def __init__(self, rtype, pos):
        """Inits the Restraint class.

        :param string rtype: Restraint type (**F**ixed, **P**artial, **R**otational, **L**ateral,
            '**U**nrestrained')
        :param float pos: Relative length along member at which the restraint is applied
            *(0 <= pos <= 1)*
        """

        self.rtype = rtype
        self.pos = pos
