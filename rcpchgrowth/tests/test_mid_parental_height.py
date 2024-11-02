import pytest

from rcpchgrowth.constants import MALE, FEMALE, UK_WHO, CDC
from rcpchgrowth.mid_parental_height import mid_parental_height, mid_parental_height_z, expected_height_z_from_mid_parental_height_z

maternal_height = 151
paternal_height = 167
ACCURACY = 1e-3


def test_midparental_height():
    assert mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_height, sex=MALE) == 165.5 
    assert mid_parental_height(maternal_height=maternal_height, paternal_height=paternal_height, sex=FEMALE) == 152.5
    assert mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_height, reference=UK_WHO) == pytest.approx(-0.8943229, ACCURACY)
    assert mid_parental_height_z(maternal_height=maternal_height, paternal_height=paternal_height, reference=CDC) == pytest.approx(-0.8177165233046019, ACCURACY)
    assert expected_height_z_from_mid_parental_height_z(mid_parental_height_z=-0.8943229) == pytest.approx(-0.44716145, ACCURACY)