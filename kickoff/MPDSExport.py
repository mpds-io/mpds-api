"""
Utilities on exporting MPDS
API JSON data for plotting
"""
import os
import sys
import random
import ujson as json
import pandas as pd


EXPORT_DIR = "/tmp/_MPDS"
HUMAN_NAMES = {
    'length': 'Bond lengths, &#8491;',
    'occurrence': 'Counts',
    'bandgap': 'Band gap, eV'
}

def verify_export_dir():
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    if not os.access(EXPORT_DIR, os.W_OK):
        raise RuntimeError("%s is not writable!" % EXPORT_DIR)

def gen_basename():
    basename = []
    random.seed()
    for i in range(12):
        basename.append(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"))
    return "".join(basename)

def title(term):
    return HUMAN_NAMES.get(term, term)

def export_plot(data, columns, plottype):
    verify_export_dir()

    plot = {"type": plottype, "payload": {}}

    csv_export = os.path.join(EXPORT_DIR, gen_basename() + ".csv")
    json_export = os.path.join(EXPORT_DIR, gen_basename() + ".json")
    f1, f2 = open(csv_export, "w"), open(json_export, "w")

    if isinstance(data, pd.DataFrame):
        iter_data = data.iterrows
        pointers = columns
    else:
        iter_data = lambda: enumerate(data)
        pointers = range(len(data[0]))

    # CSV:
    f1.write("%s\n" % ",".join(map(str, columns)))
    for _, row in iter_data():
        f1.write("%s\n" % ",".join([str(row[i]) for i in pointers]))
    f1.close()
    print(csv_export)

    # JSON:
    if plottype == 'bar':

        plot["payload"] = {"x": [], "y": [], "xtitle": title(columns[0]), "ytitle": title(columns[1])}

        for _, row in iter_data():
            plot["payload"]["x"].append(row[pointers[0]])
            plot["payload"]["y"].append(row[pointers[1]])

    elif plottype == 'plot3d':

        plot["payload"]["points"] = {"x": [], "y": [], "z": [], "labels": []}
        plot["payload"]["meshes"] = []
        plot["payload"]["xtitle"] = title(columns[0])
        plot["payload"]["ytitle"] = title(columns[1])
        plot["payload"]["ztitle"] = title(columns[2])
        recent_mesh = 0

        for _, row in iter_data():
            plot["payload"]["points"]["x"].append(row[pointers[0]])
            plot["payload"]["points"]["y"].append(row[pointers[1]])
            plot["payload"]["points"]["z"].append(row[pointers[2]])
            plot["payload"]["points"]["labels"].append(row[pointers[3]])

            if row[4] != recent_mesh:
                plot["payload"]["meshes"].append({"x": [], "y": [], "z": []})
            recent_mesh = row[4]

            if plot["payload"]["meshes"]:
                plot["payload"]["meshes"][-1]["x"].append(row[pointers[0]])
                plot["payload"]["meshes"][-1]["y"].append(row[pointers[1]])
                plot["payload"]["meshes"][-1]["z"].append(row[pointers[2]])

    else: raise RuntimeError("\r\nError: %s is an unknown plot type" % plottype)

    f2.write(json.dumps(plot, escape_forward_slashes=False, indent=4))
    f2.close()
    print(json_export)

if __name__ == "__main__":

    a1 = pd.DataFrame([[1.0, 1.0], [2.0, 3.0], [3.0, 9.0], [4.0, 10.0], [5.0, 100.0]], columns=['a11', 'a12']) # NB integers may fail: TypeError: 0 is not JSON serializable
    export_plot(a1, ['a11', 'a12'], 'bar')

    a2 = [[1, 0], [2, 0], [3, 0], [4, 0], [5, 2]]
    export_plot(a2, ['a21', 'a22'], 'bar')

    a3 = pd.DataFrame([[1, 2, 3, '', 0], [1, 2, 2, '', 0], [3, 2, 4, '', 0], [0, 0, 0, '', 0]], columns=['a31', 'a32', 'a33', 'a34', 'a35'])
    export_plot(a3, ['a31', 'a32', 'a33', 'a34', 'a35'], 'plot3d')

    a4 = [[1, 2, 3, '', 0], [1, 2, 2, '', 0], [3, 2, 4, '', 0], [0, 0, 0, '', 0]]
    export_plot(a4, ['a41', 'a42', 'a43', 'a44', 'a45'], 'plot3d')
