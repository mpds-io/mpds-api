#!/usr/bin/env python3
"""
Extract and cache the MPDS data of different types (i.e. harvesting approaches):
peer_reviewed experimental vs. in-house ab initio modeling
for the further comparison
"""
import os.path
import pickle
import math

from mpds_client import MPDSDataRetrieval, MPDSDataTypes


result_cache = 'mpds_cmp_ab_pr.pkl'

MILLIEV_TO_INVCM = 8.06554
INVMM_TO_INVCM = 10

MPDSDataRetrieval.chilouttime = 0.5


def sg_to_label(num):
    if   195 <= num <= 230: return 'cub'
    elif 168 <= num <= 194: return 'hex'
    elif 143 <= num <= 167: return 'trig'
    elif 75  <= num <= 142: return 'tet'
    elif 16  <= num <= 74:  return 'orth'
    elif 3   <= num <= 15:  return 'monocl'
    elif 1   <= num <= 2:   return 'tricl'
    else: raise RuntimeError(f'Space group number {num} is invalid')


def short_formula(given_string, round_brackets_strip=True):
    given_string = given_string.split()[0].strip().replace("x", "")

    if given_string.startswith("[") and len(given_string.split("[")) == 2 and given_string.endswith("]"):
        given_string = given_string.strip("[]")

    if round_brackets_strip:
        given_string = given_string.strip("()")

    given_string = given_string.replace("(", "[").replace(")", "]")
    return given_string


def is_scalar(value):
    try: float(value)
    except (TypeError, ValueError): return False
    return True


def pr_prop_massage_1(deck):
    if deck[4] != 'kJ g-at.-1':
        return None
    return deck


def ab_prop_massage_2(deck):
    deck[3] = list(set(filter(None, deck[3]['modes_freqs']['0 0 0'])))
    return deck


def pr_prop_massage_2(deck):
    if deck[4] == 'eV':
        deck[3] *= (1000 * MILLIEV_TO_INVCM)
    elif deck[4] != 'mm-1':
        deck[3] *= INVMM_TO_INVCM
    return deck


def pr_prop_massage_3(deck):
    if deck[4] != 'J K-1 g-at.-1':
        return None
    return deck


def pr_prop_massage_4(deck):
    if deck[4] != 'GPa':
        return None
    return deck


def pr_prop_massage_5(deck):
    if deck[4] != '':
        return None
    return deck


def ab_prop_massage_6(deck):
    deck[3] = (deck[5], deck[3])
    return deck


def pr_prop_massage_6(deck):
    if deck[4] != '':
        return None
    deck[3] = (deck[5], deck[3])
    return deck


phases_known_bg_type = set()

def bg_filter_1(deck):
    if deck[4] != 'eV':
        return None
    return deck


def bg_filter_2(deck):
    if deck[4] != 'eV':
        return None
    phases_known_bg_type.add(deck[2])
    return deck


def bg_filter_3(deck):
    if deck[2] in phases_known_bg_type:
        return None
    if deck[4] != 'eV':
        return None
    return deck


work_outline = {
    'electrical conductivity': {
        'meta': {
            'interval': [math.exp(-28), math.exp(28)]
        }
    },
    'Seebeck coefficient': {
        'meta': {
            'interval': [-1000, 1000]
        }
    },
    'enthalpy of formation': {
        'meta': {
            'pr_prop_massage': pr_prop_massage_1,
            'interval': [-900, 200]
        }
    },
    'vibrational spectra': {
        'meta': {
            'pr_prop_name': 'phonons',
            'ab_prop_conds': [
                'sample.material.chemical_formula',
                'sample.material.condition[0].scalar[0].value',
                'sample.material.phase_id',
                'sample.measurement[0].property.matrix'
            ],
            'ab_prop_massage': ab_prop_massage_2,
            'pr_prop_massage': pr_prop_massage_2,
            'interval': [0, 2000]
        }
    },
    'heat capacity at constant pressure': {
        'meta': {
            'pr_prop_massage': pr_prop_massage_3,
            'interval': [0, 500]
        }
    },
    'isothermal bulk modulus': {
        'meta': {
            'pr_prop_massage': pr_prop_massage_4,
            'interval': [0.5, 2000]
        }
    },
    'poisson ratio': {
        'meta': {
            'pr_prop_massage': pr_prop_massage_5,
            'interval': [0, 1]
        }
    },
    'effective charge': {
        'meta': {
            'ab_prop_conds': [
                'sample.material.chemical_formula',
                'sample.material.condition[0].scalar[0].value',
                'sample.material.phase_id',
                'sample.measurement[0].property.scalar',
                'sample.measurement[0].property.units',
                'sample.measurement[0].condition[1].refers_to'
            ],
            'pr_prop_conds': [
                'sample.material.chemical_formula',
                'sample.material.condition[0].scalar[0].value',
                'sample.material.phase_id',
                'sample.measurement[0].property.scalar',
                'sample.measurement[0].property.units',
                'sample.measurement[0].condition[1].refers_to'
            ],
            'ab_prop_massage': ab_prop_massage_6,
            'pr_prop_massage': pr_prop_massage_6,
            'interval': [-20, 20]
        }
    },
    'energy gap for direct transition': {
        'meta': {
            'ab_prop_conds': ['sample.material.chemical_formula', 'sample.material.condition[0].scalar[0].value',
            'sample.material.phase_id', 'sample.measurement[0].property.scalar', 'sample.measurement[0].property.units'],
            'pr_prop_conds': ['sample.material.chemical_formula', 'sample.material.condition[0].scalar[0].value',
            'sample.material.phase_id', 'sample.measurement[0].property.scalar', 'sample.measurement[0].property.units'],
            'ab_prop_massage': bg_filter_1,
            'pr_prop_massage': bg_filter_2,
            'interval': [0.01, 20]
        }
    },
    'energy gap for indirect transition': {
        'meta': {
            'ab_prop_conds': ['sample.material.chemical_formula', 'sample.material.condition[0].scalar[0].value',
            'sample.material.phase_id', 'sample.measurement[0].property.scalar', 'sample.measurement[0].property.units'],
            'pr_prop_conds': ['sample.material.chemical_formula', 'sample.material.condition[0].scalar[0].value',
            'sample.material.phase_id', 'sample.measurement[0].property.scalar', 'sample.measurement[0].property.units'],
            'ab_prop_massage': bg_filter_1,
            'pr_prop_massage': bg_filter_2,
            'interval': [0.01, 20]
        }
    },
    'energy gap': {
        'meta': {
            'ab_prop_conds': ['sample.material.chemical_formula', 'sample.material.condition[0].scalar[0].value',
            'sample.material.phase_id', 'sample.measurement[0].property.scalar', 'sample.measurement[0].property.units'],
            'pr_prop_conds': ['sample.material.chemical_formula', 'sample.material.condition[0].scalar[0].value',
            'sample.material.phase_id', 'sample.measurement[0].property.scalar', 'sample.measurement[0].property.units'],
            'ab_prop_massage': bg_filter_3,
            'pr_prop_massage': bg_filter_3,
            'interval': [0.01, 20]
        }
    },
    # 'magnetic moment': {}  # TODO after new data 2022 release
    # 'infrared spectra': {} # TODO after new data 2022 release
    # 'Raman spectra': {}    # TODO after new data 2022 release
}

phase_formulae = {}

def get_ab_pr_values(
    ab_prop_name,
    pr_prop_name=None,
    interval=[0, 1],
    ab_prop_conds=None,
    pr_prop_conds=None,
    ab_prop_massage=None,
    pr_prop_massage=None
):
    if not pr_prop_name:
        pr_prop_name = ab_prop_name

    ab_data, pr_data = {}, {}

    print('#' * 50, 'downloading', ab_prop_name)

    mpds_api = MPDSDataRetrieval(dtype=MPDSDataTypes.AB_INITIO)
    for deck in mpds_api.get_data({'props': ab_prop_name}, fields={'P': ab_prop_conds or [
        'sample.material.chemical_formula',
        'sample.material.condition[0].scalar[0].value',
        'sample.material.phase_id',
        'sample.measurement[0].property.scalar'
    ]}):
        if ab_prop_massage:
            deck = ab_prop_massage(deck)
            if not deck:
                continue

        if is_scalar(deck[3]) and not interval[0] < deck[3] < interval[1]:
            print('Skipping value: %s' % str(deck))
            continue

        ab_data.setdefault(deck[2], []).append(deck[3])
        phase_formulae[deck[2]] = (short_formula(deck[0]), sg_to_label(deck[1]))

    print('#' * 50, 'downloading', pr_prop_name)

    mpds_api = MPDSDataRetrieval(dtype=MPDSDataTypes.PEER_REVIEWED)
    for deck in mpds_api.get_data({'props': pr_prop_name}, fields={'P': pr_prop_conds or [
        'sample.material.chemical_formula',
        'sample.material.condition[0].scalar[0].value',
        'sample.material.phase_id',
        'sample.measurement[0].property.scalar',
        'sample.measurement[0].property.units',
        'sample.measurement[0].condition[0].units',
        'sample.measurement[0].condition[0].name',
        'sample.measurement[0].condition[0].scalar'
    ]}):
        if pr_prop_massage:
            deck = pr_prop_massage(deck)
            if not deck:
                continue

        if is_scalar(deck[3]) and not interval[0] < float(deck[3]) < interval[1]:
            print('Skipping value: %s' % str(deck))
            continue

        pr_data.setdefault(deck[2], []).append(deck[3])
        phase_formulae[deck[2]] = (short_formula(deck[0]), sg_to_label(deck[1]))

    for phase_id in ab_data:
        if phase_id not in pr_data:
            continue

        #print("%s: %s vs. %s" % (phase_formulae[phase_id], ab_data[phase_id], pr_data[phase_id]))
        work_outline[ab_prop_name].setdefault('data', []).append(
            (phase_formulae[phase_id], ab_data[phase_id], pr_data[phase_id])
        )


if __name__ == "__main__":

    if not os.path.exists(result_cache):

        for key, value in work_outline.items():
            get_ab_pr_values(
                key,
                pr_prop_name=value['meta'].get('pr_prop_name'),
                interval=value['meta'].get('interval'),
                ab_prop_conds=value['meta'].get('ab_prop_conds'),
                pr_prop_conds=value['meta'].get('pr_prop_conds'),
                ab_prop_massage=value['meta'].get('ab_prop_massage'),
                pr_prop_massage=value['meta'].get('pr_prop_massage')
            )
            del work_outline[key]['meta'] # for pickling

        # saving as a cache for future re-use
        with open(result_cache, 'wb') as pickle_file:
            pickle.dump(work_outline, pickle_file, protocol=2)

    with open(result_cache, 'rb') as pickle_file:
        work_outline = pickle.load(pickle_file)

    for key, value in work_outline.items():

        print('#' * 50, 'comparing', key)
        for item in value['data']:
            print(item)
