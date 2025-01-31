"""
Handles UK-WHO-specific reference data selection
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
    data_directory, "uk90_preterm.json")  # 23 - 42 weeks gestation
with open(data_path) as json_file:
    UK90_PRETERM_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    data_directory, "uk90_term.json")  # 37-42 weeks gestation
with open(data_path) as json_file:
    UK90_TERM_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    data_directory, "who_infants.json")  # 2 weeks to 2 years
with open(data_path) as json_file:
    WHO_INFANTS_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    data_directory, "who_children.json")  # 2 years to 4 years
with open(data_path) as json_file:
    WHO_CHILD_DATA = json.load(json_file)
    json_file.close()

data_path = Path(
    data_directory, "uk90_child.json")  # 4 years to 20 years
with open(data_path) as json_file:
    UK90_CHILD_DATA = json.load(json_file)
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

    if age < TWENTY_THREE_WEEKS_GESTATION:  # lower threshold of UK90 data
        return True, "UK-WHO data does not exist below 23 weeks gestation."

    if age > TWENTY_YEARS:  # upper threshold of UK90 data
        return True, "UK-WHO data does not exist above 20 years."

    if measurement_method == HEIGHT and age < TWENTY_FIVE_WEEKS_GESTATION:
        return True, "UK-WHO length data does not exist in infants below 25 weeks gestation."

    elif measurement_method == BMI and age < FORTY_TWO_WEEKS_GESTATION:
        return True, "UK-WHO BMI data does not exist below 2 weeks of age."

    elif measurement_method == HEAD_CIRCUMFERENCE:
        if (sex == MALE and age > EIGHTEEN_YEARS) or (sex == FEMALE and age > SEVENTEEN_YEARS):
            if sex == MALE:
                return True, "UK-WHO head circumference data does not exist in boys over 18 y of age."
            else:
                return True, "UK-WHO head circumference data does not exist in girls over 17 y of age."
        else:
            return False, ""
    else:
        return False, ""


def uk_who_reference(
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

    # These conditionals are to select the correct reference
    if age < UK90_REFERENCE_LOWER_THRESHOLD:
        # Below the range for which we have reference data, we can't provide a calculation.
        raise ValueError("There is no UK90 reference data below 23 weeks gestation")
    elif age < UK_WHO_INFANT_LOWER_THRESHOLD:
        # Below 42 weeks, the UK90 preterm data is always used
        return UK90_PRETERM_DATA

    elif age < WHO_CHILD_LOWER_THRESHOLD:
        # Children beyond 2 weeks but below 2 years are measured lying down using WHO data
        if age == FORTY_TWO_WEEKS_GESTATION and default_youngest_reference:
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 lying and standing in centile curve generation
            return UK90_PRETERM_DATA
        return WHO_INFANTS_DATA

    elif age < WHO_CHILDREN_UPPER_THRESHOLD:
        # Children 2 years and beyond but below 4 years are measured standing up using WHO data
        if age == 2.0 and default_youngest_reference:
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 lying and standing in centile curve generation
            return WHO_INFANTS_DATA     
        return WHO_CHILD_DATA
        
    elif age <= UK90_UPPER_THRESHOLD:
        # All children 4 years and above are measured using UK90 child data
        if age == 4.0 and default_youngest_reference:
            # If default_youngest_reference is True, the younger reference is used to calculate values
            # This is specifically for the overlap between WHO 2006 and UK90 in centile curve generation
            return WHO_CHILD_DATA
        return UK90_CHILD_DATA

    else:
        raise ValueError("There is no UK90 reference data above the age of 20 years.")


def uk_who_lms_array_for_measurement_and_sex(
    age: float,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False
) -> list:

    # selects the correct lms data array from the patchwork of references that make up UK-WHO

    try:
        selected_reference = uk_who_reference(
            age=age,
            default_youngest_reference=default_youngest_reference
        )
    except:  #  there is no reference for the age supplied
        raise LookupError("There is no UK-WHO reference for the age supplied.")

    # Check that the measurement requested has reference data at that age

    invalid_data, data_error = reference_data_absent(
        age=age,
        measurement_method=measurement_method,
        sex=sex)

    if invalid_data:
        raise LookupError(data_error)
    else:
        return selected_reference["measurement"][measurement_method][sex]


def select_reference_data_for_uk_who_chart(
    uk_who_reference_name: str, 
    measurement_method: str, 
    sex: str):

    # takes a uk_who_reference name (see parameter constants), measurement_method and sex to return
    # reference data

    if uk_who_reference_name == UK90_PRETERM:
        try:
            uk90_preterm_reference = uk_who_lms_array_for_measurement_and_sex(
                age=-0.01,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=False # should never need younger reference in this calculation
            )
        except:
            uk90_preterm_reference = []
        return uk90_preterm_reference
    elif uk_who_reference_name == UK_WHO_INFANT:
        try:
            uk_who_infants_reference = uk_who_lms_array_for_measurement_and_sex(
                age=0.04,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=False # should never need younger reference in this calculation
            )
        except:
            uk_who_infants_reference = []
        return uk_who_infants_reference
    elif uk_who_reference_name == UK_WHO_CHILD:
        try:
            uk_who_children_reference = uk_who_lms_array_for_measurement_and_sex(
                age=2.0,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=False # should never need younger reference in this calculation
            )
        except:
            uk_who_children_reference = []
        return uk_who_children_reference
    elif uk_who_reference_name == UK90_CHILD:
        try:
            uk90_children_reference = uk_who_lms_array_for_measurement_and_sex(
                age=4.0,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=False # should never need younger reference in this calculation
            )
        except:
            uk90_children_reference = []
        return uk90_children_reference
    else:
        raise LookupError(
            f"No data found for {measurement_method} in {sex}s in {uk_who_reference_name}")
