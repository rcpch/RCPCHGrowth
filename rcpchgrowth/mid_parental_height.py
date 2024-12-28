from .constants import HEIGHT, MALE, FEMALE, UK_WHO, WHO
from .global_functions import sds_for_measurement
"""
Functions to calculate mid-parental height

cf 
Tanner JM, Whitehouse RH, Takaishi M. Standards from birth to maturity for height, weight, height velocity, and weight velocity: British children, 1965. I. Arch Dis Child. 1966;41(219):454-471.
The strengths and limitations of parental heights as a predictor of attained height, Charlotte M Wright, Tim D Cheetham, Arch Dis Child 1999;81:257–260
"""

def mid_parental_height(maternal_height, paternal_height, sex):
    """
    Calculate mid-parental height
    """
    if sex == MALE:
        return (maternal_height + paternal_height + 13) / 2
    else:
        return (maternal_height + paternal_height - 13) / 2

def mid_parental_height_z(maternal_height, paternal_height, reference=UK_WHO):
    """
    Calculate mid-parental height standard deviation
    """
    
    # convert parental heights to z-scores
    adult_age = 20.0
    if reference == WHO:
        adult_age = 19.0
    
    maternal_height_z = sds_for_measurement(reference=reference, age=adult_age, measurement_method=HEIGHT, observation_value=maternal_height, sex=FEMALE)
    paternal_height_z = sds_for_measurement(reference=reference, age=adult_age, measurement_method=HEIGHT, observation_value=paternal_height, sex=MALE)

    # take the means of the z-scores and apply the regression coefficient of 0.5 - simplifed: (MatHtz +PatHtz)/4
    mid_parental_height_z_score = (maternal_height_z + paternal_height_z) / 4.0

    return mid_parental_height_z_score

def expected_height_z_from_mid_parental_height_z(mid_parental_height_z):
    """
    Calculate expected height z score from mid-parental height z-score

    Ninety per cent of children had values within 1.4 SDS of their expected SDS (just over two
    centile spaces) and only 1% had values > 2 SDS (three centile spaces) below (cf Wright et al)
    """
    
    return mid_parental_height_z * 0.5

def lower_and_upper_limits_of_expected_height_z(mid_parental_height_z):
    """
    Calculate lower and upper limits of expected height z score from mid-parental height z-score
    Returns a tuple of (lower, upper) limits
    """
    
    return mid_parental_height_z - 1.4, mid_parental_height_z + 1.4