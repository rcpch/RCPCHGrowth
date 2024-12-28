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
from .constants.reference_constants import UK_WHO, TURNERS, TRISOMY_21, BMI, CDC, TRISOMY_21_AAP, WHO


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
    lms_array_for_measurement: list,
    reference: str,
    is_sds: bool = False,
    default_youngest_reference: bool = False,
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

    for item in lms_array_for_measurement:

        try:
            measurement = measurement_from_sds(
                reference=reference,
                measurement_method=measurement_method,
                requested_sds=round(z, 4),
                sex=sex,
                age=round(item['decimal_age'], 4),
                default_youngest_reference=default_youngest_reference,
            )
        except Exception as err:
            print(err)
            measurement = None  #
            continue

        if measurement is not None:
            measurement = round(measurement, 4)

        value = create_data_point(
            age=round(item['decimal_age'], 4), measurement=measurement, label_value=label_value
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
