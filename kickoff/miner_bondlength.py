#!/usr/bin/env python

import pandas as pd

from mpds_client import MPDSDataRetrieval
from MPDSExport import export_plot


def calculate_lengths(ase_obj, elA, elB, limit=4):
    assert elA != elB
    lengths = []
    for n, atom in enumerate(ase_obj):
        if atom.symbol == elA:
            for m, neighbor in enumerate(ase_obj):
                if neighbor.symbol == elB:
                    dist = round(ase_obj.get_distance(n, m), 2) # NB occurrence <-> rounding
                    if dist < limit:
                        lengths.append(dist)
    return lengths

client = MPDSDataRetrieval()

answer = client.get_data(
    {"elements": "U-O", "props": "atomic structure"},
    fields={'S':['phase_id', 'entry', 'chemical_formula', 'cell_abc', 'sg_n', 'setting', 'basis_noneq', 'els_noneq']}
)

lengths = []

for item in answer:
    crystal = MPDSDataRetrieval.compile_crystal(item, 'ase')
    if not crystal: continue
    lengths.extend( calculate_lengths(crystal, 'U', 'O') )

dfrm = pd.DataFrame(sorted(lengths), columns=['length'])
dfrm['occurrence'] = dfrm.groupby('length')['length'].transform('count')
dfrm.drop_duplicates('length', inplace=True)

export_plot(dfrm, ['length', 'occurrence'], 'bar')
