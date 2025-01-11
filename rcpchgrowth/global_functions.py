import math
import scipy.stats as stats
from scipy.interpolate import interp1d
from .uk_who import uk_who_lms_array_for_measurement_and_sex
from .turner import turner_lms_array_for_measurement_and_sex
from .trisomy_21 import trisomy_21_lms_array_for_measurement_and_sex
from .cdc import cdc_lms_array_for_measurement_and_sex
from .trisomy_21_aap import trisomy_21_aap_lms_array_for_measurement_and_sex
from .who import who_lms_array_for_measurement_and_sex

# from scipy import interpolate  #see below, comment back in if swapping interpolation method
# from scipy.interpolate import CubicSpline #see below, comment back in if swapping interpolation method
from .constants.reference_constants import UK_WHO, TURNERS, TRISOMY_21, BMI, CDC, TRISOMY_21_AAP, WHO, UK90_PRETERM,UK_WHO_INFANT, UK_WHO_CHILD,UK90_CHILD,WHO_2006_INFANT,WHO_2006_CHILD,WHO_2007_CHILD,CDC_INFANT,CDC_CHILD,FENTON, TRISOMY_21_AAP_INFANT, TRISOMY_21_AAP_CHILD

"""Public functions"""


def measurement_from_sds(
    reference: str,
    requested_sds: float,
    measurement_method: str,
    sex: str,
    age: float,
    default_youngest_reference: bool = False,
) -> float:

    try:
        lms_value_array_for_measurement = lms_value_array_for_measurement_for_reference(
            reference=reference,
            age=age,
            measurement_method=measurement_method,
            sex=sex,
            default_youngest_reference=default_youngest_reference,
        )
    except LookupError as err:
        raise LookupError(err)

    # get LMS values from the reference: check for age match, interpolate if none
    lms = fetch_lms(
        age=age, lms_value_array_for_measurement=lms_value_array_for_measurement
    )
    l = lms["l"]
    m = lms["m"]
    s = lms["s"]

    observation_value = None

    if reference == CDC and measurement_method == BMI:
        # CDC BMI references require a different method to calculate the centile
        # This is because the centile is calculated from the z-score using the cumulative distribution function
        # if the centile is below 95% (or the inverse if the centile is above 95%)
        # It takes the sigma value from the reference data and applies the cdf to the z-score
       
        sigma = lms["sigma"]
        if requested_sds <= 1.645: # 95th centile
            observation_value = m * (1 + l * s * requested_sds)**(1/l)
        else:
            # inverse of the cdf applied to the bmi percentile - 90 / 10,
            # then multiplied by the sigma value and added to the 95th centile
            p95 = m * (1 + l * s * 1.645)**(1/l) # 95th centile measurement
            centile = stats.norm.cdf(requested_sds) * 100 # convert z-score to centile
            observation_value = stats.norm.ppf((centile - 90)/10) * sigma + p95
    else:
        # all other references use the standard method
        try:
            observation_value = measurement_for_z(z=requested_sds, l=l, m=m, s=s)
        except Exception as e:
            print(f"measurement_from_sds exception {e} - age: {age}, l: {l}, m: {m}, s: {s}, requested_sds: {requested_sds} lms: {lms}")
            return None
    
    if observation_value is not None:
        observation_value = round(observation_value, 4)
    
    return observation_value


def sds_for_measurement(
    reference: str,
    age: float,
    measurement_method: str,
    observation_value: float,
    sex: str,
) -> float:

    try:
        lms_value_array_for_measurement = lms_value_array_for_measurement_for_reference(
            reference=reference,
            age=age,
            measurement_method=measurement_method,
            sex=sex,
            default_youngest_reference=False,  # The oldest child reference should always be selected for SDS calculation
        )
    except LookupError as err:
        raise LookupError(err)

    # get LMS values from the reference: check for age match, interpolate if none
    lms = fetch_lms(
        age=age, lms_value_array_for_measurement=lms_value_array_for_measurement
    )
    l = lms["l"]
    m = lms["m"]
    s = lms["s"]

    # this calculation is different for CDC BMI references and uses the
    # cumulative distribution function to calculate the z-score
    # (if the centile is below 95% (or the inverse if the centile is above 95%)
    if reference == CDC and measurement_method == BMI:
        sigma = lms["sigma"]
        if observation_value > m * (1 + l * s * 1.645)**(1/l):
            # above 95th centile
            p95 = m * (1 + l * s * 1.645)**(1/l)
            centile = stats.norm.cdf((observation_value - p95) / sigma)*10 + 90
            z = stats.norm.ppf(centile/100)
            return z

    return z_score(l=l, m=m, s=s, observation=observation_value)


def percentage_median_bmi(
    reference: str, age: float, actual_bmi: float, sex: str
) -> float:
    """
    public method
    This returns a child"s BMI expressed as a percentage of the median value for age and sex.
    It is used widely in the assessment of malnutrition particularly in children and young people with eating disorders.
    It accepts the reference ('uk-who', 'turners-syndrome' or 'trisomy-21')
    """

    # fetch the LMS values for the requested measurement
    try:
        lms_value_array_for_measurement = lms_value_array_for_measurement_for_reference(
            reference=reference,
            measurement_method=BMI,
            sex=sex,
            age=age,
            default_youngest_reference=False,
        )  # The oldest reference should always be chosen for this calculation
    except LookupError as err:
        raise LookupError(err)

    # get LMS values from the reference: check for age match, interpolate if none
    try:
        lms = fetch_lms(
            age=age, lms_value_array_for_measurement=lms_value_array_for_measurement
        )
    except LookupError as err:
        print(f"percentage median BMI lookup exception: {err}")
        return None

    m = lms["m"]  # this is the median BMI

    percent_median_bmi = (actual_bmi / m) * 100.0
    return percent_median_bmi


def generate_centile(
    z: float,
    centile: float,
    measurement_method: str,
    sex: str,
    reference: str,
    reference_name: str,
    is_sds: bool = False,
) -> list:
    """
    Generates a centile curve for a given reference.
    Takes the z-score equivalent of the centile, the centile to be used as a label, the sex and measurement method.
    Accepts the LMS values for the measurement as a list of dictionaries.
    If the list is empty, the function will return an empty list.
    If default_youngest_reference is True, the youngest reference will be used for overlap values - for example infant and child data sets in the UK-WHO and CDC references have duplicate ages at disjunction ages - 
    this ensures that the centile line runs up to the disjunction.

    To keep the dataset as small as possible, the function will skip non-integer ages above 3 years, but will include all ages below 3 years that are in the LMS list. 
    Paradoxically, the fewer data points, the smoother the curve, though for periods of rapid growth, more data points are needed.
    """


    # if this is an sds line, the label reflects the sds value. The default is to reflect the centile
    label_value = centile
    if is_sds:
        label_value = round(z, 3)

    centile_measurements = []

    # iterate through ages from 23 weeks to 20 years
    UK_90_PRETERM_AGES = [-0.325804244, -0.306639288, -0.287474333, -0.268309377, -0.249144422, -0.229979466, -0.210814511, -0.191649555, -0.1724846, -0.153319644, -0.134154689, -0.114989733, -0.095824778, -0.076659822, -0.057494867, -0.038329911, -0.019164956, 0, 0.019164956, 0.038329911]
    WHO_2006_UNDER_TWOS_AGES = [0.038329911, 0.057494867, 0.076659822, 0.083333333, 0.095824778, 0.114989733, 0.134154689, 0.153319644, 0.166666667, 0.1724846, 0.191649555, 0.210814511, 0.229979466, 0.249144422, 0.25, 0.333333333, 0.416666667, 0.5, 0.583333333, 0.666666667, 0.75, 0.833333333, 0.916666667, 1, 1.083333333, 1.166666667, 1.25, 1.333333333, 1.416666667, 1.5, 1.583333333, 1.666666667, 1.75, 1.833333333, 1.916666667, 2]
    UK_WHO_2006_OVER_TWOS_AGES = [2, 2.083333333, 2.166666667, 2.25, 2.333333333, 2.416666667, 2.5, 2.583333333, 2.666666667, 2.75, 2.833333333, 2.916666667, 3, 3.083333333, 3.166666667, 3.25, 3.333333333, 3.416666667, 3.5, 3.583333333, 3.666666667, 3.75, 3.833333333, 3.916666667, 4]
    WHO_2006_OVER_TWOS_AGES = [2, 2.083333333, 2.166666667, 2.25, 2.333333333, 2.416666667, 2.5, 2.583333333, 2.666666667, 2.75, 2.833333333, 2.916666667, 3, 3.083333333, 3.166666667, 3.25, 3.333333333, 3.416666667, 3.5, 3.583333333, 3.666666667, 3.75, 3.833333333, 3.916666667, 4, 3.083333333, 4.166666667, 4.25, 4.333333333, 4.416666667, 4.5, 4.583333333, 4.666666667, 4.75, 4.833333333, 4.916666667,  5.0]
    WHO_2007_AGES = [5.08,5.17,5.25,5.33,5.42, 5.5,5.58,5.67,5.75,5.83,5.92,6,6.08,6.17,6.25,6.33,6.42, 6.5,6.58,6.67,6.75,6.83,6.92,7,7.08,7.17,7.25,7.33,7.42, 7.5,7.58,7.67,7.75,7.83,7.92,8,8.08,8.17,8.25,8.33,8.42, 8.5,8.58,8.67,8.75,8.83,8.92,9,9.08,9.17,9.25,9.33,9.42, 9.5,9.58,9.67,9.75,9.83,9.92,10,10.08,10.17,10.25,10.33,10.42, 10.5,10.58,10.67,10.75,10.83,10.92,11,11.08,11.17,11.25,11.33,11.42, 11.5,11.58,11.67,11.75,11.83,11.92,12,12.08,12.17,12.25,12.33,12.42, 12.5,12.58,12.67,12.75,12.83,12.92,13,13.08,13.17,13.25,13.33,13.42, 13.5,13.58,13.67,13.75,13.83,13.92,14,14.08,14.17,14.25,14.33,14.42, 14.5,14.58,14.67,14.75,14.83,14.92,15,15.08,15.17,15.25,15.33,15.42, 15.5,15.58,15.67,15.75,15.83,15.92,16,16.08,16.17,16.25,16.33,16.42, 16.5,16.58,16.67,16.75,16.83,16.92,17,17.08,17.17,17.25,17.33,17.42, 17.5,17.58,17.67,17.75,17.83,17.92, 18,18.08,18.17,18.25,18.33,18.42, 18.5,18.58,18.67,18.75,18.83,18.92,19]
    UK90_AGES = [4, 4.083, 4.167, 4.25, 4.333, 4.417, 4.5, 4.583, 4.667, 4.75, 4.833, 4.917, 5, 5.083, 5.167, 5.25, 5.333, 5.417, 5.5, 5.583, 5.667, 5.75, 5.833, 5.917, 6, 6.083, 6.167, 6.25, 6.333, 6.417, 6.5, 6.583, 6.667, 6.75, 6.833, 6.917, 7, 7.083, 7.167, 7.25, 7.333, 7.417, 7.5, 7.583, 7.667, 7.75, 7.833, 7.917, 8, 8.083, 8.167, 8.25, 8.333, 8.417, 8.5, 8.583, 8.667, 8.75, 8.833, 8.917, 9, 9.083, 9.167, 9.25, 9.333, 9.417, 9.5, 9.583, 9.667, 9.75, 9.833, 9.917, 10, 10.083, 10.167, 10.25, 10.333, 10.417, 10.5, 10.583, 10.667, 10.75, 10.833, 10.917, 11, 11.083, 11.167, 11.25, 11.333, 11.417, 11.5, 11.583, 11.667, 11.75, 11.833, 11.917, 12, 12.083, 12.167, 12.25, 12.333, 12.417, 12.5, 12.583, 12.667, 12.75, 12.833, 12.917, 13, 13.083, 13.167, 13.25, 13.333, 13.417, 13.5, 13.583, 13.667, 13.75, 13.833, 13.917, 14, 14.083, 14.167, 14.25, 14.333, 14.417, 14.5, 14.583, 14.667, 14.75, 14.833, 14.917, 15, 15.083, 15.167, 15.25, 15.333, 15.417, 15.5, 15.583, 15.667, 15.75, 15.833, 15.917, 16, 16.083, 16.167, 16.25, 16.333, 16.417, 16.5, 16.583, 16.667, 16.75, 16.833, 16.917, 17, 17.083, 17.167, 17.25, 17.333, 17.417, 17.5, 17.583, 17.667, 17.75, 17.833, 17.917, 18, 18.083, 18.167, 18.25, 18.333, 18.417, 18.5, 18.583, 18.667, 18.75, 18.833, 18.917, 19, 19.083, 19.167, 19.25, 19.333, 19.417, 19.5, 19.583, 19.667, 19.75, 19.833, 19.917, 20]
    CDC_TO_TWO=[0, 0.041666667, 0.125, 0.208333333, 0.291666667, 0.375, 0.458333333, 0.541666667, 0.625, 0.708333333, 0.791666667, 0.875, 0.958333333, 1.041666667, 1.125, 1.208333333, 1.291666667, 1.375, 1.458333333, 1.541666667, 1.625, 1.708333333, 1.791666667, 1.875, 1.958333333, 2]
    CDC_TWO_TWENTY = [2, 2.041666667, 2.125, 2.208333333, 2.291666667, 2.375, 2.458333333, 2.541666667, 2.625, 2.708333333, 2.791666667, 2.875, 2.958333333, 3.041666667, 3.125, 3.208333333, 3.291666667, 3.375, 3.458333333, 3.541666667, 3.625, 3.708333333, 3.791666667, 3.875, 3.958333333, 4.041666667, 4.125, 4.208333333, 4.291666667, 4.375, 4.458333333, 4.541666667, 4.625, 4.708333333, 4.791666667, 4.875, 4.958333333, 5.041666667, 5.125, 5.208333333, 5.291666667, 5.375, 5.458333333, 5.541666667, 5.625, 5.708333333, 5.791666667, 5.875, 5.958333333, 6.041666667, 6.125, 6.208333333, 6.291666667, 6.375, 6.458333333, 6.541666667, 6.625, 6.708333333, 6.791666667, 6.875, 6.958333333, 7.041666667, 7.125, 7.208333333, 7.291666667, 7.375, 7.458333333, 7.541666667, 7.625, 7.708333333, 7.791666667, 7.875, 7.958333333, 8.041666667, 8.125, 8.208333333, 8.291666667, 8.375, 8.458333333, 8.541666667, 8.625, 8.708333333, 8.791666667, 8.875, 8.958333333, 9.041666667, 9.125, 9.208333333, 9.291666667, 9.375, 9.458333333, 9.541666667, 9.625, 9.708333333, 9.791666667, 9.875, 9.958333333, 10.04166667, 10.125, 10.20833333, 10.29166667, 10.375, 10.45833333, 10.54166667, 10.625, 10.70833333, 10.79166667, 10.875, 10.95833333, 11.04166667, 11.125, 11.20833333, 11.29166667, 11.375, 11.45833333, 11.54166667, 11.625, 11.70833333, 11.79166667, 11.875, 11.95833333, 12.04166667, 12.125, 12.20833333, 12.29166667, 12.375, 12.45833333, 12.54166667, 12.625, 12.70833333, 12.79166667, 12.875, 12.95833333, 13.04166667, 13.125, 13.20833333, 13.29166667, 13.375, 13.45833333, 13.54166667, 13.625, 13.70833333, 13.79166667, 13.875, 13.95833333, 14.04166667, 14.125, 14.20833333, 14.29166667, 14.375, 14.45833333, 14.54166667, 14.625, 14.70833333, 14.79166667, 14.875, 14.95833333, 15.04166667, 15.125, 15.20833333, 15.29166667, 15.375, 15.45833333, 15.54166667, 15.625, 15.70833333, 15.79166667, 15.875, 15.95833333, 16.04166667, 16.125, 16.20833333, 16.29166667, 16.375, 16.45833333, 16.54166667, 16.625, 16.70833333, 16.79166667, 16.875, 16.95833333, 17.04166667, 17.125, 17.20833333, 17.29166667, 17.375, 17.45833333, 17.54166667, 17.625, 17.70833333, 17.79166667, 17.875, 17.95833333, 18.04166667, 18.125, 18.20833333, 18.29166667, 18.375, 18.45833333, 18.54166667, 18.625, 18.70833333, 18.79166667, 18.875, 18.95833333, 19.04166667, 19.125, 19.20833333, 19.29166667, 19.375, 19.45833333, 19.54166667, 19.625, 19.70833333, 19.79166667, 19.875, 19.95833333, 20]

    if reference == UK_WHO:
        if reference_name == UK90_PRETERM:
            AGES = UK_90_PRETERM_AGES
        elif reference_name == UK_WHO_INFANT:
            AGES = WHO_2006_UNDER_TWOS_AGES
        elif reference_name ==  UK_WHO_CHILD:
            AGES = UK_WHO_2006_OVER_TWOS_AGES
        elif reference_name == UK90_CHILD:
            AGES = UK90_AGES
    
    elif reference == WHO:
        if reference_name ==WHO_2006_INFANT:
            AGES = WHO_2006_UNDER_TWOS_AGES
        elif reference_name == WHO_2006_CHILD:
            AGES = WHO_2006_OVER_TWOS_AGES
        elif reference_name == WHO_2007_CHILD:
            AGES = WHO_2007_AGES

    elif reference == CDC:
        if reference_name == CDC_INFANT:
            AGES = CDC_TO_TWO
        elif reference_name == CDC_CHILD:
            AGES = CDC_TWO_TWENTY
        elif reference_name == FENTON:
            AGES = []
    
    elif reference == TURNERS:
         AGES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    
    elif reference == TRISOMY_21:
        AGES = [0, 0.08, 0.17, 0.25, 0.33, 0.42, 0.5, 0.58, 0.67, 0.75, 0.83, 0.92, 1, 1.08, 1.17, 1.25, 1.33, 1.42, 1.5, 1.58, 1.67, 1.75, 1.83, 1.92, 2, 2.08, 2.17, 2.25, 2.33, 2.42, 2.5, 2.58, 2.67, 2.75, 2.83, 2.92, 3, 3.08, 3.17, 3.25, 3.33, 3.42, 3.5, 3.58, 3.67, 3.75, 3.83, 3.92, 4, 4.08, 4.17, 4.25, 4.33, 4.42, 4.5, 4.58, 4.67, 4.75, 4.83, 4.92, 5, 5.08, 5.17, 5.25, 5.33, 5.42, 5.5, 5.58, 5.67, 5.75, 5.83, 5.92, 6, 6.08, 6.17, 6.25, 6.33, 6.42, 6.5, 6.58, 6.67, 6.75, 6.83, 6.92, 7, 7.08, 7.17, 7.25, 7.33, 7.42, 7.5, 7.58, 7.67, 7.75, 7.83, 7.92, 8, 8.08, 8.17, 8.25, 8.33, 8.42, 8.5, 8.58, 8.67, 8.75, 8.83, 8.92, 9, 9.08, 9.17, 9.25, 9.33, 9.42, 9.5, 9.58, 9.67, 9.75, 9.83, 9.92, 10, 10.08, 10.17, 10.25, 10.33, 10.42, 10.5, 10.58, 10.67, 10.75, 10.83, 10.92, 11, 11.08, 11.17, 11.25, 11.33, 11.42, 11.5, 11.58, 11.67, 11.75, 11.83, 11.92, 12, 12.08, 12.17, 12.25, 12.33, 12.42, 12.5, 12.58, 12.67, 12.75, 12.83, 12.92, 13, 13.08, 13.17, 13.25, 13.33, 13.42, 13.5, 13.58, 13.67, 13.75, 13.83, 13.92, 14, 14.08, 14.17, 14.25, 14.33, 14.42, 14.5, 14.58, 14.67, 14.75, 14.83, 14.92, 15, 15.08, 15.17, 15.25, 15.33, 15.42, 15.5, 15.58, 15.67, 15.75, 15.83, 15.92, 16, 16.08, 16.17, 16.25, 16.33, 16.42, 16.5, 16.58, 16.67, 16.75, 16.83, 16.92, 17, 17.08, 17.17, 17.25, 17.33, 17.42, 17.5, 17.58, 17.67, 17.75, 17.83, 17.92, 18, 18.08, 18.17, 18.25, 18.33, 18.42, 18.5, 18.58, 18.67, 18.75, 18.83, 18.92, 19, 19.08, 19.17, 19.25, 19.33, 19.42, 19.5, 19.58, 19.67, 19.75, 19.83, 19.92, 20]
    
    elif reference == TRISOMY_21_AAP:
        if reference_name==TRISOMY_21_AAP_INFANT:
            AGES = [0.083333333, 0.166666667, 0.25, 0.333333333, 0.416666667, 0.5, 0.583333333, 0.666666667, 0.75, 0.833333333, 0.916666667, 1, 1.083333333, 1.166666667, 1.25, 1.333333333, 1.416666667, 1.5, 1.583333333, 1.666666667, 1.75, 1.833333333, 1.916666667, 2, 2.083333333, 2.166666667, 2.25, 2.333333333, 2.416666667, 2.5, 2.583333333, 2.666666667, 2.75, 2.833333333, 2.916666667, 3]
        elif reference_name==TRISOMY_21_AAP_CHILD:
            AGES = [3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20]
    
    def should_default_to_youngest_reference(age: float, reference_name: str):
        if reference_name == UK90_PRETERM:
            if age == 0.038329911:
                return True
        if reference_name == UK_WHO_INFANT:
            if age == 2:
                return True
        elif reference_name == UK_WHO_CHILD:
            if age == 4:
                return True
        elif reference_name == WHO_2006_INFANT:
            if age == 0.038329911:
                return True
            if age == 2:
                return True
        elif reference_name == WHO_2006_CHILD:
            if age == 5:
                return True
        elif reference_name == TRISOMY_21_AAP_INFANT:
            if age == 3:
                return True
        return False

    for age in AGES:
        default_youngest_reference = False
        if should_default_to_youngest_reference(age, reference_name):
            default_youngest_reference = True

        try:
            measurement = measurement_from_sds(
                reference=reference,
                measurement_method=measurement_method,
                requested_sds=round(z, 4),
                sex=sex,
                age=age,
                default_youngest_reference=default_youngest_reference,
            )
        except Exception as err:
            print(err)
            measurement = None  #
            continue
        
        if measurement is not None:
            measurement = round(measurement, 4)

        value = create_data_point(
            age=age, measurement=measurement, label_value=label_value
        )
        centile_measurements.append(value)

    return centile_measurements

"""
*** PUBLIC FUNCTIONS THAT CONVERT BETWEEN CENTILE AND SDS
"""


def sds_for_centile(centile: float) -> float:
    """
    converts a centile (supplied as a percentage) using the scipy package to an SDS.
    """
    sds = stats.norm.ppf(centile / 100)
    return sds


def rounded_sds_for_centile(centile: float) -> float:
    """
    converts a centile (supplied as a percentage) using the scipy package to the nearest 2/3 SDS.
    """
    sds = stats.norm.ppf(centile / 100)
    if sds == 0:
        return sds
    else:
        rounded_to_nearest_two_thirds = round(sds / (2 / 3))
        return rounded_to_nearest_two_thirds * (2 / 3)


def centile(z_score: float):
    """
    Converts a Z Score to a p value (2-tailed) using the SciPy library, which it returns as a percentage
    """
    try:
        centile = stats.norm.cdf(z_score) * 100
        return centile
    except Exception as err:
        raise Exception(err)


"""
Private Functions
These are essential to the public functions but are not needed outside this file
"""


def create_data_point(age: float, measurement: float, label_value: str):
    # creates a data point
    if measurement is not None:
        try:
            rounded = round(measurement, 4)
        except Exception as e:
            print(f"create datapoint error: {e} for {measurement}")
            return
    else:
        rounded = None
    value = {"l": label_value, "x": round(age, 4), "y": rounded}
    return value


"""
***** INTERPOLATION FUNCTIONS *****
"""


def cubic_interpolation(
    age: float,
    age_one_below: float,
    age_two_below: float,
    age_one_above: float,
    age_two_above: float,
    parameter_two_below: float,
    parameter_one_below: float,
    parameter_one_above: float,
    parameter_two_above: float,
) -> float:
    """
    See sds function. This method tests if the age of the child (either corrected for prematurity or chronological) is at a threshold of the reference data
    This method is specific to the UK-WHO data set.
    """

    cubic_interpolated_value = 0.0

    t = 0.0  # actual age ///This commented function is Tim Cole"s used in LMSGrowth to perform cubic interpolation - 50000000 loops, best of 5: 7.37 nsec per loop
    tt0 = 0.0
    tt1 = 0.0
    tt2 = 0.0
    tt3 = 0.0

    t01 = 0.0
    t02 = 0.0
    t03 = 0.0
    t12 = 0.0
    t13 = 0.0
    t23 = 0.0

    t = age

    tt0 = t - age_two_below
    tt1 = t - age_one_below
    tt2 = t - age_one_above
    tt3 = t - age_two_above

    t01 = age_two_below - age_one_below
    t02 = age_two_below - age_one_above
    t03 = age_two_below - age_two_above

    t12 = age_one_below - age_one_above
    t13 = age_one_below - age_two_above
    t23 = age_one_above - age_two_above

    cubic_interpolated_value = (
        parameter_two_below * tt1 * tt2 * tt3 / t01 / t02 / t03
        - parameter_one_below * tt0 * tt2 * tt3 / t01 / t12 / t13
        + parameter_one_above * tt0 * tt1 * tt3 / t02 / t12 / t23
        - parameter_two_above * tt0 * tt1 * tt2 / t03 / t13 / t23
    )

    # prerequisite arrays for either of below functions
    # xpoints = [age_two_below, age_one_below, age_one_above, age_two_above]
    # ypoints = [parameter_two_below, parameter_one_below, parameter_one_above, parameter_two_above]

    # this is the scipy cubic spline interpolation function...
    # cs = CubicSpline(xpoints,ypoints,bc_type="natural")
    # cubic_interpolated_value = cs(age) # this also works, but not as accurate: 50000000 loops, best of 5: 7.42 nsec per loop

    # this is the scipy splrep function
    # tck = interpolate.splrep(xpoints, ypoints)
    # cubic_interpolated_value = interpolate.splev(age, tck)   #Matches Tim Cole"s for accuracy but slower: speed - 50000000 loops, best of 5: 7.62 nsec per loop

    return cubic_interpolated_value


def linear_interpolation(
    age: float,
    age_one_below: float,
    age_one_above: float,
    parameter_one_below: float,
    parameter_one_above: float,
) -> float:
    """
    See sds function. This method is to do linear interpolation of L, M and S values for children whose ages are at the threshold of the reference data, making cubic interpolation impossible
    """

    linear_interpolated_value = 0.0

    # linear_interpolated_value = parameter_one_above + (((decimal_age - age_below)*parameter_one_above-parameter_one_below))/(age_above-age_below)
    x_array = [age_one_below, age_one_above]
    y_array = [parameter_one_below, parameter_one_above]
    intermediate = interp1d(x_array, y_array)
    linear_interpolated_value = intermediate(age)
    return linear_interpolated_value


"""
***** DO THE CALCULATIONS *****
"""


def measurement_for_z(z: float, l: float, m: float, s: float) -> float:
    """
    Returns a measurement for a z score, L, M and S
    x = M (1 + L S z)^(1/L) where L is not 0
    Note, in some circumstances, 1 + l * s * z will be negative, and
    it will not be possible to calculate a power.
    In these circumstances, None is returned
    When L is 0, the calculation is x = M e^(S z)
    """
    measurement_value = 0.0
    if l != 0.0:
        first_step = 1 + (l * s * z)
        exponent = 1 / l
        if first_step < 0:
            return None
        try:
            measurement_value = (first_step**exponent) * m
        except Exception as e:
            print("measurement_for_z error: {e}")
            return
    else:
        measurement_value = math.exp(s * z) * m
    return measurement_value


def z_score(l: float, m: float, s: float, observation: float):
    """
    Converts the (age-specific) L, M and S parameters into a z-score
    """
    sds = 0.0
    if l != 0.0:
        sds = (((observation / m) ** l) - 1) / (l * s)
    else:
        sds = math.log(observation / m) / s
    return sds


"""
***** LOOKUP FUNCTIONS *****
"""


def nearest_lowest_index(lms_array: list, age: float) -> int:
    """
    loops through the array of LMS values and returns either
    the index of an exact match or the lowest nearest decimal age
    """
    lowest_index = 0
    for num, lms_element in enumerate(lms_array):
        reference_age = lms_element["decimal_age"]
        if round(reference_age, 16) == round(age, 16):
            lowest_index = num
            break
        else:
            if lms_element["decimal_age"] < age:
                lowest_index = num
    return lowest_index


def fetch_lms(age: float, lms_value_array_for_measurement: list):
    """
    Retuns the LMS for a given age, and sigma if present (CDC BMI references). If there is no exact match in the reference
    an interpolated LMS is returned. Cubic interpolation is used except at the fringes of the
    reference where linear interpolation is used.
    It accepts the age and a python list of the LMS values for that measurement_method and sex.
    """
    age_matched_index = nearest_lowest_index(
        lms_value_array_for_measurement, age
    )  # returns nearest LMS for age
    if round(
        lms_value_array_for_measurement[age_matched_index]["decimal_age"], 4
    ) == round(age, 4):
        # there is an exact match in the data with the requested age
        l = lms_value_array_for_measurement[age_matched_index]["L"]
        m = lms_value_array_for_measurement[age_matched_index]["M"]
        s = lms_value_array_for_measurement[age_matched_index]["S"]

        if "sigma" in lms_value_array_for_measurement[age_matched_index]:
            # CDC BMI references have an additional sigma value
            sigma = lms_value_array_for_measurement[age_matched_index]["sigma"]
            return {"l": l, "m": m, "s": s, "sigma": sigma}
    else:
        # there has not been an exact match in the reference data
        # Interpolation will be required.
        # The age_matched_index is one below the age supplied. There
        # needs to be a value below that, and two values above the supplied age,
        # for cubic interpolation to be possible.
        age_one_below = lms_value_array_for_measurement[age_matched_index][
            "decimal_age"
        ]
        age_one_above = lms_value_array_for_measurement[age_matched_index + 1][
            "decimal_age"
        ]
        parameter_one_below = lms_value_array_for_measurement[age_matched_index]
        parameter_one_above = lms_value_array_for_measurement[age_matched_index + 1]

        if (
            age_matched_index >= 1
            and age_matched_index < len(lms_value_array_for_measurement) - 2
            and "sigma" not in lms_value_array_for_measurement[age_matched_index] # CDC BMI references have an additional sigma value
            # and CDC only use linear interpolation
        ):
            # cubic interpolation is possible
            age_two_below = lms_value_array_for_measurement[age_matched_index - 1][
                "decimal_age"
            ]
            age_two_above = lms_value_array_for_measurement[age_matched_index + 2][
                "decimal_age"
            ]
            parameter_two_below = lms_value_array_for_measurement[age_matched_index - 1]
            parameter_two_above = lms_value_array_for_measurement[age_matched_index + 2]

            l = cubic_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_two_below=age_two_below,
                age_one_above=age_one_above,
                age_two_above=age_two_above,
                parameter_two_below=parameter_two_below["L"],
                parameter_one_below=parameter_one_below["L"],
                parameter_one_above=parameter_one_above["L"],
                parameter_two_above=parameter_two_above["L"],
            )
            m = cubic_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_two_below=age_two_below,
                age_one_above=age_one_above,
                age_two_above=age_two_above,
                parameter_two_below=parameter_two_below["M"],
                parameter_one_below=parameter_one_below["M"],
                parameter_one_above=parameter_one_above["M"],
                parameter_two_above=parameter_two_above["M"],
            )
            s = cubic_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_two_below=age_two_below,
                age_one_above=age_one_above,
                age_two_above=age_two_above,
                parameter_two_below=parameter_two_below["S"],
                parameter_one_below=parameter_one_below["S"],
                parameter_one_above=parameter_one_above["S"],
                parameter_two_above=parameter_two_above["S"],
            )
            if "sigma" in lms_value_array_for_measurement[age_matched_index]:
                # CDC BMI references have an additional sigma value
                sigma = cubic_interpolation(
                    age=age,
                    age_one_below=age_one_below,
                    age_two_below=age_two_below,
                    age_one_above=age_one_above,
                    age_two_above=age_two_above,
                    parameter_two_below=parameter_two_below["sigma"],
                    parameter_one_below=parameter_one_below["sigma"],
                    parameter_one_above=parameter_one_above["sigma"],
                    parameter_two_above=parameter_two_above["sigma"],
                )
                return {"l": l, "m": m, "s": s, "sigma": sigma}
        else:
            # we are at the thresholds of this reference or are using CDC. Only linear interpolation is possible
            l = linear_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_one_above=age_one_above,
                parameter_one_below=parameter_one_below["L"],
                parameter_one_above=parameter_one_above["L"],
            )
            m = linear_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_one_above=age_one_above,
                parameter_one_below=parameter_one_below["M"],
                parameter_one_above=parameter_one_above["M"],
            )
            s = linear_interpolation(
                age=age,
                age_one_below=age_one_below,
                age_one_above=age_one_above,
                parameter_one_below=parameter_one_below["S"],
                parameter_one_above=parameter_one_above["S"],
            )
            if "sigma" in lms_value_array_for_measurement[age_matched_index]:
                # CDC BMI references have an additional sigma value
                sigma = linear_interpolation(
                    age=age,
                    age_one_below=age_one_below,
                    age_one_above=age_one_above,
                    parameter_one_below=parameter_one_below["sigma"],
                    parameter_one_above=parameter_one_above["sigma"],
                )
                return {"l": l, "m": m, "s": s, "sigma": sigma}

    return {"l": l, "m": m, "s": s}


def lms_value_array_for_measurement_for_reference(
    reference: str,
    age: float,
    measurement_method: str,
    sex: str,
    default_youngest_reference: bool = False,
) -> list:
    """
    This is a private function which returns the LMS array for measurement_method and sex and reference
    It accepts the reference ('uk-who', 'turners-syndrome', 'trisomy-21', 'cdc')
    If the UK-WHO reference is requested, it is possible to be select the younger reference for overlap values,
    using the default_youngest_reference flag.
    """

    if reference == UK_WHO:
        try:
            lms_value_array_for_measurement = uk_who_lms_array_for_measurement_and_sex(
                age=age,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference,
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == WHO:
        try:
            lms_value_array_for_measurement = who_lms_array_for_measurement_and_sex(
                age=age,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference,
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == TURNERS:
        try:
            lms_value_array_for_measurement = turner_lms_array_for_measurement_and_sex(
                measurement_method=measurement_method, sex=sex, age=age
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == TRISOMY_21:
        try:
            lms_value_array_for_measurement = (
                trisomy_21_lms_array_for_measurement_and_sex(
                    measurement_method=measurement_method, sex=sex, age=age
                )
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == CDC:
        try:
            lms_value_array_for_measurement = cdc_lms_array_for_measurement_and_sex(
                age=age,
                measurement_method=measurement_method,
                sex=sex,
                default_youngest_reference=default_youngest_reference
            )
        except LookupError as error:
            raise LookupError(error)
    elif reference == TRISOMY_21_AAP:
        try:
            lms_value_array_for_measurement = trisomy_21_aap_lms_array_for_measurement_and_sex(
                age=age, measurement_method=measurement_method, sex=sex, default_youngest_reference=default_youngest_reference)
        except LookupError as error:
            raise LookupError(error)
    else:
        raise ValueError("No or incorrect reference supplied")
    return lms_value_array_for_measurement

