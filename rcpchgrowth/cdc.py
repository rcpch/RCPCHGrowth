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

data_path = Path(data_directory, "who_infants.json")  # 2 weeks to 2 years
with open(data_path) as json_file:
    WHO_INFANTS_DATA = json.load(json_file)
    json_file.close()

data_path = Path(data_directory, "cdc.json")  # 2 years to 20 years
with open(data_path) as json_file:
    UK90_CHILD_DATA = json.load(json_file)
    json_file.close()

# public functions


def reference_data_absent(age: float, measurement_method: str, sex: str):
    """
    Helper function.
    Returns boolean
    Tests presence of valid reference data for a given measurement request

    Reference data is not complete for all ages/sexes/measurements.
     - OFC data is currently not implemented at all
     - WHO data is used from 0-2 years
     Currently it is not that clear if the CDC data on the website matches the WHO data we have (esp for OFC) but it should
    """

    if age < TWO_YEARS:
        return True, "CDC data does not exist below 2 years."
    if age > TWENTY_YEARS:  # upper threshold of UK90 data
        return True, "CDC data does not exist above 20 years."


def cdc_reference(age: float, default_youngest_reference: bool = False) -> json:
    """
    The purpose of this function is to choose the correct reference for calculation.
    The CDC standard is an unusual case because it combines two different reference sources.
    - CDC reference runs from 2 y to 20 y
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
    elif age < WHO_NEWBORN_LOWER_THRESHOLD:
        # Below 42 weeks, the UK90 preterm data is always used
        return FENTON_DATA

    elif age < WHO_CHILD_LOWER_THRESHOLD:
        # Children beyond 0 but below 2 years are measured lying down using WHO data
        if age == 0 and default_youngest_reference:
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 lying and standing in centile curve generation
            return FENTON_DATA
        return WHO_DATA  # this will need a new reference file as the current infants file starts at 2 weeks

    elif age < WHO_CHILDREN_UPPER_THRESHOLD:
        # Children 2 years and beyond but below 4 years are measured standing up using WHO data
        if age == 2.0 and default_youngest_reference:
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 lying and standing in centile curve generation
            return WHO_INFANTS_DATA
        return CDC_DATA

    elif age <= CDC_UPPER_THRESHOLD:
        # All children 4 years and above are measured using UK90 child data
        if age == 4.0 and default_youngest_reference:
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 and UK90 in centile curve generation
            return WHO_CHILD_DATA
        return UK90_CHILD_DATA

    else:
        return ValueError("There is no CDC reference data above the age of 20 years.")


def uk_who_lms_array_for_measurement_and_sex(
    age: float,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False,
) -> list:

    # selects the correct lms data array from the patchwork of references that make up UK-WHO

    try:
        selected_reference = cdc_reference(
            age=age, default_youngest_reference=default_youngest_reference
        )
    except:  #  there is no reference for the age supplied
        return LookupError("There is no CDC reference for the age supplied.")

    # Check that the measurement requested has reference data at that age

    invalid_data, data_error = reference_data_absent(
        age=age, measurement_method=measurement_method, sex=sex
    )

    if invalid_data:
        raise LookupError(data_error)
    else:
        return selected_reference["measurement"][measurement_method][sex]


# def select_reference_data_for_uk_who_chart(
#     uk_who_reference_name: str,
#     measurement_method: str,
#     sex: str):

#     # takes a uk_who_reference name (see parameter constants), measurement_method and sex to return
#     # reference data

#     if uk_who_reference_name == UK90_PRETERM:
#         try:
#             uk90_preterm_reference = uk_who_lms_array_for_measurement_and_sex(
#                 age=-0.01,
#                 measurement_method=measurement_method,
#                 sex=sex,
#                 default_youngest_reference=False # should never need younger reference in this calculation
#             )
#         except:
#             uk90_preterm_reference = []
#         return uk90_preterm_reference
#     elif uk_who_reference_name == UK_WHO_INFANT:
#         try:
#             uk_who_infants_reference = uk_who_lms_array_for_measurement_and_sex(
#                 age=0.04,
#                 measurement_method=measurement_method,
#                 sex=sex,
#                 default_youngest_reference=False # should never need younger reference in this calculation
#             )
#         except:
#             uk_who_infants_reference = []
#         return uk_who_infants_reference
#     elif uk_who_reference_name == UK_WHO_CHILD:
#         try:
#             uk_who_children_reference = uk_who_lms_array_for_measurement_and_sex(
#                 age=2.0,
#                 measurement_method=measurement_method,
#                 sex=sex,
#                 default_youngest_reference=False # should never need younger reference in this calculation
#             )
#         except:
#             uk_who_children_reference = []
#         return uk_who_children_reference
#     elif uk_who_reference_name == UK90_CHILD:
#         try:
#             uk90_children_reference = uk_who_lms_array_for_measurement_and_sex(
#                 age=4.0,
#                 measurement_method=measurement_method,
#                 sex=sex,
#                 default_youngest_reference=False # should never need younger reference in this calculation
#             )
#         except:
#             uk90_children_reference = []
#         return uk90_children_reference
#     else:
#         raise LookupError(
#             f"No data found for {measurement_method} in {sex}s in {uk_who_reference_name}")
