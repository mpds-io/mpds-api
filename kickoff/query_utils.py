def normalize_query(query):
    """Ensure 'elements' and 'classes' are joined strings, not lists.

    The MPDS API expects:
      - elements: dash-separated string  e.g. "Sr-Ti-O"
      - classes:  comma-separated string  e.g. "perovskite, conductor"

    Passing raw lists causes unsupported-symbol errors.
    """
    out = dict(query)
    if 'elements' in out and isinstance(out['elements'], (list, tuple)):
        out['elements'] = '-'.join(out['elements'])
    if 'classes' in out and isinstance(out['classes'], (list, tuple)):
        out['classes'] = ','.join(out['classes'])
    return out
