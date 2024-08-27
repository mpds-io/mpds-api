import os.path

import pandas as pd
from mpds_client import MPDSDataRetrieval


class DataExportMPDS:
    """
    Make requests to MPDS database, save data in json format
    """

    export_dir = "./export"


    def __init__(self, dtype: int = 7, api_key: str = None) -> None:
        """
        dtype : int
            Type of receiving data. Available: PEER_REVIEWED = 1,
            MACHINE_LEARNING = 2, AB_INITIO = 4, ALL = 7
        api_key : str
            Key from MPDS-account
        """
        self.api_key = api_key
        self.client = MPDSDataRetrieval(dtype=dtype, api_key=api_key)
        self.client.chilouttime = 1


    def get_structures(self):
        """
        Request atomic structure. Save in file
        """
        print("---Started receiving: atomic structure---")

        store = None
        for year in range(1890, 2024):
            if not os.path.isfile("atomic_structures.json"):
                try:
                    dfrm = pd.DataFrame(
                        self.client.get_data(
                            {"props": "atomic structure", "years": str(year)},
                            fields={},
                        )
                    )
                    if not isinstance(store, pd.DataFrame):
                        store = dfrm
                    else:
                        store = pd.concat([store, dfrm], ignore_index=True)
                except Exception as error:
                    print("An exception occurred:", error)

        store.to_json(os.path.join(DataExportMPDS.export_dir, "atomic_structures.json"))
        print("Successfully saved to atomic_structures.json")


    def get_phase_diagrams(self):
        """
        Request phase diagrams. Save in file
        """
        print("---Started receiving: phase diagram---")

        store = None
        for year in range(1890, 2024):
            if not os.path.isfile("phase_diagrams.json"):
                try:
                    dfrm = pd.DataFrame(
                        self.client.get_data(
                            {"props": "phase diagram", "years": str(year)}, fields={}
                        )
                    )
                    if not isinstance(store, pd.DataFrame):
                        store = dfrm
                    else:
                        store = pd.concat([store, dfrm], ignore_index=True)
                except Exception as error:
                    print("An exception occurred:", error)

        store.to_json(os.path.join(DataExportMPDS.export_dir, "phase_diagrams.json"))
        print("Successfully saved to phase_diagrams.json")


    def get_phys_properties(self):
        """
        Request physical properties. Save in file
        """
        print("---Started receiving: physical properties---")

        store = None
        for year in range(1890, 2024):
            if not os.path.isfile("physical_properties.json"):
                try:
                    dfrm = pd.DataFrame(
                        self.client.get_data(
                            {"props": "physical properties", "years": str(year)},
                            fields={},
                        )
                    )
                    if not isinstance(store, pd.DataFrame):
                        store = dfrm
                    else:
                        store = pd.concat([store, dfrm], ignore_index=True)
                except Exception as error:
                    print("An exception occurred:", error)

        store.to_json(os.path.join(DataExportMPDS.export_dir, "physical_properties.json"))
        print("Successfully saved to physical_properties.json")


    def get_all_data(self):
        """
        Run getting all data
        """
        self.get_phys_properties()
        self.get_structures()
        self.get_phase_diagrams()


if __name__ == "__main__":
    assert os.path.exists(DataExportMPDS.export_dir) and not os.listdir(DataExportMPDS.export_dir)

    client = DataExportMPDS(api_key="MPDS_KEY")
    client.get_all_data()
