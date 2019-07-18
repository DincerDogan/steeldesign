class SteelSection:
    """a"""

    def __init__(self):
        """a"""

        self.area = 0
        self.mass = 0
        self.ixx = 0
        self.zxx = 0
        self.sxx = 0
        self.zex = 0
        self.compact_x = 'C'
        self.rx = 0
        self.iyy = 0
        self.zyy = 0
        self.syy = 0
        self.zey = 0
        self.compact_y = 'C'
        self.ry = 0
        self.j = 0
        self.iw = 0
        self.kf = 0

    def calculate_section_properties(self):
        """a"""

        pass

    def load_section_properties(self):
        """a"""

        pass


class UBSection(SteelSection):
    """Class for Universal Beam sections.

    :param string name: Name of the UB section
    :param float d: Total depth of the UB section
    :param float bf: Flange width of the UB section
    :param float tf: Flange thickness of the UB section
    :param float tw: Web thickness of the UB section
    :param float r: Root radius of the UB section
    :param float fyf: Flange yield strength of the UB section
    :param float fyw: Web yield strength of the UB section
    """

    def __init__(self, name, d, bf, tf, tw, r, fyf, fyw):
        """Inits the UBSection class."""

        self.name = name
        self.d = d
        self.bf = bf
        self.tf = tf
        self.tw = tw
        self.fyf = fyf
        self.fyw = fyw

    def calc_dw(self):
        """Returns the depth of the web (d - 2 * tf).

        :returns: Depth of the web
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
