import numpy as np


class Member:
    """a"""

    def __init__(self, section, length, restraints):
        """Inits the Member class."""

        self.section = section
        self.length = length
        self.restraints = []

        for restraint in restraints:
            self.add_restraint(restraint)

    def add_restraint(self, restraint):
        """a"""

        # add the restraint to the list
        self.restraints.append(restraint)

        # reorder restraints
        self.restraints.sort(key=lambda r: r.pos)

    def calc_phi_mbx(self, bmd, load_position, alpha_m=None):
        """Calculates phiMbx for the member for each segment based on the applied restraints and
        supplied bending moment diagram *bmd*.

        :param bmd: Bending moment diagram for the member of size *(n x 2)*
        :type bmd: :class:`numpy.ndarray`
        :param load_position: List of strings defining the load position within each segment i.e.
            'WS' - within & shear centre; 'ES' - end & shear centre; 'WT' - within & top flange;
            'ET' - end & top flange
        :type load_position: list[strings]
        :param alpha_m: Optional list of alpha_m values to override those calculated from the bmd
        :type alpha_m: list[float]
        :returns: A list of phiMbx values for each segment
        :rtype: list[float]

        :raises Exception: Size of load_position is not equal to the number of segments
        :raises Exception: Size of alpha_m is not equal to the number of segments
        """

        # check length of load_position equals number of segments
        if len(load_position) != len(self.restraints) - 1:
            raise Exception('Size of load_position must equal number of segments')

        # check length of alpha_m equals number of segments
        if alpha_m is not None:
            if len(alpha_m) != len(self.restraints) - 1:
                raise Exception('Size of alpha_m must equal number of segments')

        # generate segments
        segments = []

        for i in range(len(self.restraints) - 1):
            segments.append(Segment(self.length, self.restraints[i], self.restraints[i+1],
                                    load_position[i], bmd, self.section))

        # calculate alpha_m values
        for (i, segment) in enumerate(segments):
            if alpha_m is None:
                segment.calc_alpha_m()
            else:
                segment.alpha_m = alpha_m[i]

        phi_mbx = []

        # calculate phi_mbx for each segment
        for segment in segments:
            # calculate le
            le = segment.calc_effective_length()
            alpha_m = segment.alpha_m

            phi_mbx.append(self.section.calc_phi_mbx(le=le, alpha_m=alpha_m))

        return phi_mbx


class Segment:
    """a

    :param float member_length: Total physical length of the memeber
    :param restraint1: Restraint at the start of the segment
    :type restraint1: :class:`steeldesign.codes.Restraint`
    :param restraint2: Restraint at the end of the segment
    :type restraint2: :class:`steeldesign.codes.Restraint`
    :param string load_position: Strings defining the load position
    :param bmd: Bending moment diagram for the member of size *(n x 2)*
    :type bmd: :class:`numpy.ndarray`
    :param section: Steel cross section object
    :type: :class:`steeldesign.sections.SteelSection`

    :cvar float segment_length: Physical length of the segment
    :cvar restraint1: Restraint at the start of the segment
    :vartype restraint1: :class:`steeldesign.codes.Restraint`
    :cvar restraint2: Restraint at the end of the segment
    :vartype restraint2: :class:`steeldesign.codes.Restraint`
    :cvar string load_position: Strings defining the load position
    :cvar bmd_segment: Bending moment diagram for the segment of size *(n x 2)*
    :type bmd_segment: :class:`numpy.ndarray`
    :cvar float alpha_m: Alpha_m value for the segment
    :cvar section: Steel cross section object
    :vartype: :class:`steeldesign.sections.SteelSection`
    """

    def __init__(self, member_length, restraint1, restraint2, load_position,
                 bmd, section):
        """Inits the Segment class."""

        self.segment_length = member_length * (restraint2.pos - restraint1.pos)
        self.restraint1 = restraint1
        self.restraint2 = restraint2
        self.load_position = load_position
        self.section = section

        bmd_segment = []

        # add start point for the segment bmd
        bmd_segment.append([restraint1.pos, np.interp(restraint1.pos, bmd[:, 0], bmd[:, 1])])

        # loop through bending moments
        for bm in bmd:
            if (bm[0] > restraint1.pos) and (bm[0] < restraint2.pos):
                bmd_segment.append(bm)

        # add end point for the segment bmd
        bmd_segment.append([restraint2.pos, np.interp(restraint2.pos, bmd[:, 0], bmd[:, 1])])

        self.bmd_segment = np.array(bmd_segment)

    def calc_alpha_m(self):
        """Calculates the alpha_m value for the segment based on the bending moment diagram.

        Cl. 5.6.1.1(a) (iii) AS4100-1998
        """

        # get start pos, end pos and length of segment
        start_pos = self.bmd_segment[0][0]
        end_pos = self.bmd_segment[-1][0]
        length = end_pos - start_pos

        # get max bending moment
        bm_max = self.bmd_segment.max(axis=0)[1]

        # get bending moment at quarter points
        bm_quarters = []
        for i in range(3):
            mult = 0.25 * (i + 1)
            bm_quarters.append(np.interp(
                start_pos + mult * length, self.bmd_segment[:, 0], self.bmd_segment[:, 1])
            )

        # calculate calc_alpha_m
        self.alpha_m = min(2.5, 1.7 * bm_max / np.sqrt(
            bm_quarters[0] ** 2 + bm_quarters[1] ** 2 + bm_quarters[2] ** 2)
        )

    def calc_effective_length(self):
        """Returns the effective length of the segment.

        Cl. 5.6.3 AS4100-1998

        :returns: Segment effective length
        :rtype: float

        :raises Exception: If the restraint code is incorrect
        :raises Exception: If the load_position code is incorrect
        """

        # determine restraint code
        res_code = self.restraint1.rtype + self.restraint2.rtype

        # calculate twist restraint factor
        if self.iscode(res_code, ['FF', 'FL', 'LL', 'FU']):
            kt = 1

        elif self.iscode(res_code, ['FP', 'PL', 'PU']):
            d1 = self.section.calc_dw()
            tf = self.section.get_tf()
            tw = self.section.get_tw()
            nw = self.section.get_nw()

            kt = 1 + (d1 / self.segment_length) * (tf / 2 / tw) ** 3 / nw

        elif self.iscode(res_code, ['PP']):
            kt = 1 + 2 * (d1 / self.segment_length) * (tf / 2 / tw) ** 3 / nw

        else:
            raise Exception('Restraint code {0} is invalid'.format(res_code))

        # calculate load height factor
        if self.load_position in ['WS', 'ES']:
            kl = 1
        elif self.load_position == 'WT':
            if self.iscode(res_code, ['FU', 'PU']):
                kl = 2
            else:
                kl = 1.4
        elif self.load_position == 'ET':
            if self.iscode(res_code, ['FU', 'PU']):
                kl = 2
            else:
                kl = 1
        else:
            raise Exception('Load position code {0} is invalid'.format(self.load_position))

        # calculate lateral rotation restraint factor
        # TODO: add ends with lateral rotation restraints
        kr = 1

        return kt * kl * kr * self.segment_length

    def iscode(self, res, codes):
        """Determines if the restraint type 'res' corresponds to any of the list of restraint
        'codes'. Note that the string code may be unordered, e.g. 'PF' is equal to 'FP'.

        :param string res: Restraint code to check
        :param codes: List of codes to check against
        :type codes: list[string]
        :returns: Whether or not 'res' matches 'code' (unordered)
        :rtype: bool
        """

        for code in codes:
            if (res == code or res[::-1] == code):
                return True

        return False
