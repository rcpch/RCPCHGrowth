from rcpchgrowth.constants import CDC, WHO

def comment_prematurity_correction(
    chronological_decimal_age: float,
    corrected_decimal_age: float,
    gestation_weeks: int,
    gestation_days: int,
    reference: str):
    """
    Returns interpretations on age correction as a string
    """

    if chronological_decimal_age == corrected_decimal_age:
        # no adjustment has been made so the child was born at 40 weeks or this child is being plotted on the CDC reference, where no adjustment is made for 37-42 weeks or beyond the age of 2 years
            lay_corrected_decimal_age_comment = "Your child was born on their due date."
            clinician_corrected_decimal_age_comment = "Born at term. No correction has been made for gestation."
            lay_chronological_decimal_age_comment = "Your child was born on their due date."
            clinician_chronological_decimal_age_comment = "Born Term. No correction has been made for gestation."
            # These fields should only apply to CDC reference, since UK-WHO corrects for all gestations (and therefore corrected_decimal_age will never be equal to chronological_decimal_age if gestation_weeks is not 40)
            if gestation_weeks < 42 and (reference == CDC or reference == WHO):
                if gestation_weeks < 37:
                    lay_chronological_decimal_age_comment = f"Your child was born at {gestation_weeks}+{gestation_days} weeks gestation. No correction is made for this beyond 2 years of age."
                    clinician_chronological_decimal_age_comment =f"Born preterm at {gestation_weeks}+{gestation_days} weeks gestation. No correction is made for this beyond 2 years of age."
                    lay_corrected_decimal_age_comment = f"Your child was born at {gestation_weeks}+{gestation_days} weeks gestation. No correction is made for this beyond 2 years of age."
                    clinician_corrected_decimal_age_comment = f"Born preterm at {gestation_weeks}+{gestation_days} weeks gestation. No correction is made for this beyond 2 years of age."
                else:
                    lay_chronological_decimal_age_comment = f"Your child was born at {gestation_weeks}+{gestation_days} weeks gestation. This is considered term and no correction for gestation has been made."
                    clinician_chronological_decimal_age_comment = f"Born at term ({gestation_weeks}+{gestation_days} weeks gestation). No correction for gestation has been made."
                    lay_corrected_decimal_age_comment = f"Your child was born at {gestation_weeks}+{gestation_days} weeks gestation. This is considered term and no correction for gestation has been made."
                    clinician_corrected_decimal_age_comment = f"Born at term ({gestation_weeks}+{gestation_days} weeks gestation). No correction for gestation has been made."
                    if gestation_weeks == 40 and gestation_days == 0:
                        lay_chronological_decimal_age_comment = "Your child was born at term. No correction for gestation has been made."
                        clinician_chronological_decimal_age_comment = "Born at term. No correction for gestation has been made."
                        lay_corrected_decimal_age_comment = "Your child was born at term. No correction for gestation has been made."
                        clinician_corrected_decimal_age_comment = "Born at term. No correction for gestation has been made."
    elif chronological_decimal_age > corrected_decimal_age or chronological_decimal_age < corrected_decimal_age:
        ## adjustment for gestational age has been made - even if >=37 weeks
        lay_corrected_decimal_age_comment = f"Because your child was born at {gestation_weeks}+{gestation_days} weeks gestation an adjustment has been made to take this into account."
        clinician_corrected_decimal_age_comment = "Correction for gestational age has been made."
        lay_chronological_decimal_age_comment = "This is your child's age without taking into account their gestation at birth."
        clinician_chronological_decimal_age_comment = "No correction has been made for gestational age."
    else:
        #some error
        lay_corrected_decimal_age_comment = "It has not been possible to calculate age this time."
        clinician_corrected_decimal_age_comment = "It has not been possible to calculate age this time."
        lay_chronological_decimal_age_comment = "It has not been possible to calculate age this time."
        clinician_chronological_decimal_age_comment = "It has not been possible to calculate age this time."

    comment = {
        'lay_corrected_comment': lay_corrected_decimal_age_comment,
        'lay_chronological_comment': lay_chronological_decimal_age_comment,
        'clinician_corrected_comment': clinician_corrected_decimal_age_comment,
        'clinician_chronological_comment': clinician_chronological_decimal_age_comment
    }
    return comment