Materials Platform for Data Science: API
==========

The API stands for the *application programming interface*, a way to get the MPDS scientific data automatically in a high-throughput manner for the machine analysis. The possible applications are high-throughput simulations, machine learning and other *data-intensive* techniques in materials science.

![MPDS: Materials Platform for Data Science](https://raw.githubusercontent.com/mpds-io/mpds-api/gh-pages/figures/materials_platform_for_data_science.png "MPDS: Materials Platform for Data Science")

Here you will find:

- issue tracker for the MPDS API
- website [developer.mpds.io](https://developer.mpds.io) with the documentation
- kickoff Python scripts:

    - [The uranium-oxygen chemical bond length distribution](https://github.com/mpds-io/mpds-api/blob/gh-pages/kickoff/miner_bondlength.py)
    - [Clustering the band gaps of binary compounds](https://github.com/mpds-io/mpds-api/blob/gh-pages/kickoff/miner_bgkmeans.py)
    - [The relationship between physical property and crystalline structure](https://github.com/mpds-io/mpds-api/blob/gh-pages/kickoff/miner_propstruct.py)

- MPDS API Jupyter notebooks: [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/mpds-io/mpds-api/gh-pages?filepath=notebooks)

    - [Short intro: basic plotting using the periodic table](https://github.com/mpds-io/mpds-api/blob/gh-pages/notebooks/1_plot_pn_vs_eneg.ipynb)
    - [Basic MPDS API usage: machine-learning and peer-reviewed data](https://github.com/mpds-io/mpds-api/blob/gh-pages/notebooks/2_mpds_basic.ipynb)
    - [Advanced MPDS API usage: unusual materials phases from the machine learning](https://github.com/mpds-io/mpds-api/blob/gh-pages/notebooks/3_mpds_ml_scan.ipynb)
    - [Advanced MPDS API usage: pVT-data and EoS fitting](https://github.com/mpds-io/mpds-api/blob/gh-pages/notebooks/4_eos_fit.ipynb)

All information here is freely available under the [MIT](https://en.wikipedia.org/wiki/MIT_License) and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0) licenses.

Login via [GitHub](https://mpds.io/github_oauth.html) if you'd like to use this API with the open MPDS data:

- `cell parameters vs. temperature and pressure diagrams` (about 6k entries)
- `all compounds containing both Ag and K` (about 250 entries)
- `all binary compounds of oxygen` (about 6k entries)
- `all data generated via machine-learning` (about 900k entries)

Contact us at <mpds-api@tilde.pro> if you'd like to use this API with the all MPDS data.
