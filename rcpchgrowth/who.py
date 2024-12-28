"""
Handles WHO reference data selection
"""

# standard imports
import json
from importlib import resources
from pathlib import Path

# rcpch imports
from .constants import *

"""
birth_date: date of birth
observation_date: date of observation
sex: sex (string, MALE or FEMALE)
decimal_age: chronological, decimal
corrected_age: corrected for prematurity, decimal
measurement_method: height, weight, bmi, ofc (decimal)
observation: value (float)
gestation_weeks: gestational age(weeks), integer
gestation_days: supplementary days of gestation
lms: L, M or S
reference: reference data
"""

# load the reference data
data_directory = resources.files("rcpchgrowth.data_tables")

data_path = Path(
    data_directory, "who_infants.json")  # 2 weeks to 2 years
with open(data_path) as json_file:
    WHO_INFANTS_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    data_directory, "who_children.json")  # 2 years to 5 years
with open(data_path) as json_file:
    WHO_CHILD_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    data_directory, "who_2007_children.json")  # 5 years to 19 years
with open(data_path) as json_file:
    WHO_2007_DATA = json.load(json_file)
    json_file.close()

# public functions


def reference_data_absent(
    age: float,
    measurement_method: str,
    sex: str
):
    """
    Helper function.
    Returns boolean
    Tests presence of valid reference data for a given measurement request

    Reference data is not complete for all ages/sexes/measurements.
     - Length data is not available until 25 weeks gestation, though weight date is available from 23 weeks
     - There is only BMI reference data from 2 weeks of age to aged 20y
     - Head circumference reference data is available from 23 weeks gestation to 17y in girls and 18y in boys
     - lowest threshold is 23 weeks, upper threshold is 20y
    """

    if age < ZERO_YEARS:  # lower threshold of WHO data
        return True, "WHO data does not exist below term."

    if age > NINETEEN_YEARS:  # upper threshold of UK90 data
        return True, "WHO data does not exist above 19 years."

    if measurement_method == WEIGHT and age > TEN_YEARS:
        return True, "WHO weight data does not exist in children over 10 y of age."
    
    if measurement_method == HEAD_CIRCUMFERENCE and age > FIVE_YEARS:
        return True, "WHO head circumference data does not exist in children over 5 y of age."

    else:
        return False, ""


def who_reference(
    age: float,
    default_youngest_reference: bool = False
) -> json:
    """
    The purpose of this function is to choose the correct reference for calculation.
    The UK-WHO standard is an unusual case because it combines two different reference sources.
    - UK90 reference runs from 23 weeks to 20 y
    - WHO 2006 runs from 2 weeks to 4 years
    - UK90 then resumes from 4 years to 20 years
    The function return the appropriate reference file as json
    """

    # # These conditionals are to select the correct reference
    # if age < WHO_2006_REFERENCE_LOWER_THRESHOLD:
    #     # Below the range for which we have reference data, we can't provide a calculation.
    #     raise LookupError("There is no WHO reference data below 42 weeks gestation")


    if age <= WHO_2006_REFERENCE_UPPER_THRESHOLD:
        # Children up to and including 5 years are measured using WHO 2006 data
        if (age == 2.0 and default_youngest_reference) or age < WHO_CHILD_LOWER_THRESHOLD:
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 lying and standing in centile curve generation
            # WHO 2006 reference is used for children below 2 years or those who are 2 years old and default_youngest_reference is True
            return WHO_INFANTS_DATA
        return WHO_CHILD_DATA
        
    elif age <= WHO_2007_REFERENCE_UPPER_THRESHOLD:
        # All children over 5 years and above are measured using WHO 2007 child data
        return WHO_2007_DATA

    else:
        raise LookupError("There are no WHO reference data above the age of 19 years.")


def who_lms_array_for_measurement_and_sex(
    age: float,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False
) -> list:

    # selects the correct lms data array from the patchwork of references that make up UK-WHO

    try:
        selected_reference = who_reference(
            age=age,
            default_youngest_reference=default_youngest_reference
        )
    except:  #  there is no reference for the age supplied
        raise LookupError("There is no WHO reference for the age supplied.")

    # Check that the measurement requested has reference data at that age

    invalid_data, data_error = reference_data_absent(
        age=age,
        measurement_method=measurement_method,
        sex=sex)

    if invalid_data:
        raise LookupError(data_error)
    else:
        return selected_reference["measurement"][measurement_method][sex]


def select_reference_data_for_who_chart(
    who_reference_name: str, 
    measurement_method: str, 
    sex: str,
    default_youngest_reference: bool = False):

    # takes a who_reference name (see parameter constants), measurement_method and sex to return
    # reference data

    if who_reference_name == WHO_2006_INFANT:
        try:
            who_infants_reference = who_lms_array_for_measurement_and_sex(
                age=0.04,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference 
            )
        except:
            who_infants_reference = []
        return who_infants_reference
    elif who_reference_name == WHO_2006_CHILD:
        try:
            who_2006_children_reference = who_lms_array_for_measurement_and_sex(
                age=1.0,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference # should never need younger reference in this calculation
            )
        except:
            who_2006_children_reference = []
        return who_2006_children_reference
    elif who_reference_name == WHO_2007_CHILD:
        try:
            who_2007_children_reference = who_lms_array_for_measurement_and_sex(
                age=6.0,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference
            )
        except:
            who_2007_children_reference = []
        return who_2007_children_reference
    else:
        raise LookupError(
            f"No data found for {measurement_method} in {sex}s in {who_reference_name}")
