#!/usr/bin/env python

from __future__ import division
import sys

import numpy
from numpy.linalg import det
from mpds_client import MPDSDataRetrieval


supported_arities = {1: 'unary', 2: 'binary', 3: 'ternary', 4: 'quaternary', 5: 'quinary'}
mpds_api = MPDSDataRetrieval()

def get_cell_v_for_t(elements, t0=250, t1=350):
    """
    Extracts the cell volumes within the certain temperature

    Args:
        elements: (list) chemical elements to retrieve, the first is metal
        t0, t1: (numeric) temperature boundaries, K

    Returns: dict of volumes per phase
    """
    phases_volumes = {}

    for item in mpds_api.get_data(dict(elements='-'.join(elements), classes=supported_arities[len(elements)]), fields={
    'P': [
        lambda: 'P',
        'sample.material.phase_id',
        lambda: None,
        'sample.measurement[0].condition[0].name',
        'sample.measurement[0].condition[0].units',
        'sample.measurement[0].condition[0].scalar',
        'sample.material.entry'
    ],
    'S':[
        lambda: 'S',
        'phase_id',
        'v',
        lambda: 'Temperature',
        lambda: 'K',
        'condition', # four values
        'entry',
        'occs_noneq',
        'cell_abc',
        'sg_n',
        'basis_noneq',
        'els_noneq'
    ]}):
        if not item or not item[1] or item[3] != 'Temperature' or item[4] != 'K':
            # Other entry type, or no phase assigned, or irrelevant condition given
            continue

        if item[0] == 'P':
            # P-entry, TODO: consider temperature
            if item[5] and (item[5] < t0 or item[5] > t1):
                print('Phase %s, P: OUT OF BOUNDS TEMPERATURE: %s K (%s)' % (item[1], item[5], item[6]))

        else:
            # S-entry
            if item[5] and item[5][0] and (item[5][0] < t0 or item[5][0] > t1):
                print('Phase %s, S: OUT OF BOUNDS TEMPERATURE: %s K (%s)' % (item[1], item[5][0], item[6]))
                continue

            ase_obj = MPDSDataRetrieval.compile_crystal(item, 'ase')
            if not ase_obj:
                continue
            n_metal_atoms = len([p for p in ase_obj if p.symbol == elements[0]])
            phases_volumes.setdefault(item[1], []).append(det(ase_obj.cell) / n_metal_atoms)

    return phases_volumes

if __name__ == "__main__":
    try:
        metal = sys.argv[1]
    except IndexError:
        raise RuntimeError('A chemical element symbol should be given.')
    print("Element: %s" % metal)

    out = get_cell_v_for_t([metal])
    volumes_metal = []
    for phase_id in out:
        v_metal = numpy.median(out[phase_id])
        volumes_metal.append(v_metal)

    out = get_cell_v_for_t([metal, 'O'])
    volumes_oxide = []
    for phase_id in out:
        v_oxide = numpy.median(out[phase_id])
        volumes_oxide.append(v_oxide)

    # Get Pilling-Bedworth ratio
    pbr = numpy.median(volumes_oxide) / numpy.median(volumes_metal)
    print(pbr)