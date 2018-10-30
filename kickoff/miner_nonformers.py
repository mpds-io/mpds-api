#!/usr/bin/env python
"""
MPDS API usage example:
using the machine-readable phase diagrams
find binary elemental systems producing no compounds,
i.e. non-formers. Typical non-former cases are
complete insolubility systems (elements "hate" each other)
and continuous solid solution systems (elements "love" each other).
"""

import time
from mpds_client import MPDSDataRetrieval

from numpy import linspace
from shapely.geometry import Polygon
from svg.path import parse_path, Path, Line, CubicBezier, QuadraticBezier
from svg.path.path import Move


# Within this tolerance, a phase near a pure element
# will be considered as unary (not a binary compound)
ELEMENT_TOL = 12.5


def deCasteljau(points, u, k=None, i=None, dim=None):
    """
    De Casteljau's algorithm splits Bezier curves polynomials into linear parts;
    https://en.wikipedia.org/wiki/De_Casteljau%27s_algorithm
    """
    if k == None:
        k = len(points)-1
        i = 0
        dim = len(points[0])

    if k == 0:
        return points[i]

    a = deCasteljau(points, u, k=k-1, i=i, dim=dim)
    b = deCasteljau(points, u, k=k-1, i=i+1, dim=dim)
    result = []

    for j in range(dim):
        result.append((1-u) * a[j] + u * b[j])

    return tuple(result)


def linearize_path(path, nsections=4):
    """
    In the MPDS API, phases at the phase diagrams are represented
    as the systems of parametric equations in an SVG format (called "paths").
    Here these paths are converted to the polygon exterior points.
    """
    points = []
    for seg in path:
        if isinstance(seg, Line):
            if seg.start == seg.end:
                continue
            points += [
                [seg.start.real, seg.start.imag],
                [seg.end.real, seg.end.imag]
            ]

        elif isinstance(seg, Move):
            points += [[seg.start.real, seg.start.imag]]

        elif isinstance(seg, QuadraticBezier):
            # quadratic to cubic Bezier control coeffs conversion
            cp1x = seg.start.real + 2/3 * (seg.control.real - seg.start.real)
            cp1y = seg.start.imag + 2/3 * (seg.control.imag - seg.start.imag)
            cp2x = seg.end.real + 2/3 * (seg.control.real - seg.end.real)
            cp2y = seg.end.imag + 2/3 * (seg.control.imag - seg.end.imag)
            controls = [
                [seg.start.real, seg.start.imag],
                [cp1x, cp1y],
                [cp2x, cp2y],
                [seg.end.real, seg.end.imag]
            ]
            for coeff in linspace(0, 1, nsections):
                points += [ deCasteljau(controls, coeff) ]

        elif isinstance(seg, CubicBezier):
            controls = [
                [seg.start.real, seg.start.imag],
                [seg.control1.real, seg.control1.imag],
                [seg.control2.real, seg.control2.imag],
                [seg.end.real, seg.end.imag]
            ]
            for coeff in linspace(0, 1, nsections):
                points += [ deCasteljau(controls, coeff) ]

        else:
            raise RuntimeError('Unexpected SVG primitive!')

    return points


def almost_equal(x, y, tol=0.1):
    return True if abs(x - y) < tol else False


if __name__ == "__main__":

    client = MPDSDataRetrieval()

    starttime = time.time()

    formers, nonformers = set(), set()

    for pd in client.get_data({"props": "phase diagram", "classes": "binary"}, fields={}):

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

            # Discard non-stoichiometric phases
            if area.get('is_ordered') is False:
                continue

            if area.get('nphases') == 1:

                points = linearize_path(parse_path(area['svgpath']))
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

    print("Binary nonformers:", len(nonformers))
    for pair in sorted(list(nonformers)):
        print(pair)
    print("Done in %1.2f sc" % (time.time() - starttime))
