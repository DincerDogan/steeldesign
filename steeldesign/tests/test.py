from steeldesign.codes import DesignCode
from steeldesign.sections import UBSection

as4100 = DesignCode()

ub1 = UBSection(code=as4100, name='250UB25', d=203, bf=133, tf=7.8, tw=5.8, r=10, fyf=320, fyw=320)

ub1.zxx = 233e5
ub1.sxx = 259e3

print(ub1.calc_phi_msx())
