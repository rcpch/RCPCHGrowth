"""
Handles CDC-specific reference data selection
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

# data_path = Path(data_directory,"fenton", "fenton.json")  # 23 weeks to 50 weeks - currently not in the code base
# with open(data_path) as json_file:
#     FENTON_DATA = json.load(json_file)
#     json_file.close()
FENTON_DATA = []

data_path = Path(data_directory, "cdc_infants.json")  # CDC interpretation of WHO 0-2y
with open(data_path) as json_file:
    CDC_INFANT_DATA = json.load(json_file)
    json_file.close()

data_path = Path(data_directory, "cdc2-20.json")  # 2 years to 20 years
with open(data_path) as json_file:
    CDC_CHILD_DATA = json.load(json_file)
    json_file.close()
# public functions


def reference_data_absent(age: float, measurement_method: str, sex: str):
    """
    Helper function.
    Returns boolean
    Tests presence of valid reference data for a given measurement request

    Reference data is not complete for all ages/sexes/measurements.
    - WHO data is used from 0-2 years
    - CDC data is used from 2-20 years
    """

    if age < 0:
        return True, "CDC data does not exist below 40 weeks."
    if age > TWENTY_YEARS:  # upper threshold of UK90 data
        return True, "CDC data does not exist above 20 years."
    if measurement_method == HEAD_CIRCUMFERENCE and age > THREE_YEARS:
        return True, "CDC data does not exist for head circumference above 3 years."
    if measurement_method == BMI and age < TWO_YEARS:
        return True, "CDC data does not exist for BMI below 2 years."
    else:
        return False, None


def cdc_reference(age: float, measurement_method, default_youngest_reference: bool = False) -> json:
    """
    The purpose of this function is to choose the correct reference for calculation.
    The CDC standard is an unusual case because it combines two different reference sources: the 1977 National Center for Health Statistics (NCHS) and the WHO2006.
    - CDC reference runs from 2.04 y to 20 y
    - WHO 2006 runs from 0  to 2 years
    - Preterm data is handled by Fenton (which is Canadian data)
    The function return the appropriate reference file as json
    """

    # These conditionals are to select the correct reference
    if age < FENTON_LOWER_THRESHOLD:
        # Below the range for which we have reference data, we can't provide a calculation.
        raise ValueError(
            "There is no reference data for ages below 22 weeks gestation."
        )
    elif age < 0:
        # Below 40 weeks, Fenton data is always used
        return FENTON_DATA
    
    elif age < 2 or (age == 2 and default_youngest_reference) or (measurement_method == HEAD_CIRCUMFERENCE and age <= 3):
        # Below 2 years, CDC interpretation of WHO is used
        return CDC_INFANT_DATA

    elif age <= CDC_UPPER_THRESHOLD:
        # CDC data is used for all children 2-20 years
        return CDC_CHILD_DATA 

    else:
        return ValueError("There is no CDC reference data above the age of 20 years.")


def cdc_lms_array_for_measurement_and_sex(
    age: float,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False,
) -> list:

    # selects the correct lms data array from the patchwork of references that make up UK-WHO

    # Check that the measurement requested has reference data at that age

    invalid_data, data_error = reference_data_absent(
     
        age=age, measurement_method=measurement_method, sex=sex
    )
    try:
        selected_reference = cdc_reference(
            age=age, measurement_method=measurement_method, default_youngest_reference=default_youngest_reference
        )
    except:  #  there is no reference for the age supplied
        return LookupError("There is no CDC reference for the age supplied.")


    if invalid_data:
        raise LookupError(data_error)
    else:
        return selected_reference["measurement"][measurement_method][sex]


def select_reference_data_for_cdc_chart(
    cdc_reference_name: str,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False,
):

    # takes a cdc reference name (see parameter constants), measurement_method and sex to return
    # reference data - NOTE for the moment Fenton is not implemented as license not yet secured and reference data therefore not committed to the repo

    if cdc_reference_name == FENTON:
        try:
            fenton_preterm_reference = cdc_lms_array_for_measurement_and_sex(
                age=-0.01, # an arbritrary age to select the preterm data
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=False # should never need younger reference in this calculation
            )
        except:
            fenton_preterm_reference = []
        return fenton_preterm_reference
    elif cdc_reference_name == CDC_INFANT:
        try:
            cdc_infant_reference = cdc_lms_array_for_measurement_and_sex(
                age=0.04, # an arbritrary age to select the infant data
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference
            )
        except:
            cdc_infant_reference = []
        return cdc_infant_reference
    else:
        try:
            cdc_children_reference = cdc_lms_array_for_measurement_and_sex(
                age=3, # an arbritrary age to select the child data
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=False # There is no younger reference data for CDC
            )
        except:
            cdc_children_reference = []
        return cdc_children_reference
