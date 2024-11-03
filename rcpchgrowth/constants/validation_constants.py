"""
These constants are intended to be used throughout both the rcpchgrowth module
and the API for validation of input values and rejection of very high or low values

The constants used previously drew on the Guiness Book of Records and other sources to set hard limits.
These were replaced with SDS sds_advisory and sds_error values in the rcpchgrowth-python repository as per issue #32
"""

# HEIGHT CONSTANTS
# The smallest baby was report by the BBC on 9/8/2021 (https://www.bbc.co.uk/news/world-asia-58141756.amp)
# to have a length of just 24cm and was born at 25 weeks gestation, discharged at 13 mths of age (chronological)
# from Singapore's National University Hospital
# The tallest person for whom there is irrefutable evidence is
# Robert Pershing Wadlow who was 2.72m (8 ft 11.1 in) tall at his death in 1940
# https://en.wikipedia.org/wiki/Robert_Wadlow

# WEIGHT CONSTANTS
# The smallest baby was report by the BBC on 9/8/2021 (https://www.bbc.co.uk/news/world-asia-58141756.amp)
# to weigh just 212g and was born at 25 weeks gestation, discharged at 13 mths of age (chronological)
# from Singapore's National University Hospital
# The heaviest man according to google is Jon Brower Minnoch (US)
# who had suffered from obesity since childhood. In September 1976,
# he measured 185 cm (6 ft 1 in) tall and weighed 442 kg (974 lb; 69 st 9 lb)
# https://en.wikipedia.org/wiki/Jon_Brower_Minnoch

# OFC CONSTANTS
# We couldn't find a good answer for the 'largest human head' that we could use
# Instead have presumed that 100 is a good maximum, given that pathological states
# causing very large head size (eg hydrocephalus) render the OFC meaningless for
# growth measurement and assessment purposes.

# BMI CONSTANTS
# Again, John Brower Minnoch comes to our rescue here. HIs body mass index
# at the time of his death was 105 kg/m2. In terms of the lowest body mass index ever recorded
# there was nly limited web search information that suggested 7.5 kg.m2 as the lowest ever.

# GESTATION CONSTANTS
MINIMUM_GESTATION_WEEKS = 22
MINIMUM_GESTATION_WEEKS_ERROR = f"It is very unlikely that a gestational age of less than {MINIMUM_GESTATION_WEEKS} weeks is correct"
MAXIMUM_GESTATION_WEEKS = 44
MAXIMUM_GESTATION_WEEKS_ERROR = f"It is very unlikely that a gestational age of more than {MAXIMUM_GESTATION_WEEKS} weeks is correct"

# PARENTAL HEIGHT CONSTANTS
MINIMUM_PARENTAL_HEIGHT_CM = 50
# the shortest man in the world was 54.6 cm Chandra Bahadur Dangi
# the shortest woman in the world is Jyoti Kishanji Amge at 62.8 cm
# lower limit to paternal and maternal height here therefore set arbitrarily at 50 cm
# (this constant was added from the API server `schemas/request_validation_classes.py`)

# These constants are used to determine the range of SDS values that are considered - see discussion in issue #32 in the rcpchgrowth-python repository
# All previous hard-coded values have been replaced with these constants
MINIMUM_HEIGHT_WEIGHT_OFC_ADVISORY_SDS = -4
MAXIMUM_HEIGHT_WEIGHT_OFC_ADVISORY_SDS = 4
MINIMUM_BMI_ADVISORY_SDS = -4
MAXIMUM_BMI_ADVISORY_SDS = 4
MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS = -8
MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS = 8
MINIMUM_BMI_ERROR_SDS = -15
MAXIMUM_BMI_ERROR_SDS = 15
