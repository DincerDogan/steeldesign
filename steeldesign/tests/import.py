import csv
from steeldesign.codes import DesignCode
from steeldesign.sections import UBSection

as4100 = DesignCode()
ubs = []

with open('ub.csv') as f:
    reader = csv.reader(f, delimiter=',')

    row_num = 0

    for (i, row) in enumerate(reader):
        if i == 0:
            continue
        elif row[0] == '':
            continue

        name = row[0]
        d = float(row[1])
        bf = float(row[2])
        tf = float(row[3])
        tw = float(row[4])
        r = float(row[5])
        area = float(row[9])
        ixx = float(row[10])
        zxx = float(row[11])
        sxx = float(row[12])
        rx = float(row[13])
        iyy = float(row[14])
        zyy = float(row[15])
        syy = float(row[16])
        ry = float(row[17])
        j = float(row[18])
        iw = float(row[19])
        fyf = float(row[20])
        fyw = float(row[21])
        kf = float(row[22])

        props = [area, None, ixx, zxx, sxx, rx, iyy, zyy, syy, ry, j, iw, kf]

        ubs.append(UBSection(code=as4100, name=name, d=d, bf=bf, tf=tf, tw=tw,
                             r=r, fyf=fyf, fyw=fyw, props=props))

for ub in ubs:
    print('{0}:\t{1:0.1f}'.format(ub.name, ub.calc_phi_msx()))

for ub in ubs:
    compact, _, _, plate = ub.bending_compact_x()
    print('{0}:\t{1}\t{2}'.format(ub.name, compact, plate))
