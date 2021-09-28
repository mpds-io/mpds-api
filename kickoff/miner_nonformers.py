#!/usr/bin/env python
"""
MPDS API usage example:
using the machine-readable phase diagrams
find binary elemental systems producing no compounds,
i.e. non-formers. Typical non-former cases are:

- complete insolubility systems (e.g. La-Mn, elements "too much hate" each other)
- continuous solid solution systems (e.g. Au-Cu, elements "too much love" each other).

NB shapely (libgeos-dev) is required.
"""

import os
import re
import time
import json
from mpds_client import MPDSDataRetrieval


# Within this composition tolerance (%), a phase near a pure element
# will be considered as unary (not a binary) compound
ELEMENT_TOL = 15


def pd_svg_to_points(shape_str):
    """
    Only SVG commands L, M, and Z are used
    in the *svgpath* phase diagrams JSON field
    """
    points = []
    for point in re.split(' L | M ', shape_str.lstrip('M ').rstrip(' Z')):
        points.append([
            float(coord)
            for coord in point.split(',')
        ])
    return points


def almost_equal(x, y, tol=0.1):
    return True if abs(x - y) < tol else False


def get_nonformers(api_client):
    """
    Main procedure:
    phase diagram extraction and massage
    """
    from shapely.geometry import Polygon

    true_nonformers, maybe_nonformers, formers = set(), set(), set()

    for pd in api_client.get_data({"props": "phase diagram", "classes": "binary"}, fields={}):

        # Only full-composition diagrams
        if pd['comp_range'] != [0, 100]:
            continue

        # Only a relatively large temperature range
        if pd['temp'][1] - pd['temp'][0] < 300:
            continue

        fingerprint = tuple(sorted(pd['chemical_elements']))
        #print('|'*50 + pd['entry'])

        for area in pd['shapes']:

            # Discard paths without the semantic meaning
            if area['kind'] == 'drawing':
                continue

            # Discard liquid and gas phases
            if not area.get('is_solid'):
                continue

            if area.get('nphases') == 1:

                points = pd_svg_to_points(area['svgpath'])
                if len(points) == 2:
                    # This is a line compound
                    x0, y0 = points[0]
                    x1, y1 = points[1]
                else:
                    # This is a phase area polygon
                    poly = Polygon(points)
                    x0, y0, x1, y1 = poly.bounds

                # Here we have a continuous solid solution case, e.g. Au-Cu
                if almost_equal(x1 - x0, 100):
                    true_nonformers.add(fingerprint)
                    break

                # Here we discard the elementary phases
                # which may spread over a relatively large range
                elif (almost_equal(x0, 0, ELEMENT_TOL) and almost_equal(x1, 0, ELEMENT_TOL)) \
                    or (almost_equal(x0, 100, ELEMENT_TOL) and almost_equal(x1, 100, ELEMENT_TOL)):
                    continue

                formers.add(fingerprint)
                break

            # Here we have no single phases: complete insolubility case, e.g. La-Mn

        else: maybe_nonformers.add(fingerprint)

    # different pd's may give different impression, so we compare globally
    true_nonformers |= (maybe_nonformers - formers)
    return true_nonformers


if __name__ == "__main__":

    OUTPUT = "mpds_bin_nonformers.json"
    assert not os.path.exists(OUTPUT), "%s exists!" % OUTPUT

    starttime = time.time()

    nonformers = get_nonformers(MPDSDataRetrieval())

    print("Binary nonformers:", len(nonformers))
    f = open(OUTPUT, "w")
    f.write(json.dumps(sorted(list(nonformers)), indent=4))
    f.close()

    print("Done in %1.2f sc" % (time.time() - starttime))
