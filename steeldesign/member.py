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

    def calc_phi_mbx(self, bmd, shear_centre, alpha_m=None):
        """Calculates phiMbx for the member for each segment based on the
        applied restraints and supplied bending moment diagram *bmd*.

        :param bmd: Bending moment diagram for the member of size *(n x 2)*
        :type bmd: :class:`numpy.ndarray`
        :param shear_centre: List of booleans defining whether or not the load
            is applied at the shear centre for each segment
        :type shear_centre: list[bool]
        :param alpha_m: Optional list of alpha_m values to override those
            calculated from the bmd
        :type alpha_m: list[float]

        :raises Exception: Size of shear_centre is not equal to the number of
            segments
        :raises Exception: Size of alpha_m is not equal to the number of
            segments
        """

        # generate segments
        segments = []

        for i in range(len(self.restraints) - 1):
            segments.append(
                Segment(self.restraints[i], self.restraints[i+1], bmd))

        # check length of shear_centre equals number of segments
        if len(shear_centre) != len(segments):
            raise Exception('Size of shear_centre must equal segment number')

        # check length of alpha_m equals number of segments
        if alpha_m is not None:
            if len(alpha_m) != len(segments):
                raise Exception('Size of alpha_m must equal segment number')

        # calculate alpha_m values
        for (i, segment) in enumerate(segments):
            if alpha_m is None:
                segment.calc_alpha_m()
            else:
                segment.alpha_m = alpha_m[i]

        # calculate mbx for each segment
        for segment in segments:
            # calculate le
            pass


class Segment:
    """a

    :param restraint1: Restraint at the start of the segment
    :type restraint1: :class:`steeldesign.codes.Restraint`
    :param restraint2: Restraint at the end of the segment
    :type restraint2: :class:`steeldesign.codes.Restraint`
    :param bmd: Bending moment diagram for the member of size *(n x 2)*
    :type bmd: :class:`numpy.ndarray`

    :cvar restraint1: Restraint at the start of the segment
    :vartype restraint1: :class:`steeldesign.codes.Restraint`
    :cvar restraint2: Restraint at the end of the segment
    :vartype restraint2: :class:`steeldesign.codes.Restraint`
    :cvar bmd_segment: Bending moment diagram for the segment of size *(n x 2)*
    :type bmd_segment: :class:`numpy.ndarray`
    :cvar float alpha_m: Alpha_m value for the segment
    """

    def __init__(self, restraint1, restraint2, bmd):
        """Inits the Segment class."""

        self.restraint1 = restraint1
        self.restraint2 = restraint2

        bmd_segment = []

        # add start point for the segment bmd
        bmd_segment.append(
            [restraint1.pos, np.interp(restraint1.pos, bmd[:, 0], bmd[:, 1])])

        # loop through bending moments
        for bm in bmd:
            if (bm[0] > restraint1.pos) and (bm[0] < restraint2.pos):
                bmd_segment.append(bm)

        # add end point for the segment bmd
        bmd_segment.append(
            [restraint2.pos, np.interp(restraint2.pos, bmd[:, 0], bmd[:, 1])])

        self.bmd_segment = np.array(bmd_segment)

    def calc_alpha_m(self):
        """Calculates the alpha_m value for the segment based on the bending
        moment diagram.

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
            bm_quarters.append(
                np.interp(start_pos + mult * length,
                          self.bmd_segment[:, 0],
                          self.bmd_segment[:, 1]))

        # calculate calc_alpha_m
        self.alpha_m = min(2.5, 1.7 * bm_max / np.sqrt(
            bm_quarters[0] ** 2 + bm_quarters[1] ** 2 + bm_quarters[2] ** 2))
