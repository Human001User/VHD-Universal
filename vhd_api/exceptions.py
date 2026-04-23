class VitalSharkAPIError(Exception):
    pass

class UnauthorizedError(VitalSharkAPIError):
    pass

class NotFoundError(VitalSharkAPIError):
    pass

class RequestError(VitalSharkAPIError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")
