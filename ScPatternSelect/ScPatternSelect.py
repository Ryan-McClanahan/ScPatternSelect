import os
from .tools.globals import globals
from epics import caput, caget

from p4p.client.thread import Context


class ScPatternSelect:
    def __init__(self, system: str, unit: str, ioc: str):
        """"""
        self.system = system
        self.unit = unit
        self.ioc = ioc
        self.globals = globals(self.system, self.unit, self.ioc)
        pva = Context("pva", nt=False)
        self.patt_table = pva.get(self.globals.get_patt_table_name())
        self.init_err_mesages()

    def load_pattern(self, pattern_name: str):
        """
        Loads the given pattern to the tpg
        This preps the given pattern to be started
        next time apply_pattern is called

        Use run_pattern for most usecases

        input
        -------
        pattern_name:
            string of the pattern name

        output
        -------
        Success (int)
            None: if pattern does not exist or unsuccessfull load
            1: if pattern loaded successfully
        """
        # check if pattern exists
        if not self.pattern_exists(pattern_name):
            return None

        rel_patt_path = self.get_relative_pattern_path(pattern_name)

        # this caput errors on non ints for some reason
        path_caput = caput(self.globals.get_path_set_pv(), rel_patt_path)

        load_caput = caput(self.globals.get_load_pv(), 1)

        if path_caput == load_caput == 1:
            return 1
        else:
            return None

    def apply_pattern(self, pattern_name: str):
        """
        Apply the loaded pattern to the tpg
        For safty reasons the given pattern must match the
        actual loaded pattern

        Use run_pattern for most uscases

        input
        -------
        pattern_name:
            string of the pattern name

        output
        -------
            None: on unsuccessful apply
            1: on successful apply

        """

        # check if pattern exists
        if not self.pattern_exists(pattern_name):
            return None

        # return if loaded pattern is not expected
        if pattern_name != self.get_pattern_loaded():
            return None

        # trigger apply process
        # TODO: tripple check the runing pv to see the pattern running?
        return caput(self.globals.get_apply_pv(), 1)

    def run_pattern(self, pattern_name):
        """
        Load and apply the given pattern to the tpg
        This runs the given pattern on the machiene
        Use this for most usecases of running a new pattern

        input
        -------
        pattern_name:
            name of the pattern you wish to run

        output
        -------
        success
            None: if pattern unsuccessfuly ran
            1: if pattern successfully ran
        """

        # load pattern, if load unsuccessfull return None
        if self.load_pattern(pattern_name) == None:
            return None

        # apply pattern, if apply unsuccessfull return None
        if self.apply_pattern(pattern_name) == None:
            return None

        return 1

    def pattern_exists(self, pattern_name: str):
        """
        check if the given pattern exists
        input
        -------
        pattern_name:

        output
        -------
        True
            pattern exists
        Flase
            pattern does not exist
        """
        if self.get_pattern_row(pattern_name) > 0:
            return True

        return False

    def get_pattern_row(self, pattern_name: str):
        """
        returns the row the pattern is in in the NTTable
        input
        -------
        pattern_name:

        output
        -------
        row number:
            int greater than 0
            pattern exists and is in the row number

        -1:
            pattern does not exist
        """
        for row_num, name in enumerate(self.patt_table["value"]["PATTERN_NAME"]):
            if name == pattern_name:
                return row_num

        return -1

    def is_pattern_verified(self, pattern_name: str):
        """
        return weather the given pattern is verified

        input
        -------
        pattern_name:

        output
        -------
        True
            pattern is verified
        Flase
            pattern is not verified or does not exist
        """

        row_num = self.get_pattern_row(pattern_name)

        if row_num == -1:
            return False

        is_verified = self.patt_table["value"]["IS_VERIFIED"][row_num]

        if is_verified == "True":
            return True

        return False

    def get_num_patterns(self):
        """
        Returns total number of rows in the raw_table
        This will always be the same between the raw_table and display_table
        """
        return len(self.patt_table["value"][self.globals.PATTERN_KEYS[0]])

    def get_available_rates(
        self,
        dest,
        time_source_req,
        is_verified=True,
        as_string=False,
    ):
        """
        Returns the avalable FR rates for the destination

        input
        -------
        dest
            destination by int or name, ie SC_SXR or 4
        time_source_req
            timing source requested, AC, FR, B, or ACB
        is_verified
            get rate list from verified or unverified patterns
        as_string
            if the list of rates should be returned as a list of strings

        output
        -------
        rate_list
            list of possible rates to the given destination
            with the given time_source and verification status
        """
        self.assert_dest(dest)
        self.assert_time_source(time_source_req)

        if type(dest) == int:
            dest = self.globals.DEST_NAMES[dest]

        rate_list = [0]
        for row in range(0, self.get_num_patterns()):
            rate = self.patt_table["value"][f"{dest}{self.globals.RATE_SFX}"][row]

            timing_source = self.patt_table["value"][
                f"{dest}{self.globals.TSOURCE_SFX}"
            ][row]

            if self.patt_table["value"]["IS_VERIFIED"][row] == "True":
                patt_verified = True
            else:
                patt_verified = False

            if (
                rate not in rate_list
                and timing_source == time_source_req
                and patt_verified == is_verified
            ):
                rate_list.append(int(rate))

        rate_list.sort()

        if as_string:
            for index, rate in enumerate(rate_list):
                rate = int(rate)
                rate_list[index] = str(rate)

        return rate_list

    def init_err_mesages(self):
        self.dest_name_err = f"dest must be a string in {self.globals.DEST_NAMES}"
        self.dest_num_err = (
            f"dest must be an int in range 0-{len(self.globals.DEST_NAMES)}"
        )
        self.rate_err = f"rate must be an int in range 0-928000"

    def assert_dest(self, dest: globals.DEST_NAMES):
        """
        asserts the destination and converts if needed
        acceptable forms of dest: int, upper.  ex: 2 = SC_BSYD
        """

        if type(dest) != str and type(dest) != int:
            raise TypeError(f"{self.dest_name_err}, or {self.dest_num_err}")

        if type(dest) == str:
            assert dest in self.globals.DEST_NAMES, self.dest_name_err
            return 1

        assert dest in range(0, len(self.globals.DEST_NAMES)), self.dest_num_err
        return 1

    def assert_time_source(self, time_source):
        """
        asserts the time source
        """
        time_source_err = f"time_source must be in {self.globals.TIME_SRCS}"

        assert time_source in self.globals.TIME_SRCS, time_source_err
        return 1

    def assert_rate(self, rate):
        """
        asserts the rate is an int
        """
        assert type(rate) is int, f"rate must be an int, was {rate}, type {type(rate)}"

    def assert_and_complete_dest_data(self, dest_data):
        """
        asserts that given dest_data dictionary is of the form
        {dest_num: int}: [{dest_rate: int}, {dest_time_src: str}]
        adds unincluded dests as rate=0 and time_src = 'None'
        """

        dests = []
        default_dest = [0, "FR"]

        for dest in dest_data:
            if not dest in range(1, len(self.globals.DEST_NAMES)):
                raise AssertionError(
                    f"{self.dest_num_err}, was {dest}, type {type(dest)}"
                )
            self.assert_rate(dest_data[dest][0])
            self.assert_time_source(dest_data[dest][1])
            dests.append(dest)

        for dest_num in range(1, len(self.globals.DEST_NAMES)):
            if dest_num not in dests:
                dest_data[dest_num] = default_dest

        dest_data = dict(sorted(dest_data.items()))

        dest_data = self.check_bsyd_keepalive(dest_data)

        return dest_data

    def get_pattern_name_by_rate(
        self,
        diag0_rate: int = 0,
        diag0_time_src="FR",
        bsyd_rate: int = 0,
        bsyd_time_src="FR",
        hxr_rate: int = 0,
        hxr_time_src="FR",
        sxr_rate: int = 0,
        sxr_time_src="FR",
        dasel_rate: int = 0,
        dasel_time_src="FR",
        is_verified=True,
        dest_data=None,
    ):
        """
        returns the pattern with the given rates and timing sources

        input
        -------
        {dest}_rate:
            rate at destination
        {dest}_time_src:
            timing source of the destination
        is_verified:
            verification status of pattern, True = verified, False = test pattern
        dest_data:
            dictionary with dest numbers as keys and [dest_rate, dest_time_src] as values
            i.e. {1: [0, 'FR'], 2: [0, 'FR'], 3: [0, 'FR'], 4: [10, 'FR'], 5: [0, 'FR']}
            Supports partial dictionaries as well
            i.e. {4: [10, 'FR']}

        output
        -------
        Pattern Name: str
            returns the pattern name if it exists
        None:
            returns None if the patter does not exist
        """
        if dest_data is None:
            dest_data = {}
            dest_data[1] = [diag0_rate, diag0_time_src]
            dest_data[2] = [bsyd_rate, bsyd_time_src]
            dest_data[3] = [hxr_rate, hxr_time_src]
            dest_data[4] = [sxr_rate, sxr_time_src]
            dest_data[5] = [dasel_rate, dasel_time_src]

        dest_data = self.assert_and_complete_dest_data(dest_data)

        if is_verified:
            is_verified = "True"
        else:
            is_verified = "False"

        for pattern_row in range(0, self.get_num_patterns()):
            pattern_match = True
            for dest in dest_data:

                dest_rate = int(
                    self.patt_table["value"][
                        f"{self.globals.DEST_NAMES[dest]}{self.globals.RATE_SFX}"
                    ][pattern_row]
                )
                if dest_rate != dest_data[dest][0]:
                    pattern_match = False
                    break

                dest_time_src = self.patt_table["value"][
                    f"{self.globals.DEST_NAMES[dest]}{self.globals.TSOURCE_SFX}"
                ][pattern_row]

                if dest_time_src == "None":
                    dest_time_src = "FR"

                if dest_time_src != dest_data[dest][1]:
                    pattern_match = False
                    break

            if self.patt_table["value"]["IS_VERIFIED"][pattern_row] != is_verified:
                pattern_match = False

            if pattern_match:
                return self.patt_table["value"]["PATTERN_NAME"][pattern_row]

        return None

    def check_bsyd_keepalive(self, dest_data):
        """
        Checks that dest_data contains 10Hz to bsyd if total rate past bsyd is more than 1020

        input
        -------
        dest_data
            dictionary with dest numbers as keys and [dest_rate, dest_time_src] as values
            i.e. {1: [0, 'FR'], 2: [0, 'FR'], 3: [0, 'FR'], 4: [10, 'FR'], 5: [0, 'FR']}
            This function does not support partial dictionaries

        output
        -------
        dest_data
            returns the same array, however if total rate past bsyd is more than 1020
            the bsyd info is set: dest_data[2] = [10, "FR"]
        """
        rate_past_bsyd = 0
        for dest in range(3, len(self.globals.DEST_NAMES)):
            rate_past_bsyd = dest_data[dest][0] + rate_past_bsyd

        if (rate_past_bsyd > 1020) and (dest_data[2][0] < 10):
            dest_data[2] = [10, "FR"]
        return dest_data

    def get_relative_pattern_path(self, pattern_name: str):
        """
        returns the path to the pattern relative to TpgPatternSettup
        input
        -------
        pattern_name
            Name of the pattern
        verified
            If the pattern is verified for general use

        output
        -------
        if pattern exists:
            path to the pattern relative to TpgPatternSettup
        if pattern does not exist:
            None
        """

        if not self.pattern_exists(pattern_name):
            return None

        if self.is_pattern_verified(pattern_name):
            return os.path.join("verified", pattern_name)
        else:
            return os.path.join("test", pattern_name)

    def get_pattern_data():
        """"""

    def get_pattern_running_data():
        """"""

    def get_pattern_running(self):
        """
        returns the name of the pattern name running on the TPG
        """
        patt_path = caget(self.globals.get_pattern_running_pv(), as_string=True)
        pattern_name = os.path.split(patt_path)
        return pattern_name[-1]

    def get_pattern_loaded(self):
        """
        returns the pattern name loaded to the tpg
        """
        patt_path = caget(self.globals.get_pattern_loaded_pv(), as_string=True)
        patt_path = str(patt_path)
        pattern_name = os.path.split(patt_path)
        return pattern_name[-1]

    def get_pattern_rates():
        """"""

    def stop_beam(self):
        """
        stops the beam using tpg beam classes
        output
        -------
        1
            if caput to tpg_bc_reset_pv is successful
        None
            if caput is unsuccessful
        """
        beam_stop = f"{self.globals.get_beam_stop_pv()}.PROC"
        return caput(beam_stop, 1)

    def tpg_beam_class_reset(self):
        """
        attempts to recover the tpg beam classes

        Add option to add callback once beam is recovered?
        output
        -------
        1
            if caput to tpg_bc_reset_pv is successful
        None
            if caput is unsuccessful
        """
        tpg_bc_reset = f"{self.globals.get_tpg_bc_reset_pv()}.PROC"
        return caput(tpg_bc_reset, 1)
