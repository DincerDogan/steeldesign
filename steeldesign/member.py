
import numpy as np


class Member:
    """a"""

    def __init__(self, section, length, restraints):
        """Inits the Member class."""

        self.section = section
        self.length = length
        self.restraints = []

        for restraint in restraints:
            self.add_restraint()

    def add_restraint(self, restraint):
        """a"""

        # add the restraint to the list
        self.restraints.append(restraint)

        # reorder restraints
        self.restraints.sort(key=lambda r: r.pos)

    def calc_phi_mbx(self, bmd):
        """a"""

        # determine alpha_m based on bmd
        pass
