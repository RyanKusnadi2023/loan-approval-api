from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Tuple, Optional, Dict, Any

class LoanApplication(BaseModel):
    """
    The base Loan class from Pydantic that provides automatic data validation

    Fields: define validation rules
    - ...: indicates that the field is required
	- gt: greater than
	- ge: greater than or equal to
    - Literal: restricts the field to specific string values
    """

    person_age: float = Field(..., gt=0)
    person_gender: Literal["male", "female"]
    person_education: Literal["High School", "Associate", "Bachelor", "Master", "Doctorate"]
    person_income: float = Field(..., ge=0)
    person_emp_exp: int = Field(..., ge=0)
    person_home_ownership: Literal["RENT", "OWN", "MORTGAGE", "OTHER"]
    loan_amnt: float = Field(..., gt=0)
    loan_intent: Literal["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT"]
    loan_int_rate: float = Field(..., ge=0)
    loan_percent_income: float = Field(..., ge=0)
    cb_person_cred_hist_length: float = Field(..., ge=0)
    credit_score: int = Field(..., ge=0)
    previous_loan_defaults_on_file: Literal["Yes", "No"]


def validate_payload(payload: Dict[str, Any], logger) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
	Checks if the given input data follows the rules defined in the LoanApplication model.

    Args:
        payload (Dict[str, Any]): The input data in JSON or dictionary where the keys are strings and the values can be of any data type.

    Returns:
        Tuple:
            - bool: Returns True if the data is valid, False if there are any problems.
            - Optional[Dict[str, Any]]: If the data is valid, returns None.
              If the data is invalid, returns a list of error messages.
              - {'type': 'greater_than', 'loc': ('person_age',), 'msg': 'Input should be greater than 0', 'input': -35.0, 'ctx': {'gt': 0.0}, 'url': 'https://errors.pydantic.dev/2.11/v/greater_than'}
    """
    try:
        LoanApplication(**payload)
        logger.info("Payload validated successfully.")
        return True, None

    except ValidationError as e:
        logger.warning("Payload validation failed. Errors: %s", e.errors())
        return False, e.errors()

    except Exception as e:
        logger.exception("Unexpected error during payload validation.")
        return False, {"error": str(e)}
    