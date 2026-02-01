from typing import Any


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, detail: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource} not found: {resource_id}",
            status_code=404,
        )


class AuthenticationError(AppError):
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message=message, status_code=401)


class AuthorizationError(AppError):
    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message=message, status_code=403)
