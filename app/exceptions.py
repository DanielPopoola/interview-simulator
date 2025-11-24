class InterviewSimulatorException(Exception):
    pass


class ValidationError(InterviewSimulatorException):
    pass


class NotFoundError(InterviewSimulatorException):
    pass


class DocumentParsingError(InterviewSimulatorException):
    pass


class AIServiceError(InterviewSimulatorException):
    pass
