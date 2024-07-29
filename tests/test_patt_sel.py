"""
unit tests for the ScPatternSelect class
This will test load and apply patterns to the TPG, only run on dev
"""

import unittest
import ScPatternSelect
from epics import caput


class TestPattSel(unittest.TestCase):
    # TODO: add a setUpClass that instantiates a verified and a test pattern
    @classmethod
    def setUpClass(cls) -> None:
        cls.patt_sel = ScPatternSelect.ScPatternSelect("SYS0", "1", "sioc-sys0-ts01")

        return super().setUpClass()

    def test_get_pattern_row(self):
        # TODO: add better tests for the cases of existing patterns
        self.assertNotEqual(
            self.patt_sel.get_pattern_row("SC_SXR_STD_FR_1_Hz_off_7"), -1
        )

        self.assertEqual(
            self.patt_sel.get_pattern_row("name_that_will_never_exist"), -1
        )

    def test_pattern_exists(self):
        # not sure of a better way to do this.
        # Could just grab the first file from the directory
        self.assertTrue(self.patt_sel.pattern_exists("SC_SXR_STD_FR_1_Hz_off_7"))
        self.assertFalse(self.patt_sel.pattern_exists("name_that_will_never_exist"))

    def test_is_pattern_verified(self):
        self.assertTrue(self.patt_sel.is_pattern_verified("SC_SXR_STD_FR_1_Hz_off_7"))
        self.assertFalse(
            self.patt_sel.is_pattern_verified("name_that_will_never_exist")
        )
        self.assertFalse(self.patt_sel.is_pattern_verified("SC_BSYD_EXP_AC_B_110_Hz"))

    def test_get_relative_patern_path(self):
        self.assertEqual(
            self.patt_sel.get_relative_pattern_path("SC_SXR_STD_FR_1_Hz_off_7"),
            "verified/SC_SXR_STD_FR_1_Hz_off_7",
        )
        self.assertEqual(
            self.patt_sel.get_relative_pattern_path("SC_BSYD_EXP_AC_B_110_Hz"),
            "test/SC_BSYD_EXP_AC_B_110_Hz",
        )
        self.assertIsNone(
            self.patt_sel.get_relative_pattern_path("name_that_will_never_exist")
        )

    def test_load_and_apply_pattern(self):
        """
        test running a pattern by individually calling the load
        and apply functions
        """
        # test loading non-existant pattern
        self.assertIsNone(self.patt_sel.load_pattern("name_that_will_never_exist"), 1)

        # test loading of pattern correctly, independent of pattern programmer
        self.assertEqual(self.patt_sel.load_pattern("SC_SXR_STD_FR_1_Hz_off_7"), 1)
        self.assertEqual(
            caput(
                self.patt_sel.globals.get_pattern_loaded_pv(),
                self.patt_sel.get_relative_pattern_path("SC_SXR_STD_FR_1_Hz_off_7"),
            ),
            1,
        )
        self.assertEqual(self.patt_sel.get_pattern_loaded(), "SC_SXR_STD_FR_1_Hz_off_7")

        # test applying pattern that is not loaded
        self.assertIsNone(self.patt_sel.apply_pattern("SC_BSYD_EXP_AC_B_110_Hz"))
        # test applying non-existant pattern
        self.assertIsNone(self.patt_sel.apply_pattern("name_that_will_never_exist"))

        # test applying pattern correctly, independent of pattern programmer
        self.assertEqual(self.patt_sel.apply_pattern("SC_SXR_STD_FR_1_Hz_off_7"), 1)
        self.assertEqual(
            caput(
                self.patt_sel.globals.get_pattern_running_pv(),
                self.patt_sel.get_relative_pattern_path("SC_SXR_STD_FR_1_Hz_off_7"),
            ),
            1,
        )
        self.assertEqual(
            self.patt_sel.get_pattern_running(), "SC_SXR_STD_FR_1_Hz_off_7"
        )

    def test_run_pattern(self):
        """
        test running a pattern by calling the run pattern function
        """
        # need to do the caput's first when there is no pattern programmer
        # run_pattern checks that the loaded pattern and the pattern you wish to apply are the same
        self.assertEqual(
            caput(
                self.patt_sel.globals.get_pattern_loaded_pv(),
                self.patt_sel.get_relative_pattern_path("SC_SXR_STD_FR_10_Hz_off_7"),
            ),
            1,
        )
        self.assertEqual(
            caput(
                self.patt_sel.globals.get_pattern_running_pv(),
                self.patt_sel.get_relative_pattern_path("SC_SXR_STD_FR_10_Hz_off_7"),
            ),
            1,
        )

        self.assertEqual(
            self.patt_sel.run_pattern("SC_SXR_STD_FR_10_Hz_off_7"),
            1,
        )

        self.assertEqual(
            self.patt_sel.get_pattern_loaded(), "SC_SXR_STD_FR_10_Hz_off_7"
        )
        self.assertEqual(
            self.patt_sel.get_pattern_running(), "SC_SXR_STD_FR_10_Hz_off_7"
        )

    def test_asserts(self):
        """
        test the various asert methods
        """
        with self.assertRaises(TypeError) as context:
            self.patt_sel.assert_dest(1.1)

        with self.assertRaises(AssertionError) as context:
            self.patt_sel.assert_dest(7)
            self.patt_sel.assert_dest(-1)
            self.patt_sel.assert_dest("SXR")

            self.patt_sel.assert_time_source("BC")

        self.assertEqual(self.patt_sel.assert_dest(1), 1)
        self.assertEqual(self.patt_sel.assert_dest("SC_SXR"), 1)
        self.assertEqual(self.patt_sel.assert_time_source("B"), 1)

    def test_rate_list(self):
        """
        tests if the rate list returns properly
        """
        self.assertEqual(
            self.patt_sel.get_available_rates(4, "FR"),
            [0, 1, 10, 51, 102, 204, 510, 663, 1020, 1326, 3316, 8290, 16581],
        )
        self.assertEqual(
            self.patt_sel.get_available_rates(4, "FR", as_string=True),
            [
                "0",
                "1",
                "10",
                "51",
                "102",
                "204",
                "510",
                "663",
                "1020",
                "1326",
                "3316",
                "8290",
                "16581",
            ],
        )
        self.assertEqual(
            self.patt_sel.get_available_rates(4, "FR", is_verified=False),
            [0, 1020, 33163],
        )
        self.assertEqual(
            self.patt_sel.get_available_rates(4, "AC", is_verified=True),
            [0, 1, 5, 10, 30, 60, 120],
        )

    def test_get_pattern_name_by_rate(self):

        self.assertEqual(
            "SC_SXR_STD_FR_10_Hz_off_7",
            self.patt_sel.get_pattern_name_by_rate(sxr_rate=10, sxr_time_src="FR"),
        )
        self.assertEqual(
            "SC_SXR_STD_AC_10_Hz_TS1",
            self.patt_sel.get_pattern_name_by_rate(sxr_rate=10, sxr_time_src="AC"),
        )
        self.assertEqual(
            "SC_DIAG0_STD_FR_10_Hz_off_3",
            self.patt_sel.get_pattern_name_by_rate(diag0_rate=10, diag0_time_src="FR"),
        )
        self.assertEqual(
            "SC_DIAG0_STD_FR_10_Hz_off_3",
            self.patt_sel.get_pattern_name_by_rate(diag0_rate=10, sxr_time_src="FR"),
        )
        (
            "SC_DASEL_STD_FR_10_Hz",
            self.patt_sel.get_pattern_name_by_rate(dest_data={5: [10, "FR"]}),
        )
        self.assertEqual(
            self.patt_sel.get_pattern_name_by_rate(
                dest_data={2: [10, "FR"], 4: [1326, "FR"]}
            ),
            "SC_SXR_EXP_FR_1.3_kHz_off_7",
        )
        self.assertEqual(
            self.patt_sel.get_pattern_name_by_rate(dest_data={4: [1326, "FR"]}),
            "SC_SXR_EXP_FR_1.3_kHz_off_7",
        )

        self.assertEqual(
            self.patt_sel.assert_and_complete_dest_data(
                {
                    4: [1326, "FR"],
                }
            ),
            {
                1: [0, "FR"],
                2: [10, "FR"],
                3: [0, "FR"],
                4: [1326, "FR"],
                5: [0, "FR"],
            },
        )

    def test_assert_dest_data(self):

        with self.assertRaises(AssertionError) as context:
            self.patt_sel.assert_and_complete_dest_data({1: [0, "F"]})
            self.patt_sel.assert_and_complete_dest_data({"1": [0, "FR"]})
            self.patt_sel.assert_rate("1")

        self.assertEqual(
            self.patt_sel.assert_and_complete_dest_data({5: [10, "FR"]}),
            {
                1: [0, "FR"],
                2: [0, "FR"],
                3: [0, "FR"],
                4: [0, "FR"],
                5: [10, "FR"],
            },
        )

        self.assertEqual(
            self.patt_sel.check_bsyd_keepalive(
                {
                    1: [0, "FR"],
                    2: [0, "FR"],
                    3: [0, "FR"],
                    4: [1326, "FR"],
                    5: [0, "FR"],
                }
            ),
            {
                1: [0, "FR"],
                2: [10, "FR"],
                3: [0, "FR"],
                4: [1326, "FR"],
                5: [0, "FR"],
            },
        )


if __name__ == "__main__":
    unittest.main()
