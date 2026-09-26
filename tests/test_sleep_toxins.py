"""Sleep architecture and toxin load unit tests."""

from __future__ import annotations

import pytest

from moac_qmm.exceptions import ToxinOverloadKill
from moac_qmm.models import ExogenousToxinLoad, SleepArchitectureTensor


class TestSleepArchitectureTensor:
    def test_n3_hours_formula(self) -> None:
        sleep = SleepArchitectureTensor(8.0, 18.0, 22.0, 0.85, 2)
        assert sleep.calc_n3_hours() == pytest.approx(8 * 0.85 * 0.18)

    def test_gh_pulse_scales_with_n3(self) -> None:
        sleep = SleepArchitectureTensor(8.0, 18.0, 22.0, 0.85, 2)
        assert sleep.calc_gh_pulse() == pytest.approx(sleep.calc_n3_hours() * 1.3)

    def test_deficient_n3_collapses_glymphatic(self) -> None:
        sleep = SleepArchitectureTensor(4.0, 3.0, 10.0, 0.8, 6)
        assert sleep.calc_glymphatic_clearance() == 0.2

    def test_sufficient_n3_glymphatic(self) -> None:
        sleep = SleepArchitectureTensor(9.0, 25.0, 22.0, 0.95, 1)
        assert sleep.calc_glymphatic_clearance() > 0.5

    def test_short_sleep_impairs_immune_consolidation(self) -> None:
        sleep = SleepArchitectureTensor(5.0, 20.0, 22.0, 0.9, 1)
        assert sleep.calc_immune_consolidation() == 0.5

    def test_fragmentation_penalty(self) -> None:
        assert SleepArchitectureTensor(8, 18, 22, 0.9, 6).calc_sleep_fragmentation_penalty() == 0.6
        assert SleepArchitectureTensor(8, 18, 22, 0.9, 2).calc_sleep_fragmentation_penalty() == 1.0


class TestExogenousToxinLoad:
    def test_no_toxins_is_neutral(self) -> None:
        toxins = ExogenousToxinLoad({})
        assert toxins.calc_toxin_cyp_derate() == 1.0
        assert toxins.calc_glutathione_depletion() == 1.0

    def test_lead_derates_cyp(self) -> None:
        toxins = ExogenousToxinLoad({"lead": 8.0})
        assert toxins.calc_toxin_cyp_derate() == pytest.approx(0.7)

    def test_double_toxic_load_raises(self) -> None:
        toxins = ExogenousToxinLoad({"lead": 12.0})
        with pytest.raises(ToxinOverloadKill):
            toxins.calc_toxin_cyp_derate()

    def test_alcohol_induces_cyp2e1(self) -> None:
        toxins = ExogenousToxinLoad({"alcohol_chronic": 60.0})
        assert toxins.calc_cyp2e1_induction() == 3.0

    def test_moderate_alcohol_no_induction(self) -> None:
        toxins = ExogenousToxinLoad({"alcohol_chronic": 20.0})
        assert toxins.calc_cyp2e1_induction() == 1.0

    def test_combined_gsh_depletion(self) -> None:
        toxins = ExogenousToxinLoad({"mercury": 6.0, "alcohol_chronic": 60.0})
        assert toxins.calc_glutathione_depletion() == pytest.approx(0.3)
