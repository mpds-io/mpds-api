#!/usr/bin/env python
"""
This script extracts the liquidus lines for all the reported
phase diagram entries for a given binary system. The extracted
liquidus lines are plotted all together using *matplotlib*.
The following MPDS API JSON fields are considered:
- comp_range
- temp
- shapes: kind
- shapes: nphases
- shapes: is_solid
- shapes: svgpath
"""
import sys
import numpy
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from mpds_client import MPDSDataRetrieval

from miner_nonformers import pd_svg_to_points


MARGIN_EDGES_COMP = 0.1
MARGIN_EDGES_TEMP = 5

if __name__ == "__main__":
    try:
        ela, elb = list(set([sys.argv[1], sys.argv[2]]))
    except IndexError:
        raise RuntimeError('Chemical element symbols should be given.')
    elements = sorted([ela, elb])
    print("Elements: %s" % elements)

    api_client = MPDSDataRetrieval()

    plt.xlabel('Composition')
    plt.ylabel('Temperature')
    plt.annotate(ela, xy=(-0.05, -0.1), xycoords='axes fraction')
    plt.annotate(elb, xy=(1.05, -0.1), xycoords='axes fraction')
    ymin, ymax = 500, 700

    for pd in api_client.get_data({"props": "phase diagram", "classes": "binary", "elements": "-".join(elements)}, fields={}): # fields={} means all fields
        # Consider only full-composition diagrams
        if pd['comp_range'] != [0, 100]:
            continue

        # Consider only a relatively large temperature range
        if pd['temp'][1] - pd['temp'][0] < 300:
            continue

        print("*"*50, pd['entry'], "*"*50)
        done_liquidus = False
        if pd['temp'][0] < ymin: ymin = pd['temp'][0]
        if pd['temp'][1] > ymax: ymax = pd['temp'][1]

        for area in pd['shapes']:
            # Discard the paths without the semantic meaning
            if area['kind'] == 'drawing':
                continue

            # Work with the liquid or gas phases
            if area.get('nphases') == 1 and area.get('is_solid') is False:
                if done_liquidus:
                    print("ANOTHER LIQUID OR GAS PHASE WAS FOUND, THE PD SHAPE IS TOO COMPLEX")
                    continue

                done_liquidus = True
                liquidus_line = []

                for point in pd_svg_to_points(area['svgpath']):

                    # NB the line out of polygon extraction algorithm must be improved;
                    # this is just a quick and dirty example based on
                    # MARGIN_EDGES_TEMP and MARGIN_EDGES_COMP
                    if point[1] < pd['temp'][1] - MARGIN_EDGES_TEMP and \
                       point[0] > pd['comp_range'][0] + MARGIN_EDGES_COMP and \
                       point[0] < pd['comp_range'][1] - MARGIN_EDGES_COMP:
                        liquidus_line.append(point)

                if not liquidus_line:
                    continue

                liquidus_line.sort(key=lambda x: x[0])
                #print(liquidus_line)
                x, y = numpy.transpose(numpy.array(liquidus_line)).tolist()
                plt.plot(x, y, c=numpy.random.rand(3,), lw=1, label=pd['entry'])
                #plt.scatter(x, y, c=numpy.random.rand(3,), s=3, label=pd['entry'])

    plt.axis([0, 100, ymin, ymax])
    plt.legend()
    plt.title('Reported liquidus lines for %s system' % "-".join(elements))
    plt.savefig('liquidus_%s.png' % "-".join(elements), dpi=250)