import pytest
from rcpchgrowth.constants import UK_90_PRETERM_AGES,WHO_2006_UNDER_TWOS_AGES,UK_WHO_2006_OVER_TWOS_AGES, UK90_AGES, TWENTY_FIVE_WEEKS_GESTATION

from rcpchgrowth.chart_functions import create_chart
@pytest.mark.parametrize(
        "sex, measurement_method",
        [
            ("male", "height"),
            ("male", "weight"),
            ("male", "bmi"),
            ("male", "ofc"),
            ("female", "height"),
            ("female", "weight"),
            ("female", "bmi"),
            ("female", "ofc"),
        ]
)
def test_create_uk_who_chart_size(sex, measurement_method):
    """
    Tests the size of the charts created
    """
    chart = create_chart(reference="uk-who", measurement_method=measurement_method, sex=sex)

    assert len(chart[0]['uk90_preterm'][sex][measurement_method])==9, f"The 'uk90_preterm' {sex} {measurement_method} chart should have 9 entries, one for each centile."
    assert len(chart[1]['uk_who_infant'][sex][measurement_method])==9, f"The 'uk_who_infant' {sex} {measurement_method} chart should have 9 entries, one for each centile."
    assert len(chart[2]['uk_who_child'][sex][measurement_method])==9, f"The 'uk_who_infant' {sex} {measurement_method} chart should have 9 entries, one for each centile."
    assert len(chart[3]['uk90_child'][sex][measurement_method])==9, f"The 'uk90_child' chart {sex} {measurement_method} should have 9 entries, one for each centile."

    if measurement_method == "bmi":
        assert len(chart[0]['uk90_preterm'][sex][measurement_method][0]['data'])==0, f"The 'uk90_preterm' {sex} {measurement_method} chart 0.4th centile should have 0 entries, one for each decimal age."
        assert len(chart[1]['uk_who_infant'][sex][measurement_method][0]['data'])==len(WHO_2006_UNDER_TWOS_AGES)-1, f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(WHO_2006_UNDER_TWOS_AGES)-1} entries."
        assert len(chart[2]['uk_who_child'][sex][measurement_method][0]['data'])==len(UK_WHO_2006_OVER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(UK_WHO_2006_OVER_TWOS_AGES)} entries."
        assert len(chart[3]['uk90_child'][sex][measurement_method][0]['data'])==len(UK90_AGES), f"The 'uk90_child' {sex} {measurement_method} chart 0.4th centile should have {len(UK90_AGES)} entries."
    elif measurement_method == "height":
        assert len(chart[0]['uk90_preterm'][sex][measurement_method][0]['data'])==len([age for age in UK_90_PRETERM_AGES if age >=TWENTY_FIVE_WEEKS_GESTATION]), f"The 'uk90_preterm' {sex} {measurement_method} chart 0.4th centile should have {len([age for age in UK_90_PRETERM_AGES if age >=TWENTY_FIVE_WEEKS_GESTATION])} entries, one for each decimal age from 25 weeks."
        assert len(chart[1]['uk_who_infant'][sex][measurement_method][0]['data'])==len(WHO_2006_UNDER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(WHO_2006_UNDER_TWOS_AGES)} entries."
        assert len(chart[2]['uk_who_child'][sex][measurement_method][0]['data'])==len(UK_WHO_2006_OVER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(UK_WHO_2006_OVER_TWOS_AGES)} entries."
        assert len(chart[3]['uk90_child'][sex][measurement_method][0]['data'])==len(UK90_AGES), f"The 'uk90_child' {sex} {measurement_method} chart 0.4th centile should have {len(UK90_AGES)} entries."
    elif measurement_method == "weight":
        assert len(chart[0]['uk90_preterm'][sex][measurement_method][0]['data'])==len(UK_90_PRETERM_AGES)-1, f"The 'uk90_preterm' {sex} {measurement_method} chart 0.4th centile should have {len(UK_90_PRETERM_AGES)-1} entries, one for each decimal age from 25 weeks."
        assert len(chart[1]['uk_who_infant'][sex][measurement_method][0]['data'])==len(WHO_2006_UNDER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(WHO_2006_UNDER_TWOS_AGES)} entries."
        assert len(chart[2]['uk_who_child'][sex][measurement_method][0]['data'])==len(UK_WHO_2006_OVER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(UK_WHO_2006_OVER_TWOS_AGES)} entries."
        assert len(chart[3]['uk90_child'][sex][measurement_method][0]['data'])==len(UK90_AGES), f"The 'uk90_child' {sex} {measurement_method} chart 0.4th centile should have {len(UK90_AGES)} entries."
    elif measurement_method == "ofc":
        assert len(chart[0]['uk90_preterm'][sex][measurement_method][0]['data'])==len(UK_90_PRETERM_AGES)-1, f"The 'uk90_preterm' {sex} {measurement_method} chart 0.4th centile should have {len(UK_90_PRETERM_AGES)-1} entries, one for each decimal age from 25 weeks."
        assert len(chart[1]['uk_who_infant'][sex][measurement_method][0]['data'])==len(WHO_2006_UNDER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(WHO_2006_UNDER_TWOS_AGES)} entries."
        assert len(chart[2]['uk_who_child'][sex][measurement_method][0]['data'])==len(UK_WHO_2006_OVER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(UK_WHO_2006_OVER_TWOS_AGES)} entries."
        if sex == 'female':
            assert len(chart[3]['uk90_child'][sex][measurement_method][0]['data'])==len([age for age in UK90_AGES if age <=17]), f"The 'uk90_child' {sex} {measurement_method} chart 0.4th centile should have {len([age for age in UK90_AGES if age <=17])} entries."
        if sex == 'male':
            assert len(chart[3]['uk90_child'][sex][measurement_method][0]['data'])==len([age for age in UK90_AGES if age <=18]), f"The 'uk90_child' {sex} {measurement_method} chart 0.4th centile should have {len([age for age in UK90_AGES if age <=18])} entries."

    else:
        assert len(chart[0]['uk90_preterm'][sex][measurement_method][0]['data'])==len(UK_90_PRETERM_AGES), f"The 'uk90_preterm' {sex} {measurement_method} chart 0.4th centile should have {len(UK_90_PRETERM_AGES)} entries, one for each centile."
        assert len(chart[1]['uk_who_infant'][sex][measurement_method][0]['data'])==len(WHO_2006_UNDER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(WHO_2006_UNDER_TWOS_AGES)} entries."
        assert len(chart[2]['uk_who_child'][sex][measurement_method][0]['data'])==len(UK_WHO_2006_OVER_TWOS_AGES), f"The 'uk_who_infant' {sex} {measurement_method} chart 0.4th centile should have {len(UK_WHO_2006_OVER_TWOS_AGES)} entries."
        assert len(chart[3]['uk90_child'][sex][measurement_method][0]['data'])==len(UK90_AGES), f"The 'uk90_child' {sex} {measurement_method} chart 0.4th centile should have {len(UK90_AGES)} entries."