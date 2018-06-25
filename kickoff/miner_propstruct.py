#!/usr/bin/env python
"""
MPDS API usage example:
the relationship between a physical property and the atomic structure,
using the Pearson and Kendall's tau coefficients

https://developer.mpds.io/#QSAR-QSPR
"""

from __future__ import division

import numpy as np
import pandas as pd
from ase.data import chemical_symbols, covalent_radii

from mpds_client import MPDSDataRetrieval


def get_APF(ase_obj):
    """
    Example crystal structure descriptor:
    https://en.wikipedia.org/wiki/Atomic_packing_factor
    """
    volume = 0.0
    for atom in ase_obj:
        volume += 4/3 * np.pi * covalent_radii[chemical_symbols.index(atom.symbol)]**3
    return volume/abs(np.linalg.det(ase_obj.cell))

def get_Wiener(ase_obj):
    """
    Example crystal structure descriptor:
    https://en.wikipedia.org/wiki/Wiener_index
    defined per a unit cell
    """
    return np.sum(ase_obj.get_all_distances()) * 0.5

client = MPDSDataRetrieval()

dfrm = client.get_dataframe({"classes": "transitional, oxide", "props": "isothermal bulk modulus"})
dfrm = dfrm[np.isfinite(dfrm['Phase'])]
dfrm = dfrm[dfrm['Units'] == 'GPa']
dfrm = dfrm[dfrm['Value'] > 0]

phases = set(dfrm['Phase'].tolist())
answer = client.get_data(
    {"props": "atomic structure"},
    phases=phases,
    fields={'S':['phase_id', 'entry', 'chemical_formula', 'cell_abc', 'sg_n', 'setting', 'basis_noneq', 'els_noneq']}
)

descriptors = []

for item in answer:
    crystal = MPDSDataRetrieval.compile_crystal(item, 'ase')
    if not crystal: continue
    descriptors.append(( item[0], get_APF(crystal), get_Wiener(crystal) ))

descriptors = pd.DataFrame(descriptors, columns=['Phase', 'APF', 'Wiener'])

d1 = descriptors.groupby('Phase')['APF'].mean().to_frame().reset_index()
d2 = descriptors.groupby('Phase')['Wiener'].mean().to_frame().reset_index()

dfrm = dfrm.groupby('Phase')['Value'].mean().to_frame().reset_index()
dfrm = dfrm.merge(d1, how='outer', on='Phase')
dfrm = dfrm.merge(d2, how='outer', on='Phase')

dfrm.drop('Phase', axis=1, inplace=True)
dfrm.rename(columns={'Value': 'Prop'}, inplace=True)

corr_pearson = dfrm.corr(method='pearson')
corr_kendall = dfrm.corr(method='kendall')

print("Pearson. Prop vs. APF = \t%s" % corr_pearson.loc['Prop']['APF'])
print("Pearson. Prop vs. Wiener = \t%s" % corr_pearson.loc['Prop']['Wiener'])
print("Kendall Tau. Prop vs. APF = \t%s" % corr_kendall.loc['Prop']['APF'])
print("Kendall Tau. Prop vs. Wiener = \t%s" % corr_kendall.loc['Prop']['Wiener'])
