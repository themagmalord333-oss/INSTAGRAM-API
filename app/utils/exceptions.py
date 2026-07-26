class BaseAPIError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class CapacityExceededError(BaseAPIError):
    def __init__(self, message="System is at maximum capacity. Please retry shortly."):
        super().__init__(message, code="CAPACITY_EXCEEDED", status_code=503)

class SourceUnavailableError(BaseAPIError):
    def __init__(self, message="All data sources are temporarily unavailable."):
        super().__init__(message, code="SOURCE_UNAVAILABLE", status_code=503)

class ProfileNotFoundError(BaseAPIError):
    def __init__(self, message="The requested profile does not exist."):
        super().__init__(message, code="PROFILE_NOT_FOUND", status_code=404)