#!/usr/bin/env python
"""
MPDS API usage example:
clustering the band gaps of binary compounds

https://developer.mpds.io/#Clustering
"""

from ase.data import chemical_symbols

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
dfrm = dfrm[dfrm['Units'] == 'eV']
dfrm = dfrm[(dfrm['Bandgap'] > 0) & (dfrm['Bandgap'] < 20)]

avgbgfrm = dfrm.groupby('Formula')['Bandgap'].mean().to_frame().reset_index().rename(columns={'Bandgap': 'AvgBandgap'})

dfrm = dfrm.merge(avgbgfrm, how='outer', on='Formula')
dfrm.drop_duplicates('Formula', inplace=True)
dfrm.sort_values('Formula', inplace=True)

fitdata, export_data = [], []

for n, row in dfrm.iterrows():
    groupA, groupB = \
        get_element_group(chemical_symbols.index(row['Elements'][0])), \
        get_element_group(chemical_symbols.index(row['Elements'][1]))
    fitdata.append(Point(sorted([groupA, groupB]) + [round(row['AvgBandgap'], 2)], reference=row['Formula']))

clusters = kmeans(fitdata, k_from_n(len(fitdata)))

for cluster_n, cluster in enumerate(clusters, start=1):
    for pnt in cluster.points:
        export_data.append(pnt.coords + [pnt.reference] + [cluster_n])

export = MPDSExport.save_plot(export_data, ['groupA', 'groupB', 'bandgap', 'compound', 'cluster'], 'plot3d')
print(export)
