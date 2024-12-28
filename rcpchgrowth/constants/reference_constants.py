"""
Reference constants
"""

# Trisomy 21 constants
TRISOMY_21 = "trisomy-21"
TRISOMY_21_AAP = "trisomy-21-aap"
TRISOMY_21_AAP_INFANT = "trisomy_21_aap_infant"
TRISOMY_21_AAP_CHILD = "trisomy_21_aap_child"
TRISOMY_21_AAP_REFERENCES = [TRISOMY_21_AAP_INFANT, TRISOMY_21_AAP_CHILD]

# Turner constants
TURNERS = "turners-syndrome"

# UK-WHO constants
UK_WHO = "uk-who"
UK90_PRETERM = "uk90_preterm"
UK_WHO_INFANT = "uk_who_infant"
UK_WHO_CHILD = "uk_who_child"
UK90_CHILD = "uk90_child"
UK_WHO_REFERENCES = [UK90_PRETERM, UK_WHO_INFANT, UK_WHO_CHILD, UK90_CHILD]

# CDC constants
CDC = "cdc" # CDC is the overarching reference
CDC_INFANT = "cdc_infant" # CDC infant is the reference name for children 0-2 years
CDC_CHILD = "cdc_child" # CDC child is the reference name for children 2-20 years
FENTON = "fenton" # Fenton is the reference name for preterm infants
CDC_REFERENCES = [FENTON, CDC_INFANT, CDC_CHILD] # CDC references

# WHO constants
WHO = "who" # WHO is the overarching reference
WHO_2006_INFANT = "who_2006_infant" # WHO 2006 infant is the reference name for children 0-2 years
WHO_2006_CHILD = "who_2006_child" # WHO 2006 child is the reference name for children 2-5 years
WHO_2007_CHILD = "who_2007_child" # WHO 2007 child is the reference name for children 5-19 years
WHO_REFERENCES = [WHO_2006_INFANT, WHO_2006_CHILD, WHO_2007_CHILD] # WHO references

WHO_2006_REFERENCE_LOWER_THRESHOLD = ((42 * 7) - (40 * 7)) / 365.25  # 42 weeks as decimal age  # 2 weeks as decimal age
WHO_2006_REFERENCE_UPPER_THRESHOLD = 5.0  # 5 years as decimal age
WHO_2007_REFERENCE_LOWER_THRESHOLD = 5.0  # 5 years as decimal age
WHO_2007_REFERENCE_UPPER_THRESHOLD = 19.0  # 19 years as decimal age

# 23 weeks is the lowest decimal age available on the UK90 charts
UK90_REFERENCE_LOWER_THRESHOLD = (
    (23 * 7) - (40 * 7)
) / 365.25  # 23 weeks as decimal age

# The WHO references change from measuring infants in the lying position to measuring children in the standing position at 2.0 years.
WHO_CHILD_LOWER_THRESHOLD = 2.0  # 2 years as decimal age
# The UK-WHO standard is complicated because it switches from the WHO references to UK90 references
#  at the age of 4.0 years. This is because it was felt the reference data from breast fed infants
#  from the WHO cohorts were more accurate than the UK90 cohorts for this age group.
#  The Term reference averaged all L, M and S from 37-42 weeks. This is now deprecated and therefore UK90 data is used
# for all measurements across this age range
# Caution is advised when interpreting serial measurements over this time periods - babies are often measured inaccurately and
# up to 10% weight loss is expected in the first 2 weeks of life, and birthweight is often not regained until
# 3 weeks of life

WHO_CHILDREN_UPPER_THRESHOLD = 4.0
UK_WHO_INFANT_LOWER_THRESHOLD = (
    (42 * 7) - (40 * 7)
) / 365.25  # 42 weeks as decimal age
UK90_UPPER_THRESHOLD = 20

WHO_NEWBORN_LOWER_THRESHOLD = 0.0
CDC_LOWER_THRESHOLD = 2.0
CDC_UPPER_THRESHOLD = 20.0

FENTON_LOWER_THRESHOLD = ((22 * 7) - (40 * 7)) / 365.25  # 22 weeks as decimal age
FENTON_UPPER_THRESHOLD = ((50 * 7) - (40 * 7)) / 365.25  # 50 weeks as decimal age


# Generic constants
MALE = "male"
FEMALE = "female"
HEIGHT = "height"
WEIGHT = "weight"
HEAD_CIRCUMFERENCE = "ofc"
BMI = "bmi"
REFERENCES = [UK_WHO, TRISOMY_21, TRISOMY_21_AAP, TURNERS, CDC, WHO]
SEXES = [MALE, FEMALE]
MEASUREMENT_METHODS = [HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI]

# Nomenclature
# Centile formats describe the collection - the two most common used are the cole-nine-centiles format used in UK-WHO
# Each centile in the cole format is 2/3 of a standard deviation apart. They map to 0.04/2/9/25/50/75/91/98/99.6

# and the three-percent-centiles and five-percent-centiles are used by the CDC. They use 5/10/25/50/75/90/95 but also replace the 5th centile with a 3rd/97th centile..
# The eight-five-percent-centiles format is also used by the CDC and adds an extra 85th centile as well as extended centiles for BMI  [5.0, 10.0, 25.0, 50.0, 75.0, 85, 90.0, 98.0, 99.0, 99.9, 99.99 centiles] for use in BMI calculations - this is not used in the UK-WHO references. 
# They were introduced in December 2022

THREE_PERCENT_CENTILES = "three-percent-centiles"
FIVE_PERCENT_CENTILES = "five-percent-centiles"
EIGHTY_FIVE_PERCENT_CENTILES = "eighty-five-percent-centiles"
COLE_TWO_THIRDS_SDS_NINE_CENTILES = "cole-nine-centiles"
CENTILE_FORMATS = [THREE_PERCENT_CENTILES, COLE_TWO_THIRDS_SDS_NINE_CENTILES]

THREE_PERCENT_CENTILE_COLLECTION = [3.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 97.0]
EIGHTY_FIVE_PERCENT_CENTILE_COLLECTION = [5.0, 10.0, 25.0, 50.0, 75.0, 85.0, 90.0, 95, 98.0, 99.0, 99.9, 99.99] # use for CDC Extended BMI centiles 2022
FIVE_PERCENT_CENTILE_COLLECTION = [5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0]
COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION = [
    0.4,
    2.0,
    9.0,
    25.0,
    50.0,
    75.0,
    91.0,
    98.0,
    99.6,
]
