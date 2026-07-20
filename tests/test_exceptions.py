import pytest

from prc.exceptions import (
    AccessError,
    ApiError,
    DeserializationError,
    RateLimited,
    RequestError,
    ServerOfflineError,
    UnknownError,
    SystemError as PRCSystemError
)


def test_api_error_dispatches_by_code():
    error = ApiError.from_dict({"code": 3002, "message": "server offline"})
    
    assert isinstance(error, ServerOfflineError)
    assert isinstance(error, RequestError)
    assert error.code == 3002
    assert error.message == "server offline"

def test_api_error_dispatches_to_unknown_error():
    error = ApiError.from_dict({"code": 0, "message": "server error"})
    
    assert isinstance(error, UnknownError)
    assert isinstance(error, PRCSystemError)
    assert error.code == 0
    assert error.message == "server error"

def test_api_error_rate_limited():
    error = ApiError.from_dict({"code": 4001, "message": "rate limited", "retry_after": 3})
    
    assert isinstance(error, RateLimited)
    assert isinstance(error, AccessError)
    assert error.code == 4001
    assert error.message == "rate limited"
    assert error.retry_after == 3

def test_api_error_falls_back_to_base_class_when_code_is_unmapped():
    error = ApiError.from_dict({"code": 12345, "message": "unmapped"})
    
    assert type(error) is ApiError
    assert error.code == 12345
    assert error.message == "unmapped"

def test_api_error_falls_back_to_subclass_when_code_in_range():
    error = ApiError.from_dict({"code": 4500, "message": "no access"})
    
    assert type(error) is AccessError
    assert error.code == 4500
    assert error.message == "no access"

def test_rate_limited_requires_retry_after():
    with pytest.raises(DeserializationError):
        ApiError.from_dict({"code": 4001, "message": "rate limited"})

def test_error_requires_code_and_message():
    with pytest.raises(DeserializationError):
        ApiError.from_dict({"code": 3002})

    with pytest.raises(DeserializationError):
        ApiError.from_dict({"message": "server offline"})
