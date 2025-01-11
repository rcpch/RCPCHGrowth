from typing import Union
from .global_functions import centile, sds_for_centile, rounded_sds_for_centile, generate_centile
from .constants.reference_constants import (
    CDC_REFERENCES, 
    CDC,
    COLE_TWO_THIRDS_SDS_NINE_CENTILES, 
    COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION,
    EIGHTY_FIVE_PERCENT_CENTILES,
    EIGHTY_FIVE_PERCENT_CENTILE_COLLECTION,
    EXTENDED_WHO_CENTILES,
    EXTENDED_WHO_CENTILES_COLLECTION,
    FEMALE,
    FENTON,
    FIVE_PERCENT_CENTILES,
    FIVE_PERCENT_CENTILE_COLLECTION,
    HEIGHT, 
    THREE_PERCENT_CENTILES,
    THREE_PERCENT_CENTILE_COLLECTION,
    TRISOMY_21, 
    TRISOMY_21_AAP,
    TRISOMY_21_AAP_REFERENCES,
    TURNERS, 
    UK_WHO, 
    UK_WHO_REFERENCES, 
    UK_WHO_CHILD,
    WHO,
    WHO_REFERENCES
)

"""
Public chart functions
"""


def create_chart(
    reference: str, 
    centile_format: Union[str, list] = COLE_TWO_THIRDS_SDS_NINE_CENTILES, 
    measurement_method: str = HEIGHT, 
    sex: str = FEMALE, 
    is_sds=False):
    """
    Global method - return chart for measurement_method, sex and reference
    """
    
    if reference == UK_WHO:
        return create_uk_who_chart(
            measurement_method=measurement_method, 
            sex=sex, 
            centile_format=centile_format, 
            is_sds=is_sds)
    elif reference == TURNERS:
        return create_turner_chart(
            centile_format=centile_format, 
            is_sds=is_sds)
    elif reference == TRISOMY_21:
        return create_trisomy_21_chart(
            measurement_method=measurement_method, 
            sex=sex, 
            centile_format=centile_format, 
            is_sds=is_sds)
    elif reference == CDC:
        return create_cdc_chart(
            measurement_method=measurement_method, 
            sex=sex, 
            centile_format=centile_format, 
            is_sds=is_sds)
    elif reference == TRISOMY_21_AAP:
        return create_trisomy_21_aap_chart(
            measurement_method=measurement_method,
            sex=sex,
            centile_format=centile_format,
            is_sds=is_sds)
    elif reference == WHO:
        return create_who_chart(
            measurement_method=measurement_method,
            sex=sex,
            centile_format=centile_format,
            is_sds=is_sds)
    else:
        print("No reference data returned. Is there a spelling mistake in your reference?")

    """
    Return object structure

    [
        heights: [
            [{
                x: 9.415, `this is the corrected age of the child at date of measurement in decimal years
                y: 120 `this is the observation value - the units will be added in the client
                "centile_band": 'Your child's height is between the 75th and 91st centiles' `a text advice string for labelling - corrected,
                "centile_value": 86 `centile number value - reported but not used: the project board do not like exact centile numbers - corrected,
                "age_type": "corrected_age", `this is a flag to differentiate the two ages for the same observation_value
                "calendar_age": "9 years and 4 months" `this is the calendar age for labelling
                "corrected_gestational_weeks": 23 `the corrected gestational age if relevant for labelling
                "corrected_gestational_days": 1 `the corrected gestational age if relevant for labelling
            }
            {
                x: 9.415, `this is the chronological age of the child at date of measurement in decimal years
                y: 120 `this is the observation value - the units will be added in the client
                "centile_band": 'Your child's height is between the 75th and 91st centiles' `a text advice string for labelling - based on chronological age,
                "centile_value": 86 `centile number value - reported but not used: the project board do not like exact centile numbers - based on chronological age, 
                "age_type": "corrected_age", `this is a flag to differentiate the two ages for the same observation_value
                "calendar_age": "9 years and 4 months" `this is the calendar age for labelling
                "corrected_gestational_weeks": 23 `the corrected gestational age if relevant for labelling
                "corrected_gestational_days": 1 `the corrected gestational age if relevant for labelling
            }
            ]
        ],
        height_sds: [
                x: 9.415, `this is the age of the child at date of measurement in decimal years
                y: 1.3 `this is the SDS value for SDS charts
                "age_type": "corrected_age", `this is a flag to differentiate the two ages for the same observation_value
                "calendar_age": "9 years and 4 months" `this is the calendar age for labelling
                "corrected_gestational_weeks": 23 `the corrected gestational age if relevant for labelling
                "corrected_gestational_days": 1 `the corrected gestational age if relevant for labelling
        ],
        .... and so on for the other measurement_methods
        
    ]

    """


"""
private functions
"""

def build_centile_object(reference, measurement_method: str, sex: str, reference_name: str, z: float, centile: float):
    sex_list: dict = {}  # all the data for a given sex are stored here
    measurements: dict = {}  # all the data for a given measurement_method are stored here
    centiles = []  # all generated centiles for a selected centile collection are stored here

    try:
        # Generate a centile. there will be nine of these if Cole method selected.
        # Some data does not exist at all ages, so any error reflects missing data.
        # If this happens, an empty list is returned.
        centile_data = generate_centile(
            z=z,
            centile=centile,
            measurement_method=measurement_method,
            sex=sex,
            # lms_array_for_measurement=lms_array_for_measurement,
            reference_name=reference_name,
            reference=reference
        )
    except:
        centile_data=None
    # Store this centile for a given measurement
    
    centiles.append({"sds": round(z * 100) / 100,
                "centile": centile, "data": centile_data})

    # this is the end of the centile_collection for loop
    # All the centiles for this measurement, sex and reference are added to the measurements list
    measurements.update({measurement_method: centiles})

    # this is the end of the measurement_methods loop
    # All data for all measurement_methods for this sex are added to the sex_list list

    sex_list.update({sex: measurements})

    return sex_list


def create_uk_who_chart(
        measurement_method: str, 
        sex: str, 
        centile_format: Union[str, list] = COLE_TWO_THIRDS_SDS_NINE_CENTILES, 
        is_sds = False
    ):

    # user selects which centile collection they want, for sex and measurement_method
    # If the Cole method is selected, conversion between centile and SDS
    # is different as SDS is rounded to the nearest 2/3
    # Cole method selection is stored in the cole_method flag.
    # If no parameter is passed, default is the Cole method
    # Alternatively it is possible to pass a custom list of values - if the is_sds flag is False (default) these are centiles

    centile_sds_collection = []
    cole_method = True if centile_format == COLE_TWO_THIRDS_SDS_NINE_CENTILES else False

    if (type(centile_format) is list):
        # a custom list of centiles was provided
        centile_sds_collection = centile_format
    else:
        # a standard centile collection was selected
        centile_sds_collection = select_centile_format(centile_format)
        is_sds=False

    ##
    # iterate through the 4 references that make up UK-WHO
    # There will be a list for each one
    ##

    # all data for a given reference are stored here: this is returned to the user
    reference_data = []

    for reference_index, reference_name in enumerate(UK_WHO_REFERENCES):
        sex_list: dict = {}  # all the data for a given sex are stored here
        # For each reference we have 2 sexes
        # For each sex we have 4 measurement_methods

        measurements: dict = {}  # all the data for a given measurement_method are stored here

        # for every measurement method we have as many centiles
        # as have been requested

        centiles = []  # all generated centiles for a selected centile collection are stored here

        for centile_index, centile_sds in enumerate(centile_sds_collection):
            # we must create a z for each requested centile
            # if the Cole 9 centiles were selected, these are rounded,
            # so conversion to SDS is different
            # Otherwise standard conversation of centile to z is used

            z=0.0 #initialise
            centile_value=0.0 #initialise

            if (is_sds):
                z=centile_sds # an sds was supplied
                centile_value=centile(centile_sds) # convert the z to a centile and store
            else:
                if cole_method:
                    z = rounded_sds_for_centile(centile_sds)
                else:
                    z = sds_for_centile(centile_sds) # a centile was provided, so convert to z
                centile_value=centile_sds # store the original centile value 
            centile_data = []

            try:
                # Generate a centile. there will be nine of these if Cole method selected.
                # Some data does not exist at all ages, so any error reflects missing data.
                # If this happens, an empty list is returned.
                centile_data = generate_centile(
                    z=z,
                    centile=centile_value,
                    measurement_method=measurement_method,
                    sex=sex,
                    reference_name=reference_name,
                    reference=UK_WHO,
                    is_sds=is_sds
                )
            except:
                print(f"Not possible to generate centile data for UK-WHO {measurement_method} in {sex}s.")
                centile_data=None
            # Store this centile for a given measurement
            
            centiles.append({"sds": round(z * 100) / 100,
                        "centile": centile_value, "data": centile_data})

        # this is the end of the centile_collection for loop
        # All the centiles for this measurement, sex and reference are added to the measurements list
        measurements.update({measurement_method: centiles})

        # this is the end of the measurement_methods loop
        # All data for all measurement_methods for this sex are added to the sex_list list

        sex_list.update({sex: measurements})

        # all data can now be tagged by reference_name and added to reference_data
        reference_data.append({reference_name: sex_list})

    # returns a list of 4 references, each containing 2 lists for each sex,
    # each sex in turn containing 4 datasets for each measurement_method
    return reference_data

    """
    structure:
    UK_WHO generates 4 json objects, each structure as below
    uk90_preterm: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...]
        },
        female {...}
    }
    uk_who_infant: {...}
    uk_who_child:{...}
    uk90_child: {...}
    """


def create_turner_chart(centile_format: Union[str, list], is_sds=False):
   # user selects which centile collection they want
    # If the Cole method is selected, conversion between centile and SDS
    # is different as SDS is rounded to the nearest 2/3
    # Cole method selection is stored in the cole_method flag.
    # If no parameter is passed, default is the Cole method
    # NOTE: Turner's syndrome only affects girls and reference data only exists for height. This function will only return height data and
    # relies on error handling elsewhere to catch any other requests for data.

    centile_sds_collection = []
    cole_method = False

    if (type(centile_format) is list):
        # a custom list of centiles was provided
        centile_sds_collection = centile_format
    else:
        # a standard centile collection was selected
        centile_sds_collection = select_centile_format(centile_format)
        is_sds=False

    # all data for a the reference are stored here: this is returned to the user
    reference_data = {}

    # for sex_index, sex in enumerate(SEXES):
    # For each sex we have 4 measurement_methods
    # Turner is female only, but we will generate empty arrays for male
    # data to keep all objects the same

    sex_list: dict = {}
    sex = FEMALE

    measurements: dict = {}  # all the data for a given measurement_method are stored here

    # for measurement_index, measurement_method in enumerate(MEASUREMENT_METHODS):
    # for every measurement method we have as many centiles
    # as have been requested

    centiles = []  # all generated centiles for a selected centile collection are stored here

    for centile_index, centile_sds in enumerate(centile_sds_collection):
        # we must create a z for each requested centile
        # if the Cole 9 centiles were selected, these are rounded,
        # so conversion to SDS is different
        # Otherwise standard conversation of centile to z is used
        if cole_method:
            z = rounded_sds_for_centile(centile_sds)
            centile_value=centile_sds
        else:
            if is_sds:
                z = centile_sds
                centile_value = centile(centile_sds)
            else:
                z = sds_for_centile(centile_sds)
                centile_value=centile_sds
        # Collect the LMS values from the correct reference
        # lms_array_for_measurement = select_reference_data_for_turner(
        #     measurement_method=HEIGHT, sex=sex)
        # Generate a centile. there will be nine of these if Cole method selected.
        # Some data does not exist at all ages, so any error reflects missing data.
        # If this happens, an empty list is returned.
        try:
            centile_data = generate_centile(
                z=z, 
                centile=centile_value, 
                measurement_method=HEIGHT,
                sex=sex, 
                reference_name=TURNERS, reference=TURNERS,
                is_sds=is_sds)

            # Store this centile for a given measurement
            centiles.append({"sds": round(z * 100) / 100,
                            "centile": centile_value, "data": centile_data})
        except Exception as e:
            print(f"create_turner chart generate centile error: {e}")

    # this is the end of the centile_collection for loop
    # All the centiles for this measurement, sex and reference are added to the measurements list
    measurements.update({HEIGHT: centiles})

    # this is the end of the measurement_methods loop
    # All data for all measurement_methods for this sex are added to the sex_list list

    sex_list.update({sex: measurements})

    # all data can now be tagged by reference_name and added to reference_data
    reference_data = [{TURNERS: sex_list}]
    return reference_data

    """
    Return object structure
    [turners-syndrome: [{
        female: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...]
        },
        female {...}
    }]
    """

def create_trisomy_21_chart(measurement_method: str, sex: str, centile_format: Union[str, list], is_sds=False):
   # user selects which centile collection they want
    # If the Cole method is selected, conversion between centile and SDS
    # is different as SDS is rounded to the nearest 2/3
    # Cole method selection is stored in the cole_method flag.
    # If no parameter is passed, default is the Cole method

    centile_sds_collection = []
    cole_method = False

    if (type(centile_format) is list):
        # a custom list of centiles was provided
        centile_sds_collection = centile_format
    else:
        # a standard centile collection was selected
        centile_sds_collection = select_centile_format(centile_format)
        is_sds=False

    # all data for a the reference are stored here: this is returned to the user
    reference_data = {}
    sex_list: dict = {}

    measurements: dict = {}  # all the data for a given measurement_method are stored here

    centiles = []  # all generated centiles for a selected centile collection are stored here

    for centile_index, centile_sds in enumerate(centile_sds_collection):
        # we must create a z for each requested centile
        # if the Cole 9 centiles were selected, these are rounded,
        # so conversion to SDS is different
        # Otherwise standard conversation of centile to z is used
        if cole_method:
            z = rounded_sds_for_centile(centile_sds)
            centile_value=centile_sds
        else:
            if is_sds:
                z = centile_sds
                centile_value=centile(z)
            else:
                z = sds_for_centile(centile_sds)
                centile_value=centile_sds

        # Generate a centile. there will be nine of these if Cole method selected.
        # Some data does not exist at all ages, so any error reflects missing data.
        # If this happens, an empty list is returned.
        try:    
            centile_data = generate_centile(
                z=z, 
                centile=centile_value, 
                measurement_method=measurement_method,
                sex=sex, 
                reference=TRISOMY_21,
                reference_name=TRISOMY_21,
                is_sds=is_sds)

            # Store this centile for a given measurement
            centiles.append({"sds": round(z, 2),
                            "centile": centile_value, "data": centile_data})
        except Exception as e:
            print(f"generate_centile error: {e}")

    # this is the end of the centile_collection for loop
    # All the centiles for this measurement, sex and reference are added to the measurements list
    measurements.update({measurement_method: centiles})

    # this is the end of the measurement_methods loop
    # All data for all measurement_methods for this sex are added to the sex_list list

    sex_list.update({sex: measurements})

    # all data can now be tagged by reference_name and added to reference_data
    reference_data = [{TRISOMY_21: sex_list}]
    return reference_data

    """
    # return object structure
    [trisomy_21: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...]
        },
        female {...}
    }]
    """

def create_cdc_chart(
        measurement_method: str, 
        sex: str, 
        centile_format: Union[str, list] = COLE_TWO_THIRDS_SDS_NINE_CENTILES, 
        is_sds = False
    ):

    # user selects which centile collection they want, for sex and measurement_method
    # If the Cole method is selected, conversion between centile and SDS
    # is different as SDS is rounded to the nearest 2/3
    # Cole method selection is stored in the cole_method flag.
    # If no parameter is passed, default is the Cole method
    # Alternatively it is possible to pass a custom list of values - if the is_sds flag is False (default) these are centiles
    
    centile_sds_collection = []
    cole_method = False

    if (type(centile_format) is list):
        # a custom list of centiles was provided
        centile_sds_collection = centile_format
    else:
        # a standard centile collection was selected
        centile_sds_collection = select_centile_format(centile_format)
        is_sds=False

    ##
    # iterate through the 3 references that make up CDC (Fenton, WHO, CDC  itself)
    # There will be a list for each one
    ##

    # all data for a given reference are stored here: this is returned to the user
    reference_data = []

    for reference_index, reference_name in enumerate(CDC_REFERENCES):
        sex_list: dict = {}  # all the data for a given sex are stored here
        # For each reference we have 2 sexes
        
        measurements: dict = {}  # all the data for a given measurement_method are stored here

        centiles = []  # all generated centiles for a selected centile collection are stored here

        for centile_index, centile_sds in enumerate(centile_sds_collection):
            # we must create a z for each requested centile
            # if the Cole 9 centiles were selected, these are rounded,
            # so conversion to SDS is different
            # Otherwise standard conversation of centile to z is used

            z=0.0 #initialise
            centile_value=0.0 #initialise

            if cole_method:
                z = rounded_sds_for_centile(centile_sds) # a centile was provided, so convert to z
                centile_value=centile_sds # store the original centile value 
            else:
                if (is_sds):
                    z=centile_sds # an sds was supplied
                    centile_value=centile(centile_sds) # convert the z to a centile and store
                else:
                    z = sds_for_centile(centile_sds) # a centile was provided, so convert to z
                    centile_value=centile_sds # store the original centile value 
            centile_data = []

            try:
                # Generate a centile. there will be nine of these if Cole method selected.
                # Some data does not exist at all ages, so any error reflects missing data.
                # If this happens, an empty list is returned.
                centile_data = generate_centile(
                    z=z,
                    centile=centile_value,
                    measurement_method=measurement_method,
                    sex=sex,
                    reference=CDC,
                    reference_name=reference_name,
                    is_sds=is_sds
                )
            except LookupError as e:
                print(f"Not possible to generate centile data for CDC {measurement_method} in {sex}s. {e}")
                centile_data=None
            # Store this centile for a given measurement
            
            centiles.append({"sds": round(z * 100) / 100,
                        "centile": centile_value, "data": centile_data})

        # this is the end of the centile_collection for loop
        # All the centiles for this measurement, sex and reference are added to the measurements list
        measurements.update({measurement_method: centiles})

        # this is the end of the measurement_methods loop
        # All data for all measurement_methods for this sex are added to the sex_list list

        sex_list.update({sex: measurements})

        # all data can now be tagged by reference_name and added to reference_data
        reference_data.append({reference_name: sex_list})

    # returns a list of 4 references, each containing 2 lists for each sex,
    # each sex in turn containing 4 datasets for each measurement_method
    return reference_data

    """
    # return object structure
    [ cdc_infant: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...],
            bmi: [...],
            ofc: [...]
        },
        female {...}
    },
    cdc_child: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...],
            bmi: [...],
            ofc: [...]
            },
        female {...}
        }
    ]
    """

def create_trisomy_21_aap_chart(measurement_method: str, sex: str, centile_format: Union[str, list], is_sds=False):
    # user selects which centile collection they want, for sex and measurement_method
    # If the Cole method is selected, conversion between centile and SDS
    # is different as SDS is rounded to the nearest 2/3
    # Cole method selection is stored in the cole_method flag.
    # If no parameter is passed, default is the Cole method
    # Alternatively it is possible to pass a custom list of values - if the is_sds flag is False (default) these are centiles
    
    centile_sds_collection = []
    cole_method = False

    if (type(centile_format) is list):
        # a custom list of centiles was provided
        centile_sds_collection = centile_format
    else:
        # a standard centile collection was selected
        centile_sds_collection = select_centile_format(centile_format)
        is_sds=False

    ##
    # iterate through the 4 references that make up UK-WHO
    # There will be a list for each one
    ##

    # all data for a given reference are stored here: this is returned to the user
    reference_data = []

    for reference_index, reference_name in enumerate(TRISOMY_21_AAP_REFERENCES):
        sex_list: dict = {}  # all the data for a given sex are stored here
        # For each reference we have 2 sexes
        # For each sex we have 4 measurement_methods

        measurements: dict = {}  # all the data for a given measurement_method are stored here

        centiles = []  # all generated centiles for a selected centile collection are stored here

        for centile_index, centile_sds in enumerate(centile_sds_collection):
            # we must create a z for each requested centile
            # if the Cole 9 centiles were selected, these are rounded,
            # so conversion to SDS is different
            # Otherwise standard conversation of centile to z is used

            z=0.0 #initialise
            centile_value=0.0 #initialise

            if cole_method:
                z = rounded_sds_for_centile(centile_sds) # a centile was provided, so convert to z
                centile_value=centile_sds # store the original centile value 
            else:
                if (is_sds):
                    z=centile_sds # an sds was supplied
                    centile_value=centile(centile_sds) # convert the z to a centile and store
                else:
                    z = sds_for_centile(centile_sds) # a centile was provided, so convert to z
                    centile_value=centile_sds # store the original centile value 
            centile_data = []

            try:
            # Generate a centile. there will be nine of these if Cole method selected.
            # Some data does not exist at all ages, so any error reflects missing data.
            # If this happens, an empty list is returned.
                centile_data = generate_centile(
                    z=z,
                    centile=centile_value,
                    measurement_method=measurement_method,
                    sex=sex,
                    reference=TRISOMY_21_AAP,
                    reference_name=reference_name,
                    is_sds=is_sds,

                )
            except Exception as e:
                print(f"Not possible to generate centile data for Trisomy 21 (AAP) for {measurement_method} in {sex}s. {e}")
                centile_data=None
            # Store this centile for a given measurement
            
            centiles.append({"sds": round(z * 100) / 100,
                        "centile": centile_value, "data": centile_data})

        # this is the end of the centile_collection for loop
        # All the centiles for this measurement, sex and reference are added to the measurements list
        measurements.update({measurement_method: centiles})

        # this is the end of the measurement_methods loop
        # All data for all measurement_methods for this sex are added to the sex_list list

        sex_list.update({sex: measurements})

        # all data can now be tagged by reference_name and added to reference_data
        reference_data.append({reference_name: sex_list})

    # returns a list of 2 references, each containing 2 lists for each sex,
    # each sex in turn containing 4 datasets for each measurement_method
    return reference_data

    """
    # return object structure
    [ trisomy_21_aap_infant: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...],
            bmi: [...],
            ofc: [...]
        },
        female {...}
    },
    trisomy_aap_child: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...],
            bmi: [...],
            ofc: [...]
            },
        female {...}
        }
    ]
    """

def create_who_chart(
        measurement_method: str, 
        sex: str, 
        centile_format: Union[str, list] = COLE_TWO_THIRDS_SDS_NINE_CENTILES, 
        is_sds = False
    ):

    # user selects which centile collection they want, for sex and measurement_method
    # If the Cole method is selected, conversion between centile and SDS
    # is different as SDS is rounded to the nearest 2/3
    # Cole method selection is stored in the cole_method flag.
    # If no parameter is passed, default is the Cole method
    # Alternatively it is possible to pass a custom list of values - if the is_sds flag is False (default) these are centiles
    
    centile_sds_collection = []
    cole_method = False

    if (type(centile_format) is list):
        # a custom list of centiles was provided
        centile_sds_collection = centile_format
    else:
        # a standard centile collection was selected
        centile_sds_collection = select_centile_format(centile_format)
        is_sds=False

    ##
    # iterate through the 3 references that make up CDC (Fenton, WHO, CDC  itself)
    # There will be a list for each one
    ##

    # all data for a given reference are stored here: this is returned to the user
    reference_data = []

    for reference_index, reference_name in enumerate(WHO_REFERENCES):
        sex_list: dict = {}  # all the data for a given sex are stored here
        # For each reference we have 2 sexes
        # For each sex we have 4 measurement_methods

        measurements: dict = {}  # all the data for a given measurement_method are stored here

        # for every measurement method we have as many centiles
        # as have been requested

        centiles = []  # all generated centiles for a selected centile collection are stored here

        for centile_index, centile_sds in enumerate(centile_sds_collection):
            # we must create a z for each requested centile
            # if the Cole 9 centiles were selected, these are rounded,
            # so conversion to SDS is different
            # Otherwise standard conversation of centile to z is used

            z=0.0 #initialise
            centile_value=0.0 #initialise

            if cole_method:
                z = rounded_sds_for_centile(centile_sds) # a centile was provided, so convert to z
                centile_value=centile_sds # store the original centile value 
            else:
                if (is_sds):
                    z=centile_sds # an sds was supplied
                    centile_value=centile(centile_sds) # convert the z to a centile and store
                else:
                    z = sds_for_centile(centile_sds) # a centile was provided, so convert to z
                    centile_value=centile_sds # store the original centile value 
            centile_data = []

            try:
                # Generate a centile. there will be nine of these if Cole method selected.
                # Some data does not exist at all ages, so any error reflects missing data.
                # If this happens, an empty list is returned.
                centile_data = generate_centile(
                    z=z,
                    centile=centile_value,
                    measurement_method=measurement_method,
                    sex=sex,
                    reference=WHO,
                    is_sds=is_sds,
                    reference_name=reference_name
                )
            except LookupError as e:
                print(f"Not possible to generate centile data for WHO {measurement_method} in {sex}s. {e}")
                centile_data=None
            # Store this centile for a given measurement
            
            centiles.append({"sds": round(z * 100) / 100,
                        "centile": centile_value, "data": centile_data})

        # this is the end of the centile_collection for loop
        # All the centiles for this measurement, sex and reference are added to the measurements list
        measurements.update({measurement_method: centiles})

        # this is the end of the measurement_methods loop
        # All data for all measurement_methods for this sex are added to the sex_list list

        sex_list.update({sex: measurements})

        # all data can now be tagged by reference_name and added to reference_data
        reference_data.append({reference_name: sex_list})

    # returns a list of 4 references, each containing 2 lists for each sex,
    # each sex in turn containing 4 datasets for each measurement_method
    return reference_data

    """
    # return object structure
    [ cdc_infant: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...],
            bmi: [...],
            ofc: [...]
        },
        female {...}
    },
    cdc_child: {
        male: {
            height: [
                {
                    sds: -2.667,
                    centile: 0.4
                    data: [{l: , x: , y: }, ....]
                }
            ],
            weight: [...],
            bmi: [...],
            ofc: [...]
            },
        female {...}
        }
    ]
    """
        


def select_centile_format(centile_format: str):
    """
    Select the centile format
    Helper function to select the correct centile collection
    the pre-defined collections are in the constants file and have string names: 'cole-nine-centiles', 'three-percent-centiles', 'five-percent-centiles', 'eighty-five-percent_centiles'
    """
    if centile_format == COLE_TWO_THIRDS_SDS_NINE_CENTILES:
        return COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION
    elif centile_format == THREE_PERCENT_CENTILES:
        return THREE_PERCENT_CENTILE_COLLECTION
    elif centile_format == FIVE_PERCENT_CENTILES:
        return FIVE_PERCENT_CENTILE_COLLECTION
    elif centile_format == EIGHTY_FIVE_PERCENT_CENTILES:
        return EIGHTY_FIVE_PERCENT_CENTILE_COLLECTION
    elif centile_format == EXTENDED_WHO_CENTILES:
        return EXTENDED_WHO_CENTILES_COLLECTION
    else:
        return COLE_TWO_THIRDS_SDS_NINE_CENTILE_COLLECTION