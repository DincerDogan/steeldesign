class SteelSection:
    """a"""

    def __init__(self, code):
        """a"""

        self.code = code
        self.area = 0
        self.mass = 0
        self.ixx = 0
        self.zxx = 0
        self.sxx = 0
        self.rx = 0
        self.iyy = 0
        self.zyy = 0
        self.syy = 0
        self.ry = 0
        self.j = 0
        self.iw = 0
        self.kf = 0

    def calc_section_properties(self):
        """a"""

        pass

    def load_section_properties(self):
        """a"""

        pass

    def calc_zex(self):
        """a"""

        return min(1.5 * self.zxx, self.sxx)

    def calc_phi_msx(self):
        """a"""

        return self.code.phi * self.calc_msx()


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
    """

    def __init__(self, code, name, d, bf, tf, tw, r, fyf, fyw):
        """Inits the UBSection class."""

        super().__init__(code)

        self.name = name
        self.d = d
        self.bf = bf
        self.tf = tf
        self.tw = tw
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
        """Returns the unfactored section moment capacity about the xx-axis
        [kN.m]

        Ms = min(fyf, fyw) * Zex

        :returns: Unfactored section moment capacity about the xx-axis
        :rtype: float
        """

        return min(self.fyf, self.fyw) * self.calc_zex() / 1e6
