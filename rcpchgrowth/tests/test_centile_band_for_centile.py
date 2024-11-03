from scipy.stats import norm
from ..centile_bands import centile_band_for_centile
from ..global_functions import sds_for_centile
from ..constants.reference_constants import HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI
from ..constants.reference_constants import THREE_PERCENT_CENTILES, FIVE_PERCENT_CENTILES, EIGHTY_FIVE_PERCENT_CENTILES, COLE_TWO_THIRDS_SDS_NINE_CENTILES

measurements = [HEIGHT, WEIGHT, HEAD_CIRCUMFERENCE, BMI]
measurement_texts = ["height", "weight", "head circumference", "body mass index"]

on_cole_centiles = [
            {
                "centile": 0.4, 
                "text": "0.4th"
            },
            {
                "centile": 2.0, 
                "text": "2nd"
            },
            {
                "centile": 9.0, 
                "text": "9th"
            },
            {
                "centile": 25.0, 
                "text": "25th"
            },
            {
                "centile": 50.0, 
                "text": "50th"
            },
            {
                "centile": 75.0, 
                "text": "75th"
            },
            {
                "centile": 91.0, 
                "text": "91st"
            },
            {
                "centile": 98.0, 
                "text": "98th"
            },
            {
                "centile": 99.6, 
                "text": "99.6th"
            }
        ]
between_cole_centiles = [
            {
                "centile": 1.0, 
                "text": "between the 0.4th and 2nd"
            },
            {
                "centile": 5.0, 
                "text": "between the 2nd and 9th"
            },
            {
                "centile": 17.0, 
                "text": "between the 9th and 25th"
            },
            {
                "centile": 37.0, 
                "text": "between the 25th and 50th"
            },
            {
                "centile": 62.0, 
                "text": "between the 50th and 75th"
            },
            {
                "centile": 83.0, 
                "text": "between the 75th and 91st"
            },
            {
                "centile": 94.5, 
                "text": "between the 91st and 98th"
            },
            {
                "centile": 99.3, 
                "text": "between the 98th and 99.6th"
            }
        ]

beyond_cole_thresholds = [
            {
                "centile": 99.8, 
                "text": "above the normal range"
            },
            {
                "centile": 0.1, 
                "text": "below the normal range"
            }
        ]

# on three-percent-centiles (3rd, 5th, 10th, 25th, 50th, 75th, 90th, 95th, 97th)
on_three_percent_centiles = [
            {
                "centile": 3.0, 
                "text": "3rd"
            },
            {
                "centile": 5.0, 
                "text": "5th"
            },
            {
                "centile": 10.0, 
                "text": "10th"
            },
            {
                "centile": 25.0, 
                "text": "25th"
            },
            {
                "centile": 50.0, 
                "text": "50th"
            },
            {
                "centile": 75.0, 
                "text": "75th"
            },
            {
                "centile": 90.0, 
                "text": "90th"
            },
            {
                "centile": 95.0, 
                "text": "95th"
            },
            {
                "centile": 97.0, 
                "text": "97th"
            }
        ]

# between three-percent-centiles (7.0th, 17.5th, 37.5th, 62.5th, 82.5th, 93rd)
between_three_percent_centiles = [
            {
                "centile": 7.0, 
                "text": "between the 5th and 10th"
            },
            {
                "centile": 17.5, 
                "text": "between the 10th and 25th"
            },
            {
                "centile": 37.5, 
                "text": "between the 25th and 50th"
            },
            {
                "centile": 62.5, 
                "text": "between the 50th and 75th"
            },
            {
                "centile": 82.5, 
                "text": "between the 75th and 90th"
            },
            {
                "centile": 93, 
                "text": "between the 90th and 95th"
            },
        ]

# beyond three-percent-centiles (1st, 97.5th, 99.9th)
beyond_three_percent_thresholds = [
            {
                "centile": 1.0, 
                "text": "below the normal range"
            },
            {
                "centile": 98, 
                "text": "above the normal range"
            },
            {
                "centile": 99.9,
                "text": "above the normal range"
            }
        ]

# on five-percent-centiles (5th, 10th, 25th, 50th, 75th, 90th, 95th)
on_five_percent_centiles = [
            {
                "centile": 5.0,
                "text": "5th",
            },
            {
                "centile": 10.0,
                "text": "10th",
            },
            {
                "centile": 25.0,
                "text": "25th",
            },
            {
                "centile": 50.0,
                "text": "50th",
            },
            {
                "centile": 75.0,
                "text": "75th",
            },
            {
                "centile": 90.0,
                "text": "90th",
            },
            {
                "centile": 95.0,
                "text": "95th",
            }
        ]

# between five-percent-centiles (8th, 17.5th, 37.5th, 62.5th, 82.5th, 92.5th)
between_five_percent_centiles = [
            {
                "centile": 7,
                "text": "between the 5th and 10th",
            },
            {
                "centile": 17.5,
                "text": "between the 10th and 25th",
            },
            {
                "centile": 37.5,
                "text": "between the 25th and 50th",
            },
            {
                "centile": 62.5,
                "text": "between the 50th and 75th",
            },
            {
                "centile": 82.5,
                "text": "between the 75th and 90th",
            },
            {
                "centile": 93,
                "text": "between the 90th and 95th",
            }
        ]

# beyond five-percent-centiles (1st, 97.5th, 99.9th)
beyond_five_percent_thresholds = [
            {
                "centile": 1.0,
                "text": "below the normal range",
            },
            {
                "centile": 97.5,
                "text": "above the normal range",
            },
            {
                "centile": 99.9,
                "text": "above the normal range",
            }
        ]

# on eighty-five-percent-centiles (15th, 50th, 85th)
on_eighty_five_percent_centiles_bmi = [
            {
                "centile": 85.0,
                "text": "85th",
            },
            {
                "centile": 98.0,
                "text": "98th",
            },
            {
                "centile": 99.9,
                "text": "99.9th",
            },
            {
                "centile": 99.99,
                "text": "99.99th"
            }
        ]

# between eighty-five-percent-centiles (32.5th, 67.5th)
between_eighty_five_percent_centiles = [
            {
                "centile": 15.0,
                "text": "between the 10th and 25th",
            },
            {
                "centile": 32.5,
                "text": "between the 25th and 50th",
            },
            {
                "centile": 67.5,
                "text": "between the 50th and 75th",
            },
            {
                "centile": 80,
                "text": "between the 75th and 85th",
            }
        ]

# beyond eighty-five-percent-centiles (7.5th, 92.5th)
beyond_eighty_five_percent_thresholds = [
            {
                "centile": 7.5,
                "text": "below the normal range",
            },
            {
                "centile": 92.5,
                "text": "above the normal range",
            }
]

def test_centile_band_for_centile_cole():

    # on cole centiles (2.0, 9.0, 25.0, 50.0, 75.0, 91.0, 98.0, 99.6)
    for measurement in measurements:
        for centile in on_cole_centiles:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=COLE_TWO_THIRDS_SDS_NINE_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is on or near the {centile['text']} centile."
        
        
    #  between cole centiles (0.4th, 2nd, 9th, 25th, 50th, 75th, 91st, 98th, 99.6th)
    for measurement in measurements:
        for centile in between_cole_centiles:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=COLE_TWO_THIRDS_SDS_NINE_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is {centile['text']} centiles."

    #  above 99.6th centile or below 0.4th centile
    for measurement in measurements:
        for centile in beyond_cole_thresholds:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=COLE_TWO_THIRDS_SDS_NINE_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is {centile['text']}."

def test_centile_band_for_centile_three_percent():
    # on three-percent-centiles (3rd, 5th, 10th, 25th, 50th, 75th, 90th, 95th, 97th)
    for measurement in measurements:
        for centile in on_three_percent_centiles:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=THREE_PERCENT_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is on or near the {centile['text']} centile."
        
    # between three-percent-centiles (4th, 7.5th, 17.5th, 37.5th, 62.5th, 82.5th, 92.5th, 96.5th)
    for measurement in measurements:
        for centile in between_three_percent_centiles:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=THREE_PERCENT_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is {centile['text']} centiles."

    # beyond three-percent-centiles (1st, 97.5th, 99.9th)
    for measurement in measurements:
        for centile in beyond_three_percent_thresholds:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=THREE_PERCENT_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is {centile['text']}."

def test_centile_band_for_centile_five_percent():
    # on five-percent-centiles (5th, 10th, 25th, 50th, 75th, 90th, 95th)
    for measurement in measurements:
        for centile in on_five_percent_centiles:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=FIVE_PERCENT_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is on or near the {centile['text']} centile."
        
    # between five-percent-centiles (7.5th, 17.5th, 37.5th, 62.5th, 82.5th, 92.5th)
    for measurement in measurements:
        for centile in between_five_percent_centiles:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=FIVE_PERCENT_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is {centile['text']} centiles."

    # beyond five-percent-centiles (1st, 97.5th, 99.9th)
    for measurement in measurements:
        for centile in beyond_five_percent_thresholds:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=FIVE_PERCENT_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is {centile['text']}."

def test_centile_band_for_centile_eighty_five_percent():
        
    # between eighty-five-percent-centiles (32.5th, 67.5th)
    for measurement in measurements:
        for centile in between_eighty_five_percent_centiles:
            sds = sds_for_centile(centile['centile'])
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=EIGHTY_FIVE_PERCENT_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is {centile['text']} centiles."

    #on eighty-five-percent-centiles (85th, 98th, 99.9th, 99.99th)
    for centile in on_eighty_five_percent_centiles_bmi:
        sds = sds_for_centile(centile['centile'])
        assert centile_band_for_centile(sds=sds, measurement_method="bmi", centile_format=EIGHTY_FIVE_PERCENT_CENTILES) == f"This body mass index measurement is on or near the {centile['text']} centile."

def test_advisory_thresholds():
    for measurement in measurements:
        for centile in beyond_eighty_five_percent_thresholds:
            sds = 5 # above 4 and less than 8
            if measurement == BMI:
                sds = 10
            assert centile_band_for_centile(sds=sds, measurement_method=measurement, centile_format=COLE_TWO_THIRDS_SDS_NINE_CENTILES) == f"This {measurement_texts[measurements.index(measurement)]} measurement is well outside the normal range. Please check its accuracy."