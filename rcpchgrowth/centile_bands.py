# imports from rcpchgrowth
from rcpchgrowth.constants.reference_constants import COLE_TWO_THIRDS_SDS_NINE_CENTILES, THREE_PERCENT_CENTILES, UK_WHO, CDC
from .constants import BMI, HEAD_CIRCUMFERENCE,THREE_PERCENT_CENTILE_COLLECTION,COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION ,FIVE_PERCENT_CENTILES, FIVE_PERCENT_CENTILE_COLLECTION, EIGHTY_FIVE_PERCENT_CENTILES, EIGHTY_FIVE_PERCENT_CENTILE_COLLECTION, MAXIMUM_HEIGHT_WEIGHT_OFC_ADVISORY_SDS, MINIMUM_HEIGHT_WEIGHT_OFC_ADVISORY_SDS, MAXIMUM_BMI_ADVISORY_SDS, MINIMUM_BMI_ADVISORY_SDS, HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI
from .global_functions import rounded_sds_for_centile, sds_for_centile

# Recommendations from Project board for reporting Centiles

# Lower limit	Upper limit	Centile band	Weight,  Height, Head	BMI
# 	<-6 		Probable error	Probable error
# -6.00	-2.84	Below 0.4th	Below normal range	Very thin
# -2.84	-2.50	0.4th 		Low BMI
# -2.50	-2.17	0.4th-2nd		Low BMI
# -2.17	-1.83	2nd		
# -1.83	-1.50	2nd -9th		
# -1.50	-1.16	9th		
# -1.16	-0.84	9th-25th		
# -0.84	-0.50	25th		
# -0.50	-0.17	25-50th 		
# -0.17	0.17	50th 		
# 0.17	0.50	50-75th 		
# 0.50	0.84	75th 		
# 0.84	1.16	75-91st 		
# 1.16	1.50	91st 		
# 1.50	1.83	91-98th 		Overweight
# 1.83	2.17	98th 		Overweight
# 2.17	2.50	98-99.6th 		Very overweight (obese)
# 2.50	2.84	99.6th 		Very overweight (obese)
# 2.84	6.00	Above 99.6th	Above normal range	Severely obese
# 	>6.00		Probable error	Probable error
"""
In fact we have changed these slightly as sometimes we might not always use the standard Cole nine
centile format. In those circumstances hard coding these thresholds would not work.
Instead @a-wei-0513 has calculated 0.25 distance between the lines to be 'on or near'. This is very close
to these numbers and would accommodate different centile formats.
"""

def return_suffix(centile: float)->str:
    # Converts a cardinal number to an ordinal by adding a suffix 'st', 'nd', 'rd' or 'th'
    # Accepts decimals and negative numbers
    # This function only works if the centile is received already rounded to 1 decimal place or 2 decimal places if reference is CDC and measurement method is BMI

    # Note that if reference is CDC and measurement method is BMI, the centile is rounded to 2 decimal places if centile > 99.9

    
    # centile should not be < 0 or > 100
    if centile <=0:
        return "below lowest centile.;"
    if centile >= 100:
        return "above highest centile."

    
    final_number = centile
    if isinstance(centile, float) and centile.is_integer():
        final_number = int(centile) # convert to integer if it is a whole number as removes the decimal point

    suffix="th" # this is the default
    
    # get the final digit
    string_from_number = str(final_number)
    final_digit = int(string_from_number[len(string_from_number)-1: len(string_from_number)])
    if final_digit == 1:
        suffix = "st"
    elif final_digit == 2:
        suffix = "nd"
    elif final_digit == 3:
        suffix = "rd"
    
    # 11, 12, 13 are special cases as they take 'th'
    # get the final 2 digits if not a decimal
    if isinstance(final_number, float) and final_number.is_integer() or (isinstance(final_number, int) and len(string_from_number) > 1):
        final_two_digits = string_from_number[len(string_from_number)-2: len(string_from_number)]
        if int(final_two_digits) > 10 and int(final_two_digits) < 14:
            suffix = "th"

    return f"{string_from_number}{suffix}"

def quarter_distances(centile):
    """
    return sds of points that are +/- 0.25*0.666 sds space from the centile line

    0.25 * 0.666 comes from the definition that a point within 0.25 centile space
     from the centile line in a UK growth chart is considered as on the centile
    this distance from centile line is used for all centile patterns, regardless of 
     whether the centile lines are equally spaced apart
    """
    sds = sds_for_centile(centile)
    quarter_distance = 0.25 * 0.666
    return sds - quarter_distance, sds + quarter_distance


def generate_centile_band_ranges(centile_collection):
    """
    returns a list of tuples representing ranges of on centile line and between centiles
    """
    centile_ranges = []
    for centile in centile_collection:
        centile_ranges.extend(quarter_distances(centile))
    centile_bands = list(zip(centile_ranges[:-1],centile_ranges[1:]))

    return centile_bands


def centile_band_for_centile(sds: float, measurement_method: str, centile_format: str = COLE_TWO_THIRDS_SDS_NINE_CENTILES, reference=UK_WHO)->str:
    """
        this function returns a centile band into which the sds falls
    
        params: accepts a sds: float
        params: accepts a measurement_method as string
        params: accepts array of centiles representing the centile lines

        These advice messages appear in the tooltips of the growth charts in the RCPCH Growth Chart and are advisory only. They do not reject data entry.
    """
    
    centile_collection = []
    if centile_format == THREE_PERCENT_CENTILES:
        centile_collection = THREE_PERCENT_CENTILE_COLLECTION
    elif centile_format == FIVE_PERCENT_CENTILES:
        centile_collection = FIVE_PERCENT_CENTILE_COLLECTION
    elif centile_format == EIGHTY_FIVE_PERCENT_CENTILES:
        centile_collection = EIGHTY_FIVE_PERCENT_CENTILE_COLLECTION
    elif centile_format == COLE_TWO_THIRDS_SDS_NINE_CENTILES:
        centile_collection = COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION

    centile_band_ranges = generate_centile_band_ranges(centile_collection)

    upper_threshold = MAXIMUM_HEIGHT_WEIGHT_OFC_ADVISORY_SDS
    lower_threshold = MINIMUM_HEIGHT_WEIGHT_OFC_ADVISORY_SDS
    if measurement_method == BMI:
        measurement_method = "body mass index"
        upper_threshold = MAXIMUM_BMI_ADVISORY_SDS
        lower_threshold = MINIMUM_BMI_ADVISORY_SDS
    elif measurement_method == HEAD_CIRCUMFERENCE:
        measurement_method = "head circumference"

    if sds < lower_threshold:
        return f"This {measurement_method} measurement is well outside the normal range. Please check its accuracy."
    elif sds > upper_threshold:
        return f"This {measurement_method} measurement is well outside the normal range. Please check its accuracy."
    elif sds <= centile_band_ranges[0][0]:
        return f"This {measurement_method} measurement is below the normal range."
    elif sds > centile_band_ranges[-1][1]:
        return f"This {measurement_method} measurement is above the normal range."        
    else:
        #even indices of centile_bands list is always on centile
                    
        #odd indices of centile_bands list is always between centiles
        for r in range(len(centile_band_ranges)):
            if centile_band_ranges[r][0] <= sds < centile_band_ranges[r][1]:
                if r%2 == 0:
                    centile = centile_collection[r//2]
                    suffixed_centile = return_suffix(centile)
                    return f"This {measurement_method} measurement is on or near the {suffixed_centile} centile."
                else:
                    lower_centile = centile_collection[(r-1)//2]
                    lower_suffixed_centile = return_suffix(lower_centile)
                    upper_centile = centile_collection[(r+1)//2]
                    upper_suffixed_centile = return_suffix(upper_centile)
                    return f"This {measurement_method} measurement is between the {lower_suffixed_centile} and {upper_suffixed_centile} centiles."
