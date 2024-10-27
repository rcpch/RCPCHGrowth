import json
from importlib import resources
from pathlib import Path
from .constants import *
# from .global_functions import z_score, cubic_interpolation, linear_interpolation, centile, measurement_for_z, nearest_lowest_index, fetch_lms
# import timeit #see below, comment back in if timing functions in this module

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



data_path = Path(data_directory, "trisomy_21_aap_infants.json")
with open(data_path) as json_file:
            TRISOMY_21_AAP_INFANT_DATA = json.load(json_file)
            json_file.close()

data_path = Path(data_directory, "trisomy_21_aap_children.json")
with open(data_path) as json_file:
            TRISOMY_21_AAP_CHILD_DATA = json.load(json_file)
            json_file.close()

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
     - There is only BMI reference data until 20y
     - Head circumference reference data is available until 18.0y
     - lowest threshold is 1 month, upper threshold is 20y
    """

    if age < 0: # lower threshold of trisomy_21 data
        return True, "No Trisomy 21 (AAP) reference data exists below 40 weeks gestation"
    
    if age < 0.083 and measurement_method in ['height', 'ofc']: # lower threshold of trisomy_21 data
        return True, "No Trisomy 21 (AAP) reference data exists below 1 month of age for height or head circumference."
    
    if age < 2 and measurement_method == 'bmi': # lower threshold of trisomy_21 data
         return True, "No Trisomy 21 (AAP) reference data exists below 2 years of age for BMI."
    
    if age > TWENTY_YEARS: # upper threshold of trisomy_21 data
        return True, "Trisomy 21 reference data does not exist over the age of 20y."
    
    return False, None

def trisomy_21_aap_lms_array_for_measurement_and_sex(
        measurement_method: str,
        sex: str,
        age: float,
        default_youngest_reference: bool = False
    ):
    # returns the LMS array for a given measurement
    # raises a LookupError if the data is not available
    # No need for default_youngest_reference as all the data is from the same source
    # Note there is an overlap in the age ranges of the two datasets, so the age parameter is used to select the correct dataset - below 36mths the data is more granular

    data_invalid, data_error = reference_data_absent(age=age, measurement_method=measurement_method, sex=sex)

    if data_invalid:
        raise LookupError(f"Reference data absent: {data_error}")
    else:
        if age <= 3.0 and measurement_method in ['height', 'weight', 'ofc']:
            if measurement_method == 'ofc' and age==3 and default_youngest_reference:
                return TRISOMY_21_AAP_INFANT_DATA["measurement"][measurement_method][sex]
            elif measurement_method == 'ofc' and age==3 and not default_youngest_reference:
                return TRISOMY_21_AAP_CHILD_DATA["measurement"][measurement_method][sex]
            
            return TRISOMY_21_AAP_INFANT_DATA["measurement"][measurement_method][sex]
        else:
            return TRISOMY_21_AAP_CHILD_DATA["measurement"][measurement_method][sex]

def select_reference_data_for_trisomy_21_aap(trisomy_21_aap_reference_name, measurement_method:str, sex:str, default_youngest_reference: bool = False):

    if trisomy_21_aap_reference_name == TRISOMY_21_AAP_INFANT:
        try:
            return_value = trisomy_21_aap_lms_array_for_measurement_and_sex(measurement_method=measurement_method, sex=sex, age=1.0, default_youngest_reference=default_youngest_reference) # select arbitrary age of 1 y for infant data
        except:
            raise LookupError(f"No data for {measurement_method} in the {sex} Trisomy 21 (AAP) dataset (<36mths).")
    elif trisomy_21_aap_reference_name == TRISOMY_21_AAP_CHILD:
        try:
            return_value = trisomy_21_aap_lms_array_for_measurement_and_sex(measurement_method=measurement_method, sex=sex, age=4.0, default_youngest_reference=default_youngest_reference) # select arbitrary age of 4 y for child data
        except:
            raise LookupError(f"No data for {measurement_method} in the {sex} Trisomy 21 (US) dataset (>3y).")
    return return_value