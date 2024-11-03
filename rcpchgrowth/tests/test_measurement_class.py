# standard imports
from datetime import datetime
import json
import os
from pprint import pprint

# third-party imports
import pytest

# rcpch imports
from rcpchgrowth import Measurement
from rcpchgrowth.constants import BMI

# the ACCURACY constant defines the accuracy of the test comparisons
# owing to variations in statistical calculations it's impossible to get exact
# agreement between R and Python, so our statistician feels we can set a tolerance
# within which we will accept a result as correct.

ACCURACY = 1e-3


def load_valid_data_set():
    """
    Loads in the testing data from JSON file
    """
    with open(os.path.abspath(os.path.dirname(__file__)) + "/sds_age_validation_2021.json") as f:
        return json.load(f)


@pytest.mark.parametrize("line", load_valid_data_set())
def test_measurement_class_ukwho_data(line):
    """
    Test which iterates through a JSON file of 4000 fictional children and known calculated (TC via R)
      correct SDS values. Compares the output of the Measurement.measurement method with the known
      correct value.
    """

    measurement_object = Measurement(
        sex=str(line["sex"]),
        birth_date=datetime.strptime(line["birth_date"], "%d/%m/%Y"),
        observation_date=datetime.strptime(
            line["observation_date"], "%d/%m/%Y"),
        measurement_method=str(line["measurement_method"]),
        observation_value=float(line["observation_value"]),
        gestation_weeks=int(line["gestation_weeks"]),
        gestation_days=int(line["gestation_days"]),
        reference="uk-who"
    )

    pprint(vars(measurement_object))
    pprint(line)

    # all comparisons using absolute tolerance (not relative)

    # this conditional guards against failure of pytest.approx with NoneTypes
    if line["corrected_sds"] is None:
        assert measurement_object.measurement[
            "measurement_calculated_values"]['corrected_sds'] is None
    else:
        # Check if the value is a float and has no fractional part
        assert measurement_object.measurement[
            "measurement_calculated_values"]['corrected_sds'] == pytest.approx(
            line["corrected_sds"], abs=ACCURACY)
        if line["corrected_sds"] > 4 and line["corrected_sds"] < 8 and line["measurement_method"] != BMI:
            assert measurement_object.measurement[
                "measurement_calculated_values"]['corrected_centile_band'] == f"This {line['measurement_method']} measurement is well outside the normal range. Please check its accuracy."
        elif line["corrected_sds"] > 8 and line["measurement_method"] != BMI:
            units="cm"
            measurement_method = line["measurement_method"]
            observation_value = line["observation_value"]
            if measurement_method == "ofc":
                measurement_method = "head circumference"
            elif measurement_method == "height":
                measurement_method = "height/length"
            elif measurement_method == "weight":
                units="kg"
            assert measurement_object.measurement["child_observation_value"]["observation_value_error"] == f'The {measurement_method} of {observation_value} {units} is above +8 SD and considered to be an error.'
        elif line["corrected_sds"] > 4 and line["corrected_sds"] <= 15 and line["measurement_method"] == BMI:
            assert measurement_object.measurement[
                "measurement_calculated_values"]['corrected_centile_band'] == f"This {line['measurement_method']} measurement is well outside the normal range. Please check its accuracy."
        elif line["corrected_sds"] < -15 and line["measurement_method"] == BMI:
            observation_value = line["observation_value"]
            assert measurement_object.measurement[
                "child_observation_value"]['observation_value_error'] == f"The Body Mass Index measurement of {observation_value} kg/m² is below -15 SD and considered to be an error."
    # this conditional guards against failure of pytest.approx with NoneTypes
    if line["chronological_sds"] is None:
        assert measurement_object.measurement[
            "measurement_calculated_values"]['chronological_sds'] is None
    else:
        assert measurement_object.measurement[
            "measurement_calculated_values"]['chronological_sds'] == pytest.approx(
            line["chronological_sds"], abs=ACCURACY)
    