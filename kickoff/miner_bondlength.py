#!/usr/bin/env python
"""
MPDS API usage example:
the uranium-oxygen chemical bond length distribution

https://developer.mpds.io/#Probability-density
"""

import polars as pl

from mpds_client import MPDSDataRetrieval, MPDSExport
from ase.neighborlist import neighbor_list

def calculate_lengths(ase_obj, elA, elB, limit=4):
    assert elA != elB
    nlist = NeighborList([limit / 2] * len(ase_obj), self_interaction=False, bothways=True)
    nlist.update(ase_obj)
    lengths = []
    for n, atom in enumerate(ase_obj):
        if atom.symbol == elA:
            indices, _ = nlist.get_neighbors(n)
            for m in indices:
                if ase_obj[m].symbol == elB:
                    dist = round(ase_obj.get_distance(n,m), 2)
                    lengths.append(dist)
    return lengths

client = MPDSDataRetrieval()

answer = client.get_data(
    {"elements": "U-O", "props": "atomic structure"},
    fields={'S':['phase_id', 'entry', 'chemical_formula', 'cell_abc', 'sg_n', 'basis_noneq', 'els_noneq']}
)

lengths = []

for item in answer:
    crystal = MPDSDataRetrieval.compile_crystal(item, 'ase')
    if not crystal: continue
    lengths.extend( calculate_lengths(crystal, 'U', 'O') )

dfrm = (
    pl.DataFrame({"length": sorted(lengths)})
    .with_columns(pl.col("length").count().over("length").alias("occurrence"))
    .unique(subset=["length"])
)

export = MPDSExport.save_plot(dfrm, ['length', 'occurrence'], 'bar')
print(export)
