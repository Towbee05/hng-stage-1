from core.schemas import ErrorResponse

# Helper function to handle all error responses
def errorHandler(status:int, message:str) -> ErrorResponse:
    return ErrorResponse(
        status= status,
        message= message
    )