import numpy as np
from steeldesign.codes import DesignCode, SteelGrade, Restraint
from steeldesign.sections import UBSection
from steeldesign.member import Member

as4100 = DesignCode()
grade = SteelGrade('3679.1-300')

name = '250UB37'
d = 256
bf = 146
tf = 10.9
tw = 6.4
r = 8.9
area = 4750
ixx = 55700000
zxx = 435000
sxx = 486000
rx = 108
iyy = 5660000
zyy = 77500
syy = 119000
ry = 34.5
j = 158000
iw = 85200000000
kf = 1

props = [area, None, ixx, zxx, sxx, rx, iyy, zyy, syy, ry, j, iw, kf]

section = UBSection(code=as4100, name=name, d=d, bf=bf, tf=tf, tw=tw,
                    r=r, grade=grade, props=props)

end1 = Restraint('F', 0)
mid = Restraint('L', 0.6)
end2 = Restraint('F', 1)

member = Member(section=section, length=5000, restraints=[end1, mid, end2])

bmd = np.array([[0,	0],
                [0.05, 9.5],
                [0.1, 18],
                [0.15, 25.5],
                [0.2, 32],
                [0.25, 37.5],
                [0.3, 42],
                [0.35, 45.5],
                [0.4, 48],
                [0.45, 49.5],
                [0.5, 50],
                [0.55, 49.5],
                [0.6, 48],
                [0.65, 45.5],
                [0.7, 42],
                [0.75, 37.5],
                [0.8, 32],
                [0.85, 25.5],
                [0.9, 18],
                [0.95, 9.5],
                [1,	0]])

member.calc_phi_mbx(bmd=bmd)
