import os
import os.path
import sys
import time

import ujson as json
from mpds_client import MPDSDataRetrieval, APIError, MPDSDataTypes

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kickoff'))
from query_utils import normalize_query


class DataExportMPDS:
    """
    Make requests to MPDS database and save data in files
    """

    export_dir = "./export"

    ml_properties_supported = (
        'energy gap',
        'isothermal bulk modulus',
        'enthalpy of formation',
        'heat capacity at constant pressure',
        'Seebeck coefficient',
        'temperature for congruent melting',
        'Debye temperature',
        'linear thermal expansion coefficient',
        'electrical conductivity',
        'thermal conductivity'
    )

    def __init__(self, dtype: int = MPDSDataTypes.ALL, api_key: str = None) -> None:
        """
        dtype : int
            Type of receiving data. Available: PEER_REVIEWED, MACHINE_LEARNING, AB_INITIO, ALL
        api_key : str
            Key from MPDS account
        """
        self.api_key = api_key
        self.client = MPDSDataRetrieval(dtype=dtype, api_key=api_key)
        self.client.chilouttime = 1.0


    def get_structures(self):
        """
        Request atomic structures and save in file
        """
        print("---Started receiving: atomic structure")

        fp = open(os.path.join(DataExportMPDS.export_dir, "atomic_structures.jsonl"), "w")
        for year in range(1890, 2025):
            time.sleep(1.0)
            try:
                for entry in self.client.get_data(normalize_query({"props": "atomic structure", "years": str(year)}),
                fields={}):
                    fp.write(json.dumps(entry, escape_forward_slashes=False) + "\n")
            except APIError as error:
                if error.code == 204: continue # No hits
                else: raise
        fp.close()
        print("---Successfully saved to atomic_structures.jsonl")


    def get_phase_diagrams(self):
        """
        Request phase diagrams and save in file
        """
        print("---Started receiving: phase diagram")

        fp = open(os.path.join(DataExportMPDS.export_dir, "phase_diagrams.jsonl"), "w")
        for year in range(1890, 2025):
            time.sleep(1.0)
            try:
                for entry in self.client.get_data(normalize_query({"props": "phase diagram", "years": str(year)}),
                fields={}):
                    fp.write(json.dumps(entry, escape_forward_slashes=False) + "\n")
            except APIError as error:
                if error.code == 204: continue # No hits
                else: raise
        fp.close()
        print("---Successfully saved to phase_diagrams.jsonl")


    def get_phys_properties(self):
        """
        Request physical properties and save in file
        """
        print("---Started receiving: physical properties PEER_REVIEWED")

        fp = open(os.path.join(DataExportMPDS.export_dir, "physical_properties_peer_reviewed.jsonl"), "w")
        for year in range(1890, 2025):
            time.sleep(1.0)
            try:
                for entry in self.client.get_data(normalize_query({"props": "physical properties", "years": str(year)}),
                fields={}):
                    fp.write(json.dumps(entry, escape_forward_slashes=False) + "\n")
            except APIError as error:
                if error.code == 204: continue # No hits
                else: raise
        fp.close()

        print("---Successfully saved to physical_properties_peer_reviewed.jsonl")
        print("---Started receiving: physical properties MACHINE_LEARNING")

        self.client.dtype = MPDSDataTypes.MACHINE_LEARNING
        fp = open(os.path.join(DataExportMPDS.export_dir, "physical_properties_machine_learning.jsonl"), "w")
        for props in DataExportMPDS.ml_properties_supported:
            for entry in self.client.get_data(normalize_query({"props": props}), fields={}):
                fp.write(json.dumps(entry, escape_forward_slashes=False) + "\n")
        fp.close()

        print("---Successfully saved to physical_properties_machine_learning.jsonl")
        print("---Started receiving: physical properties AB_INITIO")

        self.client.dtype = MPDSDataTypes.AB_INITIO
        fp = open(os.path.join(DataExportMPDS.export_dir, "physical_properties_ab_initio.jsonl"), "w")
        # TODO more data will require splitting
        for entry in self.client.get_data(normalize_query({"props": "physical properties"}), fields={}):
            fp.write(json.dumps(entry, escape_forward_slashes=False) + "\n")
        fp.close()

        print("---Successfully saved to physical_properties_ab_initio.jsonl")

    def get_all_data(self):
        """
        Run getting all data
        """
        self.get_structures()
        self.get_phase_diagrams()
        self.get_phys_properties()


if __name__ == "__main__":
    assert os.path.exists(DataExportMPDS.export_dir) and not os.listdir(DataExportMPDS.export_dir)

    export = DataExportMPDS(api_key="MPDS_KEY")
    export.get_all_data()
