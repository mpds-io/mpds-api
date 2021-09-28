
def analyze_raw(fh):
    """
    This is to parse the MPDS ab initio calculations done within the
    semiclassical Boltzmann transport equation theory, frozen band approximation,
    as implemented in CRYSTAL17 code
    see https://www.crystal.unito.it/manuals/crystal17.pdf
    and https://wiki.aalto.fi/display/IMM/Transport+properties
    the corresponding carrier concentration is given as N(#carriers)
    it must be positive for valence bands (p-doping) and negative for conduction bands (n-doping),
    in the band gap, the carrier concentration is zero,
    mu is at least from -10 until 20 eV,
    temp is at least 300K and 600K
    """
    sigmas = []
    for line in fh.read().splitlines():

        if line.startswith('#'):
            continue

        mu, temp, carriers, sigma_xx, sigma_xy, sigma_xz, sigma_yy, sigma_yz, sigma_zz = map(float, line.split())
        # we expect the diagonal scalar matrix
        # however the elements can differ due to numerical noise etc.
        sigmas.append([mu, temp, abs(carriers), sigma_xx])

    # further analysis goes here...
    # we just return a value at 600K and 2 eV
    filtered = [deck for deck in sigmas if deck[1] == 600]
    filtered = [deck for deck in filtered if deck[0] == 2.0]

    return filtered[0][-1]