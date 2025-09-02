#!/usr/bin/env python
"""
MPDS API usage example:
clustering the band gaps of binary compounds

https://developer.mpds.io/#Clustering
"""

from ase.data import chemical_symbols
import polars as pl
from mpds_client import MPDSDataRetrieval, MPDSExport

from kmeans import Point, kmeans, k_from_n
from element_groups import get_element_group


client = MPDSDataRetrieval()

dfrm = client.get_dataframe(
    {"classes": "binary", "props": "band gap"},
    fields={'P': [
        'sample.material.chemical_formula',
        'sample.material.chemical_elements',
        'sample.material.condition[0].scalar[0].value',
        'sample.measurement[0].property.units',
        'sample.measurement[0].property.scalar'
    ]},
    columns=['Formula', 'Elements', 'SG', 'Units', 'Bandgap']
)
dfrm = dfrm.filter((dfrm['Units'] == 'eV') & (dfrm['Bandgap'] > 0) & (dfrm['Bandgap'] < 20))

# group by 'Formula' and calculate mean Bandgap
avgbgfrm = dfrm.group_by('Formula').agg(
    pl.col('Bandgap').mean().alias('AvgBandgap')
)

# union with existing DataFrame
dfrm = dfrm.join(avgbgfrm, on='Formula', how='outer')

# delete duplicates and sorted by Formula
dfrm = dfrm.unique(subset=['Formula']).sort('Formula')

fitdata, export_data = [], []

for row in dfrm.iter_rows(named=True):
    groupA = get_element_group(chemical_symbols.index(row['Elements'][0]))
    groupB = get_element_group(chemical_symbols.index(row['Elements'][1]))
    fitdata.append(Point(sorted([groupA, groupB]) + [round(row['AvgBandgap'], 2)], reference=row['Formula']))

# clustering by kmeans
clusters = kmeans(fitdata, k_from_n(len(fitdata)))

for cluster_n, cluster in enumerate(clusters, start=1):
    for pnt in cluster.points:
        export_data.append(pnt.coords + [pnt.reference] + [cluster_n])

columns = ['groupA', 'groupB', 'bandgap', 'compound', 'cluster']
export = MPDSExport.save_plot(pl.DataFrame(export_data, columns), columns, 'plot3d')
print(export)
