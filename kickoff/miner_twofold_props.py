#!/usr/bin/env python
"""
MPDS API usage example:

Display thermal expansion coefficient (alpha^E5)
for all the phases which have T_melt > 1800 C reported

Warning: ML data should be considered with a grain of salt
"""

import numpy as np
from mpds_client import MPDSDataRetrieval, MPDSDataTypes

mpds_api = MPDSDataRetrieval(dtype=MPDSDataTypes.MACHINE_LEARNING) # NB MPDSDataTypes.ALL

phase_for_formula = {}
phase_for_val_a, phase_for_val_b = {}, {}

for deck in mpds_api.get_data({'props': 'temperature for congruent melting', 'classes': 'oxide'}, fields={'P': [
    'sample.material.phase_id',
    'sample.material.chemical_formula',
    'sample.measurement[0].property.scalar'
]}):
    if deck[2] > (1800 + 273):
        phase_for_formula[deck[0]] = deck[1]
        phase_for_val_a.setdefault(deck[0], []).append(deck[2]) # why list? each phase might have > 1 value

for deck in mpds_api.get_data({'props': 'linear thermal expansion coefficient'}, phases=phase_for_val_a.keys(), fields={'P': [
    'sample.material.phase_id',
    # we don't need *chemical_formula* now, since we have phase_id's
    'sample.measurement[0].property.scalar'
]}):
    phase_for_val_b.setdefault(deck[0], []).append(deck[1] * 1E5) # why list? each phase might have > 1 value

# now we just re-group and show the results (but we can do much more!)
results = []
for phase_id, formula in phase_for_formula.items():

    if phase_id not in phase_for_val_b:
        continue
    results.append(
        [formula, np.median(phase_for_val_a[phase_id]) - 273, np.median(phase_for_val_b[phase_id])]
    )

for item in sorted(results, key=lambda x: x[2]):
    print("%s T_melt = %.0f C \t alpha^E5 = %.2f" % tuple(item))