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
        """a

        Cl. 5.2.3, Cl. 5.2.4, Cl. 5.2.5 AS4100-1998
        """

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

        return self.code.phi_member * self.get_yield_stress() * self.calc_ze(
            axis='x') / 1e6

    def calc_phi_msy(self):
        """a"""

        return self.code.phi_member * self.get_yield_stress() * self.calc_ze(
            axis='y') / 1e6


class UBSection(SteelSection):
    """Class for Universal Beam sections.

    :param string name: Name of the UB section
    :param float d: Total depth of the UB section [mm]
    :param float bf: Flange width of the UB section [mm]
    :param float tf: Flange thickness of the UB section [mm]
    :param float tw: Web thickness of the UB section [mm]
    :param float r: Root radius of the UB section [mm]
    :param grade: Steel grade
    :type grade: :class:`~steeldesign.codes.SteelGrade`
    :param props: List of section properties to import
    :type props: list[float]
    """

    def __init__(self, code, name, d, bf, tf, tw, r, grade, props=[None] * 13):
        """Inits the UBSection class."""

        super().__init__(code, props)

        self.name = name
        self.d = d
        self.bf = bf
        self.tf = tf
        self.tw = tw
        self.r = r
        self.grade = grade

        # calculate yield stresses
        self.fyf = self.grade.get_yield_stress(self.tf)
        self.fyw = self.grade.get_yield_stress(self.tw)

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

    def get_yield_stress(self):
        """Returns the yield stress of the section

        fy = min(fyf, fyw)

        :returns: Yield stress of the section
        :rtype: float
        """

        return min(self.fyf, self.fyw)

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

    def bending_compact_y(self):
        """Returns the compactness of the section for bending about the y-axis.

        :returns: Compactness of the section for bending about the y-axis
            *('C', 'NC', 'S'), section slenderness, slenderness limits and the
            plate type
        :rtype: tuple(string, float, tuple(float, float, float), string)
        """

        # flange slenderness
        lambda_s = self.calc_flange_slenderness() * np.sqrt(self.fyf / 250)
        lambda_lims = self.code.plate_slenderness_bending('Bending1', 'HR')
        plate_type = 'Bending1'

        # compactness
        if lambda_s < lambda_lims[0]:
            compact = 'C'
        elif lambda_s < lambda_lims[1]:
            compact = 'NC'
        else:
            compact = 'S'

        return(compact, lambda_s, lambda_lims, plate_type)

    def full_restraint_length_simple(self, beta_m=-1):
        """Returns the maximum segment length for which the section is
        considered fully laterally restrained as defined by Cl. 5.3.2.4
        AS4100-1998.

        :param float beta_m: Factor dependent on the bending moments within the
            segment
        :returns: Maximum segment length for which the section is considered
            fully laterally restrained
        :rtype: float

        The ratio beta_m shall be taken as one of the following as appropriate:
        * -1;
        * -0.8 for segments with transverse loads; or
        * the ratio of the smaller to the larger end moments in the length (l),
        (positive when the segment is bent in reverse curvature and negative
        when bent in single curvature) for segments without transverse loads.
        """

        return self.ry * (80 + 50 * beta_m) * np.sqrt(
            250 / self.get_yield_stress())
