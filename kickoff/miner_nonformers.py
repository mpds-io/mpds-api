#!/usr/bin/env python
"""
MPDS API usage example:
using the machine-readable phase diagrams
find binary elemental systems producing no compounds,
i.e. non-formers. Typical non-former cases are
complete insolubility systems (elements "hate" each other)
and continuous solid solution systems (elements "love" each other).

NB shapely (libgeos-dev) is required.
"""

import re
import time
from mpds_client import MPDSDataRetrieval

from numpy import linspace


# Within this tolerance, a phase near a pure element
# will be considered as unary (not a binary compound)
ELEMENT_TOL = 12.5


def pd_svg_to_points(shape_str):
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
    Main procedure
    for phase diagram extraction and massage
    """
    from shapely.geometry import Polygon

    formers, nonformers = set(), set()

    for pd in api_client.get_data({"props": "phase diagram", "classes": "binary"}, fields={}):

        # Only full-composition diagrams
        if pd['comp_range'] != [0, 100]:
            continue

        # Only a relatively large temperature range
        if pd['temp'][1] - pd['temp'][0] < 300:
            continue

        fingerprint = tuple(sorted(pd['chemical_elements']))

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
                    continue

                # Here we discard the elementary phases
                # which may spread over a relatively large range
                elif (almost_equal(x0, 0, ELEMENT_TOL) and almost_equal(x1, 0, ELEMENT_TOL)) \
                    or (almost_equal(x0, 100, ELEMENT_TOL) and almost_equal(x1, 100, ELEMENT_TOL)):
                    continue

                formers.add(fingerprint)

            # Here we have no single phases: complete insolubility case, e.g. La-Mn

        else: nonformers.add(fingerprint)

    nonformers -= formers
    return nonformers


if __name__ == "__main__":

    starttime = time.time()

    nonformers = get_nonformers(MPDSDataRetrieval())

    print("Binary nonformers:", len(nonformers))
    for pair in sorted(list(nonformers)):
        print(pair)

    print("Done in %1.2f sc" % (time.time() - starttime))
