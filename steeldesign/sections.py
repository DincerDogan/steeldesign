import numpy as np


class SteelSection:
    """a"""

    def __init__(self, code, props):
        """a"""

        self.code = code
        self.area = props[0]
        self.mass = props[1]
        self.ixx = props[2]
        self.zxx = props[3]
        self.sxx = props[4]
        self.rx = props[5]
        self.iyy = props[6]
        self.zyy = props[7]
        self.syy = props[8]
        self.ry = props[9]
        self.j = props[10]
        self.iw = props[11]
        self.kf = props[12]

    def calc_section_properties(self):
        """a"""

        pass

    def load_section_properties(self):
        """a"""

        pass

    def calc_ze(self, axis):
        """a"""

        if axis == 'x':
            z = self.zxx
            s = self.sxx
            (compact_x, lambda_s,
             lambda_lims, plate_type) = self.bending_compact_x()

        elif axis == 'y':
            z = self.zyy
            s = self.syy
            (compact_x, lambda_s,
             lambda_lims, plate_type) = self.bending_compact_y()

        if compact_x == 'C':
            return min(1.5 * z, s)

        elif compact_x == 'NC':
            zc = min(1.5 * z, s)
            lambda_sy = lambda_lims[1]
            lambda_sp = lambda_lims[0]

            return z + (zc - z) * (lambda_sy - lambda_s) / (
                lambda_sy - lambda_sp)

        elif compact_x == 'S':
            if plate_type in ['Uniform1', 'Uniform2']:
                return z * lambda_lims[1] / lambda_s

            elif plate_type == 'CHS':
                z1 = z * np.sqrt(lambda_lims[1] / lambda_s)
                z2 = z * (2 * lambda_lims[1] / lambda_s) ** 2
                return min(z1, z2)

            else:
                return z * (lambda_lims[1] / lambda_s) ** 2

    def calc_phi_msx(self):
        """a"""

        return self.code.phi_member * self.calc_msx()


class UBSection(SteelSection):
    """Class for Universal Beam sections.

    :param string name: Name of the UB section
    :param float d: Total depth of the UB section [mm]
    :param float bf: Flange width of the UB section [mm]
    :param float tf: Flange thickness of the UB section [mm]
    :param float tw: Web thickness of the UB section [mm]
    :param float r: Root radius of the UB section [mm]
    :param float fyf: Flange yield strength of the UB section [MPa]
    :param float fyw: Web yield strength of the UB section [MPa]
    :param props: List of section properties to import
    :type props: list[float]
    """

    def __init__(self, code, name, d, bf, tf, tw, r, fyf, fyw,
                 props=[None] * 13):
        """Inits the UBSection class."""

        super().__init__(code, props)

        self.name = name
        self.d = d
        self.bf = bf
        self.tf = tf
        self.tw = tw
        self.r = r
        self.fyf = fyf
        self.fyw = fyw

    def calc_dw(self):
        """Returns the depth of the web (d - 2 * tf).

        :returns: Depth of the web [mm]
        :rtype: float
        """

        return self.d - 2 * self.tf

    def calc_web_slenderness(self):
        """Returns the slenderness of the web (dw / tw).

        :returns: Web slenderness
        :rtype: float
        """

        return self.calc_dw() / self.tw

    def calc_flange_slenderness(self):
        """Returns the slenderness of the flange ((bf - tw) / (2 * tf)).

        :returns: Flange slenderness
        :rtype: float
        """

        return (self.bf - self.tw) / (2 * self.tf)

    def calc_msx(self):
        """Returns the unfactored section moment capacity about the x-axis
        [kN.m]

        Ms = min(fyf, fyw) * Zex

        :returns: Unfactored section moment capacity about the x-axis
        :rtype: float
        """

        return min(self.fyf, self.fyw) * self.calc_ze(axis='x') / 1e6

    def calc_msy(self):
        """Returns the unfactored section moment capacity about the y-axis
        [kN.m]

        Ms = min(fyf, fyw) * Zey

        :returns: Unfactored section moment capacity about the y-axis
        :rtype: float
        """

        return min(self.fyf, self.fyw) * self.calc_ze(axis='y') / 1e6

    def bending_compact_x(self):
        """Returns the compactness of the section for bending about the x-axis.

        :returns: Compactness of the section for bending about the x-axis
            *('C', 'NC', 'S'), section slenderness, slenderness limits and the
            plate type
        :rtype: tuple(string, float, tuple(float, float, float), string)
        """

        # flange slenderness
        lambda_f = self.calc_flange_slenderness() * np.sqrt(self.fyf / 250)
        lambda_f_lims = self.code.plate_slenderness_bending('Uniform1', 'HR')
        ratio_f = lambda_f / lambda_f_lims[1]

        # web slenderness
        lambda_w = self.calc_web_slenderness() * np.sqrt(self.fyw / 250)
        lambda_w_lims = self.code.plate_slenderness_bending('Bending2', 'HR')
        ratio_w = lambda_w / lambda_w_lims[1]

        # section slenderness
        if ratio_f > ratio_w:
            lambda_s = lambda_f
            lambda_lims = lambda_f_lims
            plate_type = 'Uniform1'
        else:
            lambda_s = lambda_w
            lambda_lims = lambda_w_lims
            plate_type = 'Bending2'

        # compactness
        if lambda_s < lambda_lims[0]:
            compact = 'C'
        elif lambda_s < lambda_lims[1]:
            compact = 'NC'
        else:
            compact = 'S'

        return(compact, lambda_s, lambda_lims, plate_type)
