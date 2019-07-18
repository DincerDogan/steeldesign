from steeldesign.sections import UBSection

ub1 = UBSection(name='250UB25', d=203, bf=133, tf=7.8, tw=5.8, r=10, fyf=320, fyw=320)

print(ub1.calc_dw())
print(ub1.calc_flange_slenderness())
print(ub1.calc_web_slenderness())
