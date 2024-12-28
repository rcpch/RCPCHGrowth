# standard imports
from datetime import date
from typing import Literal

# rcpch imports
from .centile_bands import centile_band_for_centile
from .constants import *
from .date_calculations import (chronological_decimal_age, corrected_decimal_age,
                                chronological_calendar_age, estimated_date_delivery, corrected_gestational_age)
from .global_functions import sds_for_measurement, centile, percentage_median_bmi
from .age_advice_strings import comment_prematurity_correction
class Measurement:

    def __init__(
        self,
        birth_date: date,
        measurement_method: str,
        observation_date: date,
        observation_value: float,
        reference: str,
        sex: str,
        gestation_days: int = 0,
        gestation_weeks: int = 0,
        events_text: list = None,
        bone_age: float = None,
        bone_age_type: str = None,
        bone_age_sds: float = None,
        bone_age_centile: float = None,
        bone_age_text: str = None
    ):
        """
        The Measurement Class is the gatekeeper to all the functions in the RCPCHGrowth package, although the public
        functions can be accessed independently. The bulk of the error handling happens here so be aware that calling
        other functions independently may yield unexpected results.
        It is initialised with the following Required parameters:
        `birth_date`: (Python datetime object) The date of birth of the subject.
        `measurement_type`: (string) 'height', 'weight', 'bmi' or 'ofc' only are accepted.
        `observation_date`: (Python datetime object) The date that the observation was made.
        `observation_value`: (float) The value of the height, weight, BMI or ofc observation.
        `sex`: (string) The sex of the child, which can either be 'male' or 'female'.
        Additionally there are the following optional parameters:
        `gestation_weeks`: (integer) gestation at birth in weeks.
        `gestation_days`: (integer) supplemental days in addition to gestation_weeks at birth.
        `reference`: ENUM refering to which reference dataset to use: ['uk-who', 'turners-syndrome', 'trisomy-21', 'trisomy-21-aap', 'cdc', 'who'].
        `height_prediction`: decimal years
        `height_prediction_sds`: SDS for height prediction against reference
        `height_prediction_centile`: centile for height prediction against reference
        `height_prediction_reference`: enum ['bayley-pinneau', 'roche-wainer-thissen']
        `event_text`: list. this is a list of strings which are comments to tag a given measurement/plot with contextual information 
        `bone_age`: an estimated skeletal age calculated from xrays reported in decimal years
        `bone_age_sds`: an SDS for the bone age, based on references
        `bone_age_centile`: a centile for the bone age, based on references
        `bone_age_reference`: enum ['greulich-pyle', 'tanner-whitehouse-ii', 'tanner-whitehouse-iii', 'fels', 'bonexpert']
        """

        self.birth_date = birth_date
        self.gestation_days = gestation_days
        self.gestation_weeks = gestation_weeks
        self.measurement_method = measurement_method
        self.observation_date = observation_date
        self.observation_value = observation_value
        self.reference = reference
        self.sex = sex
        self.bone_age = bone_age
        self.bone_age_type = bone_age_type
        self.bone_age_sds = bone_age_sds
        self.bone_age_centile = bone_age_centile
        self.bone_age_text = bone_age_text
        # self.height_prediction = height_prediction
        # self.height_prediction_sds = height_prediction_sds
        # self.height_prediction_centile = height_prediction_centile
        # self.height_prediction_reference = height_prediction_reference
        self.events_text = events_text


        # the ages_object receives birth_data and measurement_dates objects
        self.ages_object = self.__calculate_ages(
            sex=self.sex,
            birth_date=self.birth_date,
            observation_date=self.observation_date,
            gestation_weeks=self.gestation_weeks,
            gestation_days=self.gestation_days)
        
        # validate the measurement method to ensure that the observation value is within the expected range - changed to SDS-based cutoffs - issue #32
        try:
            self.__validate_measurement_method(
                measurement_method=measurement_method, observation_value=observation_value, corrected_decimal_age=self.ages_object['measurement_dates']['corrected_decimal_age'], reference=reference, sex=sex)
            observation_value_error = None
        except Exception as err:
            observation_value_error = f"{err}"
        
        # the calculate_measurements_object receives the child_observation_value and measurement_calculated_values objects
        self.calculated_measurements_object = self.sds_and_centile_for_measurement_method(
            sex=self.sex,
            corrected_age=self.ages_object['measurement_dates']['corrected_decimal_age'],
            chronological_age=self.ages_object['measurement_dates']['chronological_decimal_age'],
            measurement_method=self.measurement_method,
            observation_value=self.observation_value,
            observation_value_error=observation_value_error,
            reference=self.reference
        )

        corrected_gestational_age = ""
        if (self.ages_object["measurement_dates"]["corrected_gestational_age"]["corrected_gestation_weeks"] is not None):
            corrected_gestational_age = f'{ self.ages_object["measurement_dates"]["corrected_gestational_age"]["corrected_gestation_weeks"] } + { self.ages_object["measurement_dates"]["corrected_gestational_age"]["corrected_gestation_days"]} weeks'

        self.plottable_centile_data = {
            "chronological_decimal_age_data": {
                "x": self.ages_object['measurement_dates']['chronological_decimal_age'],
                "y": self.observation_value,
                "b": self.bone_age,
                "centile": self.calculated_measurements_object["measurement_calculated_values"]["chronological_centile"],
                "sds": self.calculated_measurements_object["measurement_calculated_values"]["chronological_sds"],
                "events_text": self.events_text,
                "bone_age_label": self.bone_age_text,
                "bone_age_type": self.bone_age_type,
                "bone_age_sds": self.bone_age_sds,
                "bone_age_centile": self.bone_age_centile,
                "observation_error": self.calculated_measurements_object['child_observation_value']["observation_value_error"],
                "age_type": "chronological_age",
                "calendar_age": self.ages_object["measurement_dates"]["chronological_calendar_age"],
                "lay_comment": self.ages_object["measurement_dates"]["comments"]["lay_chronological_decimal_age_comment"],
                "clinician_comment": self.ages_object["measurement_dates"]["comments"]["clinician_chronological_decimal_age_comment"],
                "age_error": self.ages_object["measurement_dates"]["corrected_decimal_age_error"],
                "centile_band": self.calculated_measurements_object['measurement_calculated_values']["chronological_centile_band"],
                "observation_value_error": self.calculated_measurements_object["measurement_calculated_values"]["chronological_measurement_error"]

            },
            "corrected_decimal_age_data": {
                "x": self.ages_object['measurement_dates']['corrected_decimal_age'],
                "y": self.observation_value,
                "b": self.bone_age,
                "centile": self.calculated_measurements_object["measurement_calculated_values"]["corrected_centile"],
                "sds": self.calculated_measurements_object["measurement_calculated_values"]["corrected_sds"],
                "events_text": self.events_text,
                "bone_age_label": self.bone_age_text,
                "bone_age_type": self.bone_age_type,
                "bone_age_sds": self.bone_age_sds,
                "bone_age_centile": self.bone_age_centile,
                "observation_error": self.calculated_measurements_object['child_observation_value']["observation_value_error"],
                "age_type": "corrected_age",
                "corrected_gestational_age": corrected_gestational_age,
                "calendar_age": self.ages_object["measurement_dates"]["corrected_calendar_age"],
                "lay_comment": self.ages_object["measurement_dates"]["comments"]["lay_corrected_decimal_age_comment"],
                "clinician_comment": self.ages_object["measurement_dates"]["comments"]["clinician_corrected_decimal_age_comment"],
                "age_error": self.ages_object["measurement_dates"]["corrected_decimal_age_error"],
                "centile_band": self.calculated_measurements_object['measurement_calculated_values']["corrected_centile_band"],
                "observation_value_error": self.calculated_measurements_object["measurement_calculated_values"]["corrected_measurement_error"]
            }
        }

        self.plottable_sds_data = {
            "chronological_decimal_age_data": {
                "x": self.ages_object['measurement_dates']['chronological_decimal_age'],
                "y": self.calculated_measurements_object['measurement_calculated_values']["chronological_sds"],
                "b": self.bone_age,
                "centile": self.calculated_measurements_object["measurement_calculated_values"]["chronological_centile"],
                "events_text": self.events_text,
                "bone_age_label": self.bone_age_text,
                "bone_age_type": self.bone_age_type,
                "bone_age_sds": self.bone_age_sds,
                "bone_age_centile": self.bone_age_centile,
                "age_type": "chronological_age",
                "calendar_age": self.ages_object["measurement_dates"]["chronological_calendar_age"],
                "lay_comment": self.ages_object["measurement_dates"]["comments"]["lay_chronological_decimal_age_comment"],
                "clinician_comment": self.ages_object["measurement_dates"]["comments"]["clinician_chronological_decimal_age_comment"],
                "age_error": self.ages_object["measurement_dates"]["corrected_decimal_age_error"],
                "centile_band": self.calculated_measurements_object['measurement_calculated_values']["chronological_centile_band"],
                "observation_value_error": self.calculated_measurements_object["measurement_calculated_values"]["chronological_measurement_error"]
            },
            "corrected_decimal_age_data": {
                "x": self.ages_object['measurement_dates']['corrected_decimal_age'],
                "y": self.calculated_measurements_object['measurement_calculated_values']["corrected_sds"],
                "b": self.bone_age,
                "centile": self.calculated_measurements_object["measurement_calculated_values"]["corrected_centile"],
                "events_text": self.events_text,
                "bone_age_label": self.bone_age_text,
                "bone_age_type": self.bone_age_type,
                "bone_age_sds": self.bone_age_sds,
                "bone_age_centile": self.bone_age_centile,
                "age_type": "corrected_age",
                "corrected_gestational_age": corrected_gestational_age,
                "calendar_age": self.ages_object["measurement_dates"]["corrected_calendar_age"],
                "lay_comment": self.ages_object["measurement_dates"]["comments"]["lay_corrected_decimal_age_comment"],
                "clinician_comment": self.ages_object["measurement_dates"]["comments"]["clinician_corrected_decimal_age_comment"],
                "age_error": self.ages_object["measurement_dates"]["corrected_decimal_age_error"],
                "centile_band": self.calculated_measurements_object['measurement_calculated_values']["corrected_centile_band"],
                "observation_value_error": self.calculated_measurements_object["measurement_calculated_values"]["corrected_measurement_error"]
            },
        }

        # the final object is made up of these five components
        self.measurement = {
            'birth_data': self.ages_object['birth_data'],
            'measurement_dates': self.ages_object['measurement_dates'],
            'child_observation_value': self.calculated_measurements_object['child_observation_value'],
            'measurement_calculated_values': self.calculated_measurements_object['measurement_calculated_values'],
            'plottable_data': {
                "centile_data": self.plottable_centile_data,
                "sds_data": self.plottable_sds_data
            },
            # 'height_prediction_data':{
            #     "height_prediction": self.height_prediction,
            #     "height_prediction_sds": self.height_prediction_sds,
            #     "height_prediction_centile": self.height_prediction_centile,
            #     "height_prediction_reference": self.height_prediction_reference
            # },
            'bone_age': {
                "bone_age": self.bone_age,
                "bone_age_type": self.bone_age_type,
                "bone_age_sds": self.bone_age_sds,
                "bone_age_centile": self.bone_age_centile,
                "bone_age_text": self.bone_age_text,
            },
            'events_data': {
                'events_text': self.events_text
            }
        }

    """
    These are 2 public class methods
    """

    def sds_and_centile_for_measurement_method(
        self,
        sex: str,
        corrected_age: float,
        chronological_age: float,
        observation_value_error: str,
        measurement_method: str,
        observation_value: float,
        reference: str
    ):

        # returns sds for given measurement
        # bmi must be supplied precalculated

        # calculate sds based on reference, age, measurement, sex and prematurity

        if corrected_age is None or chronological_age is None:
            # there has been an age calculation error. Further calculation impossible - this may be due to a date error or because CDC reference data is not available in preterm infants

            self.return_measurement_object = self.__create_measurement_object(
                reference=reference,
                measurement_method=measurement_method,
                observation_value=observation_value,
                observation_value_error=observation_value_error,
                corrected_sds_value=None,
                corrected_centile_value=None,
                corrected_centile_band=None,
                chronological_sds_value=None,
                chronological_centile_value=None,
                chronological_centile_band=None,
                chronological_measurement_error="Dates error. Calculations impossible.",
                corrected_measurement_error="Dates error. Calculations impossible.",
                corrected_percentage_median_bmi=None,
                chronological_percentage_median_bmi=None
            )
            return self.return_measurement_object
        
            # CDC data cannot be used for preterm infants who are not yet term. We will not be able to calculate SDS scores and centiles so will return none, but signpost to the user that this is what we are doing.
        if corrected_age < 0 and reference == "cdc":
            corrected_measurement_error = "This baby is born premature. CDC data is not available for preterm infants."
            corrected_measurement_sds = None
        else:
            try:
                corrected_measurement_sds = sds_for_measurement(reference=reference, age=corrected_age, measurement_method=measurement_method,
                                                                observation_value=observation_value, sex=sex)
            except Exception as err:
                corrected_measurement_error = f"{err}"
                corrected_measurement_sds = None

        try:
            chronological_measurement_sds = sds_for_measurement(reference=reference, age=chronological_age, measurement_method=measurement_method,
                                                                observation_value=observation_value, sex=sex)
        except LookupError as err:
            chronological_measurement_error = f"{err}"
            chronological_measurement_sds = None

        if chronological_measurement_sds is None:
            chronological_measurement_centile = None
            chronological_centile_band = None
        else:
            chronological_measurement_error = None
            try:
                chronological_measurement_centile = centile(
                    z_score=chronological_measurement_sds)
            except Exception as err:
                chronological_measurement_error = "Not possible to calculate centile"
                chronological_measurement_centile = None
            try:
                if reference == CDC:
                    if measurement_method == BMI:
                        centile_format = EIGHTY_FIVE_PERCENT_CENTILES
                    else:
                        centile_format = THREE_PERCENT_CENTILES
                else:
                    centile_format = COLE_TWO_THIRDS_SDS_NINE_CENTILES
                chronological_centile_band = centile_band_for_centile(
                    sds=chronological_measurement_sds, 
                    measurement_method=measurement_method,
                    centile_format=centile_format
                    )
            except Exception as err:
                chronological_measurement_error = "Not possible to calculate centile"
                chronological_centile_band = None

        if corrected_measurement_sds is None:
            corrected_measurement_centile = None
            corrected_centile_band = None
        else:
            corrected_measurement_error = None
            try:
                corrected_measurement_centile = centile(
                    z_score=corrected_measurement_sds)
            except Exception as err:
                corrected_measurement_error = "Not possible to calculate centile"
                corrected_measurement_centile = None

            try:
                if reference == CDC:
                    if measurement_method == BMI:
                        centile_format = EIGHTY_FIVE_PERCENT_CENTILES
                    else:
                        centile_format = THREE_PERCENT_CENTILES
                else:
                    centile_format = COLE_TWO_THIRDS_SDS_NINE_CENTILES
                corrected_centile_band = centile_band_for_centile(
                    sds=corrected_measurement_sds, 
                    measurement_method=measurement_method,
                    centile_format=centile_format
                )
            except Exception as err:
                corrected_measurement_error = "Not possible to calculate centile"
                corrected_centile_band = None

        # calculate BMI centiles and percentage median BMI
        corrected_percentage_median_bmi = None
        chronological_percentage_median_bmi = None
        if measurement_method == BMI and corrected_age is not None and chronological_age is not None:
            try: 
                corrected_percentage_median_bmi = percentage_median_bmi(
                reference=reference,
                age=corrected_age,
                actual_bmi=observation_value,
                sex=sex
            )
            except Exception as err:
                print(err)
                corrected_percentage_median_bmi = None
            
            try:
                chronological_percentage_median_bmi = percentage_median_bmi(
                    reference=reference,
                    age=corrected_age,
                    actual_bmi=observation_value,
                    sex=sex
                )
            except Exception as err:
                print(err)
                chronological_percentage_median_bmi = None

        self.return_measurement_object = self.__create_measurement_object(
            reference=reference,
            measurement_method=measurement_method,
            observation_value=observation_value,
            observation_value_error=observation_value_error,
            corrected_sds_value=corrected_measurement_sds,
            corrected_centile_value=corrected_measurement_centile,
            corrected_centile_band=corrected_centile_band,
            chronological_sds_value=chronological_measurement_sds,
            chronological_centile_value=chronological_measurement_centile,
            chronological_centile_band=chronological_centile_band,
            chronological_measurement_error=chronological_measurement_error,
            corrected_measurement_error=corrected_measurement_error,
            corrected_percentage_median_bmi=corrected_percentage_median_bmi,
            chronological_percentage_median_bmi=chronological_percentage_median_bmi
        )

        return self.return_measurement_object

    """
    These are all private class methods and are only accessed by this class on initialisation
    """
    def __calculate_ages(
            self,
            sex: str,
            birth_date: date,
            observation_date: date,
            gestation_weeks: int = 0,
            gestation_days=0):

        if gestation_weeks == 0:
            # if gestation not specified, set to 40 weeks
            gestation_weeks = 40
        # calculate ages from dates and gestational ages at birth


        try:
            self.corrected_decimal_age = corrected_decimal_age(
                birth_date=birth_date,
                observation_date=observation_date,
                gestation_weeks=gestation_weeks,
                gestation_days=gestation_days)
        except Exception as err:
            self.corrected_decimal_age = None
            corrected_decimal_age_error = f"{err}"

        try:
            self.chronological_decimal_age = chronological_decimal_age(
                birth_date=birth_date,
                observation_date=observation_date)
        except Exception as err:
            self.chronological_decimal_age = None
            chronological_decimal_age_error = f"{err}"
        
        # if reference is CDC or WHO, we must treat >37 week infants as term and we also stop correcting for prematurity at 2 years of age
        if self.reference == CDC or self.reference == WHO:
            if (self.corrected_decimal_age >= 2 and gestation_weeks < 37) or (gestation_weeks >= 37 and gestation_weeks <= 42):
                self.corrected_decimal_age = self.chronological_decimal_age

        if self.corrected_decimal_age is None:
            self._age_comments = None
            self.lay_corrected_decimal_age_comment = None
            self.clinician_corrected_decimal_age_comment = None
        else:
            corrected_decimal_age_error = None
            try:
                self.age_comments = comment_prematurity_correction(
                    chronological_decimal_age=self.chronological_decimal_age,
                    corrected_decimal_age=self.corrected_decimal_age,
                    gestation_weeks=gestation_weeks,
                    gestation_days=gestation_days,
                    reference=self.reference)
            except:
                self.age_comments = None
                corrected_decimal_age_error = "Error in comment on prematurity."

            try:
                self.lay_corrected_decimal_age_comment = self.age_comments['lay_corrected_comment']
            except:
                self.lay_corrected_decimal_age_comment = None
                corrected_decimal_age_error = "Error in comment on corrected decimal age."

            try:
                self.clinician_corrected_decimal_age_comment = self.age_comments[
                    'clinician_corrected_comment']
            except:
                self.clinician_corrected_decimal_age_comment = None
                corrected_decimal_age_error = "Error in comment on corrected decimal age."

        if chronological_decimal_age is None:
            self.chronological_calendar_age = None
            self.lay_chronological_decimal_age_comment = None
            self.clinician_chronological_decimal_age_comment = None
            self.corrected_gestational_age = None
            self.estimated_date_delivery = None
            self.estimated_date_delivery_string = None
        else:
            chronological_decimal_age_error = None
            try:
                self.chronological_calendar_age = chronological_calendar_age(
                    birth_date=birth_date,
                    observation_date=observation_date)
            except:
                self.chronological_calendar_age = None
                chronological_decimal_age_error = "Chronological age calculation error."

            try:
                self.lay_chronological_decimal_age_comment = self.age_comments[
                    'lay_chronological_comment']
            except:
                self.lay_chronological_decimal_age_comment = None
                chronological_decimal_age_error = "Chronological age calculation error."

            try:
                self.clinician_chronological_decimal_age_comment = self.age_comments[
                    'clinician_chronological_comment']
            except:
                self.clinician_chronological_decimal_age_comment = None
                chronological_decimal_age_error = "Chronological age calculation error."

            try:
                self.corrected_gestational_age = corrected_gestational_age(
                    birth_date=birth_date,
                    observation_date=observation_date,
                    gestation_weeks=gestation_weeks,
                    gestation_days=gestation_days)
            except:
                self.corrected_gestational_age = None
                chronological_decimal_age_error = "Corrected gestational age calculation error."

            try:
                self.estimated_date_delivery = estimated_date_delivery(
                    birth_date, gestation_weeks, gestation_days)
            except:
                self.estimated_date_delivery = None
                self.estimated_date_delivery_string = None
                chronological_decimal_age_error = "Estimated date of delivery calculation error."

            try:
                self.corrected_calendar_age = chronological_calendar_age(
                    self.estimated_date_delivery, observation_date)
            except Exception as err:
                # The EDD is still in the future as this preterm baby is not yet term. The error returned is not useful as the function is expecting a birth date in the past but is being passed an EDD in the future.
                # It is not really an error, but a limitation of the function. The calendar age really is the same as the corrected gestational age here.
                self.corrected_calendar_age = None
                chronological_decimal_age_error = None

            try:
                self.estimated_date_delivery_string = self.estimated_date_delivery.strftime(
                    '%a %d %B, %Y')
            except:
                self.estimated_date_delivery_string = None
                chronological_decimal_age_error = "Estimated date of delivery calculation error."

        birth_data = {
            "birth_date": birth_date,
            "gestation_weeks": gestation_weeks,
            "gestation_days": gestation_days,
            "estimated_date_delivery": self.estimated_date_delivery,
            "estimated_date_delivery_string": self.estimated_date_delivery_string,
            "sex": sex
        }

        measurement_dates = {
            "observation_date": observation_date,
            "chronological_decimal_age": self.chronological_decimal_age,
            "corrected_decimal_age": self.corrected_decimal_age,
            "chronological_calendar_age": self.chronological_calendar_age,
            "corrected_calendar_age": self.corrected_calendar_age,
            "corrected_gestational_age": {
                "corrected_gestation_weeks": self.corrected_gestational_age["corrected_gestation_weeks"],
                "corrected_gestation_days": self.corrected_gestational_age["corrected_gestation_days"],
            },
            "comments": {
                "clinician_corrected_decimal_age_comment": self.clinician_corrected_decimal_age_comment,
                "lay_corrected_decimal_age_comment": self.lay_corrected_decimal_age_comment,
                "clinician_chronological_decimal_age_comment": self.clinician_chronological_decimal_age_comment,
                "lay_chronological_decimal_age_comment": self.lay_chronological_decimal_age_comment
            },
            "corrected_decimal_age_error": corrected_decimal_age_error,
            "chronological_decimal_age_error": chronological_decimal_age_error
        }

        child_age_calculations = {
            "birth_data": birth_data,
            "measurement_dates": measurement_dates
        }
        return child_age_calculations

    def __create_measurement_object(
        self,
        reference: str,
        measurement_method: str,
        observation_value: float,
        observation_value_error: str,
        corrected_sds_value: float,
        corrected_centile_value: float,
        corrected_centile_band: str,
        chronological_sds_value: float,
        chronological_centile_value: float,
        chronological_centile_band: str,
        chronological_measurement_error: str,
        corrected_measurement_error: str,
        corrected_percentage_median_bmi: str,
        chronological_percentage_median_bmi: str
    ):
        """
        private class method
        This is the end step, having calculated dates, SDS/Centiles and selected appropriate clinical advice,
        to then create a bespoke json Measurement object with values relevant only to the measurement_method requested
        @params: measurement_method: string accepting only 'height', 'weight', 'bmi', 'ofc' lowercase only
        """

        # Measurement object is made up of 4 JSON elements: "birth_data", "measurement_dates",
        #  "child_observation_value" and "measurement_calculated_values"
        # All Measurement objects return the "birth_data" and "measurement_dates" elements
        # Only those calculations relevant to the measurement_method requested populate the final JSON
        # object.

        measurement_calculated_values = {
            "corrected_sds": corrected_sds_value,
            "corrected_centile": corrected_centile_value,
            "corrected_centile_band": corrected_centile_band,
            "chronological_sds": chronological_sds_value,
            "chronological_centile": chronological_centile_value,
            "chronological_centile_band": chronological_centile_band,
            "corrected_measurement_error": corrected_measurement_error,
            "chronological_measurement_error": chronological_measurement_error,
            "corrected_percentage_median_bmi": corrected_percentage_median_bmi,
            "chronological_percentage_median_bmi":chronological_percentage_median_bmi
        }

        child_observation_value = {
            "measurement_method": measurement_method,
            "observation_value": observation_value,
            "observation_value_error": observation_value_error
        }

        return {
            "child_observation_value": child_observation_value,
            "measurement_calculated_values": measurement_calculated_values,
        }

    def __validate_measurement_method(
            self,
            measurement_method: str,
            observation_value: float,
            corrected_decimal_age: float,
            sex: Literal["male", "female"],
            reference: Literal['uk-who', 'turners-syndrome', 'trisomy-21', 'trisomy-21-aap', 'cdc', 'who'] = 'uk-who'):

        # Private method which accepts a measurement_method (height, weight, bmi or ofc), reference and age as well as observation value
        # and returns True if valid

        is_valid = False

        observation_value_z_score = None
        if observation_value is not None:
            observation_value_z_score = sds_for_measurement(
                reference=reference, age=corrected_decimal_age, measurement_method=measurement_method, observation_value=observation_value, sex=sex)

        if measurement_method == 'bmi':
            if observation_value is None:
                raise ValueError(
                    'Missing observation_value for Body Mass Index. Please pass a Body Mass Index in kilograms per metre squared (kg/m²)')
            elif observation_value_z_score < MINIMUM_BMI_ERROR_SDS:
                raise ValueError(
                    f'The Body Mass Index measurement of {observation_value} kg/m² is below -15 SD and considered to be an error.')
            elif observation_value_z_score > MAXIMUM_BMI_ERROR_SDS:
                raise ValueError(
                    f'The Body Mass Index measurement of {observation_value} kg/m² is above +15 SD and considered to be an error.')
            else:
                is_valid = True

        elif measurement_method == 'height':
            if observation_value is None:
                raise ValueError(
                    'Missing observation_value for height/length. Please pass a height/length in cm.')
            elif observation_value < 2:
                # most likely metres passed instead of cm.
                raise ValueError(
                    'Height/length must be passed in cm, not metres')
            elif observation_value_z_score < MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS:
                raise ValueError(
                    f'The height/length of {observation_value} cm is below -8 SD and considered to be an error.')
            elif observation_value_z_score > MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS:
                raise ValueError(
                    f'The height/length of {observation_value} cm is above +8 SD and considered to be an error.')
            else:
                is_valid = True

        elif measurement_method == 'weight':
            if observation_value is None:
                raise ValueError(
                    'Missing observation_value for weight. Please pass a weight in kilograms.')
            elif observation_value_z_score < MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS:
                raise ValueError(
                    f'The weight of {observation_value} kg is below -8 SD and considered to be an error.')
            elif observation_value_z_score > MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS:
                # it is likely the weight is passed in grams, not kg.
                raise ValueError(
                    f'The weight of {observation_value} kg is above +8 SD and considered to be an error. Note that the weight should be supplied in kilograms.')
            else:
                is_valid = True

        elif measurement_method == 'ofc':
            if observation_value is None:
                raise ValueError(
                    'Missing observation_value for head circumference. Please pass a head circumference in centimetres.')
            elif observation_value_z_score < MINIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS:
                raise ValueError(
                    f'The head circumference of {observation_value} cm is below -8 SD and considered to be an error.')
            elif observation_value_z_score > MAXIMUM_HEIGHT_WEIGHT_OFC_ERROR_SDS:
                raise ValueError(
                    f'The head circumference of {observation_value} cm is above +8 SD and considered to be an error.')
            else:
                is_valid = True

        return is_valid