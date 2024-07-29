"""
globals.py

Contains globals class with references to constants, pvs, and paths used in multiple places
"""

import os

# Available destination names
# (should check against PVs when loading to confirm up-to-date)


class globals:
    def __init__(self, system: str, unit: str, ioc: str):
        self.system = system
        self.unit = unit
        self.ioc = ioc

    """
    returns list of dest names, most have SC_ as a prefix
    """
    DEST_NAMES = ["LASER", "SC_DIAG0", "SC_BSYD", "SC_HXR", "SC_SXR", "SC_DASEL"]

    TYPE_DICT = {"AC": "AC", "fixed_rate": "FR", "burst": "B", "AC_burst": "ACB"}

    TIME_SRCS = ["AC", "FR", "B", "ACB"]

    BSYD_FALLBACK_ENG = 15

    RATE_SFX = "_RATE_Hz"
    TSOURCE_SFX = "_TIMING_SOURCE"
    BUNCHES_PER_TRAIN_SFX = "_BUNCHES_PER_TRAIN"
    BUNCH_SPACING_SFX = "_BUNCH_SPACING"
    OFFSET_SFX = "_OFFSET"
    PATTERN_TYPE = "PATTERN_TYPE"

    PATTERN_TYPES = ["CONTINUOUS", "BURST", "ATYPICAL"]

    """
    Returns a list of available keys (column names) for the NTTable
    """
    PATTERN_KEYS = [
        "PATTERN_NAME",  #'PATTERN_TYPE', #'CUSTOM_NAME',
        "RUN_COUNT",
        "LAST_RUN",
        "IS_VERIFIED",
        "LASER_RATE_Hz",
        "LASER_TIMING_SOURCE",
        "LASER_BUNCHES_PER_TRAIN",
        "LASER_BUNCH_SPACING",
        "SC_DIAG0_RATE_Hz",
        "SC_DIAG0_TIMING_SOURCE",
        "SC_DIAG0_BUNCHES_PER_TRAIN",
        "SC_DIAG0_BUNCH_SPACING",
        "SC_BSYD_RATE_Hz",
        "SC_BSYD_TIMING_SOURCE",
        "SC_BSYD_BUNCHES_PER_TRAIN",
        "SC_BSYD_BUNCH_SPACING",
        "SC_HXR_RATE_Hz",
        "SC_HXR_TIMING_SOURCE",
        "SC_HXR_BUNCHES_PER_TRAIN",
        "SC_HXR_BUNCH_SPACING",
        "SC_SXR_RATE_Hz",
        "SC_SXR_TIMING_SOURCE",
        "SC_SXR_BUNCHES_PER_TRAIN",
        "SC_SXR_BUNCH_SPACING",
        "SC_DASEL_RATE_Hz",
        "SC_DASEL_TIMING_SOURCE",
        "SC_DASEL_BUNCHES_PER_TRAIN",
        "SC_DASEL_BUNCH_SPACING",
        "TAGS",
    ]

    """
    returns a list of the pattern keys for the display
    need to move this to the display
    """
    PATTERN_KEYS_DISPLAYED = [
        #'PATTERN_TYPE',
        "Pattern Name",
        "RAW ROW",  # used for relating back to the raw table
        "LASER_RATE_Hz",
        "LASER_BUNCH_SPACING",  #'LASER_TIMING_SOURCE',
        "SC_DIAG0_RATE_Hz",
        "SC_DIAG0_BUNCH_SPACING",  #'SC_DIAG0_TIMING_SOURCE',
        "SC_BSYD_RATE_Hz",
        "SC_BSYD_BUNCH_SPACING",  #'SC_BSYD_TIMING_SOURCE',
        "SC_HXR_RATE_Hz",
        "SC_HXR_BUNCH_SPACING",  #'SC_HXR_TIMING_SOURCE',
        "SC_SXR_RATE_Hz",
        "SC_SXR_BUNCH_SPACING",  #'SC_SXR_TIMING_SOURCE',
        "SC_DASEL_RATE_Hz",
        "SC_DASEL_BUNCH_SPACING",  #'SC_DASEL_TIMING_SOURCE',
        #'TAGS'
    ]

    """
    Returns a list of the possible modes the accelorator can be in
    I.E. SC10, SC11
    """
    MODES = [
        "SC10",
        "SC11",
        "SC12",
        "SC13",
        "SC14",
        "SC15",
        "SC16",
        "SC17",
        "SC18",
        "SC19",
    ]

    def get_tpg_base_pv(self):
        """
        returs based tpg pv with system and unit generalized
        TPG:{system}:{unit}
        """
        return f"TPG:{self.system.upper()}:{self.unit}"

    def get_patt_table_name(self):
        """
        returns the pattern table name with system and unit generalized
        TPG:{system}:{unit}:PATTERNS
        """
        return f"{self.get_tpg_base_pv()}:PATTERNS"

    def get_mode_table_name(self):
        """
        returns the pattern table name with system and unit generalized
        TPG:{system}:{unit}:MODE_FREQ_MAX
        """
        return f"{self.get_tpg_base_pv()}:MODE_FREQ_MAX"

    def get_tag_table_name(self):
        """
        returns the pattern table name with system and unit generalized
        TPG:{system}:{unit}:MODE_FREQ_MAX
        """
        return f"{self.get_tpg_base_pv()}:TAGS"

    def get_timing_sources(self, contains_any_timing_source=False):
        """
        Returns a list of the possible rate modes for the patterns
        Adds a "-" if contains_any_rate_mode = True
        """
        if contains_any_timing_source:
            return ["-", "Fixed Rate", "AC Rate"]
        else:
            return ["Fixed Rate", "AC Rate"]

    def get_mode_pv(self):
        """
        returns the pattern table name with system and unit generalized
        TPG:{system}:{unit}:MODE
        """
        return f"{self.get_tpg_base_pv()}:MODE"

    def get_path_set_pv(self):
        """
        returns the pattern table name with system and unit generalized
        TPG:{system}:{unit}:PATT_PATH
        """
        # return f"{self.get_tpg_base_pv()}:PATT_PATH_SET"
        return f"{self.get_tpg_base_pv()}:MANUAL_PATH"

    def get_load_pv(self):
        """
        returns the pattern table name with system and unit generalized
        TPG:{system}:{unit}:PATT_LOAD_SET
        """
        # return f"{self.get_tpg_base_pv()}:PATT_LOAD"
        return f"{self.get_tpg_base_pv()}:MANUAL_LOAD"

    def get_apply_pv(self):
        """
        returns the pattern table name with system and unit generalized
        TPG:{system}:{unit}:APPLY
        """
        return f"{self.get_tpg_base_pv()}:APPLY"

    def get_pattern_loaded_pv(self):
        """
        returns the pv with the pattern loaded to the TPG
        """
        return f"{self.get_tpg_base_pv()}:PATT_PATH_LOADED"

    def get_pattern_running_pv(self):
        """
        returns the pv with the readback of the running pattern relitive path
        """
        return f"{self.get_tpg_base_pv()}:PATT_PATH_APPLIED"

    def get_TpgPatternSetup_top(self):
        """
        Returns
        """
        return f'{os.environ["IOC_DATA"]}/{self.ioc}/TpgPatternSetup/'

    def get_pattern_top(self):
        """
        Returns the top pattern directory for the given ioc
        """
        return os.path.join(self.get_TpgPatternSetup_top(), "patterns")

    def get_verified_patt_path(self):
        """
        Returns the verified patterns directory for the given ioc
        """
        return os.path.join(self.get_TpgPatternSetup_top(), "patterns/verified")

    def get_test_patt_path(self):
        """
        Returns the test patterns directory for the given ioc
        """
        return os.path.join(self.get_TpgPatternSetup_top(), "patterns/test")

    def get_meta_data_path(self, pattern_name: str, is_verified: bool) -> str:
        """
        inputs:
        pattern_name
            name of the pattern that you want the meta data for
        is_verified
            weather or not the pattern is verified

        outputs:
            full path to the meta data file
        """
        if is_verified:
            head = self.get_verified_patt_path()
        else:
            head = self.get_test_patt_path()

        tail = f"{pattern_name}/meta.json"

        return os.path.join(head, tail)

    def get_tag_path(self):
        """
        Returns
        """
        return os.path.join(self.get_TpgPatternSetup_top(), "/patterns/tags")

    def get_report_top(self):
        """
        Returns report top directory
        """
        return os.path.join(self.get_TpgPatternSetup_top(), "reports")

    def get_beam_stop_pv(self):
        """"""
        return f"{self.get_tpg_base_pv}:TPG_BEAM_OFF"

    def get_tpg_bc_reset_pv(self):
        """"""
        return f"{self.get_tpg_base_pv}:TPG_BC_RESET"
