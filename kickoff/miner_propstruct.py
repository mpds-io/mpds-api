#!/usr/bin/env python
"""
MPDS API usage example:
the relationship between a physical property and crystalline structure,
using the Pearson and Kendall's tau coefficients

https://developer.mpds.io/#QSAR-QSPR
"""

from __future__ import division

import numpy as np
import polars as pl
from ase.data import covalent_radii, chemical_symbols
from mpds_client import MPDSDataRetrieval

def get_APF(ase_obj):
    """
    Example crystal structure descriptor:
    https://en.wikipedia.org/wiki/Atomic_packing_factor
    """
    volume = 0.0
    for atom in ase_obj:
        volume += 4 / 3 * np.pi * covalent_radii[chemical_symbols.index(atom.symbol)] ** 3
    return volume / abs(np.linalg.det(ase_obj.cell))

def get_Wiener(ase_obj):
    """
    Example crystal structure descriptor:
    https://en.wikipedia.org/wiki/Wiener_index
    defined per a unit cell
    """
    return np.sum(ase_obj.get_all_distances()) * 0.5

client = MPDSDataRetrieval()

data = client.get_dataframe({"classes": "transitional, oxide", "props": "isothermal bulk modulus"})
data = data.filter(pl.col("Phase").is_not_null())
data = data.filter(pl.col("Units") == "GPa")
data = data.filter(pl.col("Value") > 0)

phases = set(data.select("Phase").to_series())
answer = client.get_data(
    {"props": "atomic structure"},
    phases=phases,
    fields={
        'S': ['phase_id', 'entry', 'chemical_formula', 'cell_abc', 'sg_n', 'basis_noneq', 'els_noneq']
    }
)

descriptors = []

for item in answer:
    crystal = MPDSDataRetrieval.compile_crystal(item, 'ase')
    if not crystal:
        continue
    descriptors.append((item[0], get_APF(crystal), get_Wiener(crystal)))

descriptors = pl.DataFrame(
    descriptors,
    schema=[("Phase", pl.Utf8), ("APF", pl.Float64), ("Wiener", pl.Float64)]
)

d1 = descriptors.group_by("Phase").mean().select(["Phase", "APF"])
d2 = descriptors.group_by("Phase").mean().select(["Phase", "Wiener"])

# ensure all Phase columns are strings
data = data.with_columns(pl.col("Phase").cast(pl.Utf8))
d1 = d1.with_columns(pl.col("Phase").cast(pl.Utf8))
d2 = d2.with_columns(pl.col("Phase").cast(pl.Utf8))

# group and mean calculations
data = data.group_by("Phase").mean().select(["Phase", "Value"])

data = data.join(d1, on="Phase", how="full").select(["Phase", "Value", "APF"])
data = data.join(d2, on="Phase", how="full").select(["Phase", "Value", "APF", "Wiener"])

data = data.rename({"Value": "Prop"})

# compute Pearson correlation
corr_pearson = data.select([
    pl.corr("Prop", "APF", method="pearson").alias("Pearson_Prop_vs_APF"),
    pl.corr("Prop", "Wiener", method="pearson").alias("Pearson_Prop_vs_Wiener")
])

# compute Spearman correlation as a substitute for Kendall
corr_spearman = data.select([
    pl.corr("Prop", "APF", method="spearman").alias("Spearman_Prop_vs_APF"),
    pl.corr("Prop", "Wiener", method="spearman").alias("Spearman_Prop_vs_Wiener")
])

print(f"Pearson. Prop vs. APF = \t{corr_pearson[0, 'Pearson_Prop_vs_APF']}")
print(f"Pearson. Prop vs. Wiener = \t{corr_pearson[0, 'Pearson_Prop_vs_Wiener']}")
print(f"Spearman. Prop vs. APF = \t{corr_spearman[0, 'Spearman_Prop_vs_APF']}")
print(f"Spearman. Prop vs. Wiener = \t{corr_spearman[0, 'Spearman_Prop_vs_Wiener']}")
