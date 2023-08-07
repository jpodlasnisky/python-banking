from functools import wraps

from eventsourcing.application import AggregateNotFound
from werkzeug.exceptions import BadRequest

from typing import Any, Callable, Dict, Tuple, Union
from werkzeug.exceptions import BadRequest
from eventsourcing.application import AggregateNotFound
from banking.domainmodel import (
    AccountClosedError,
    BadCredentials,
    InsufficientFundsError,
    InvalidDeposit,
)
from functools import wraps


def handler(func: Callable[..., Union[Dict[str, Any], Tuple[Dict[str, Any], int]]]) -> Callable[..., Union[Dict[str, Any], Tuple[Dict[str, Any], int]]]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
        try:
            return func(*args, **kwargs)
        except AccountClosedError as err:
            return {"error": str(err)}, 400
        except InsufficientFundsError as err:
            return {"error": str(err)}, 400
        except BadCredentials as err:
            return {"error": str(err)}, 401
        except InvalidDeposit as err:
            return {"error": str(err)}, 400
    return wrapper
