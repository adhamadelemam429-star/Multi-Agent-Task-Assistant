class MultiAgentError(Exception):
    """Base error for the assistant."""


class PlanningError(MultiAgentError):
    """Raised when user request cannot be turned into a valid plan."""


class ToolExecutionError(MultiAgentError):
    """Raised when a registered tool cannot execute safely."""


class ValidationError(MultiAgentError):
    """Raised when input payload is invalid."""


class TaskExecutionError(MultiAgentError):
    """Raised when a task fails or times out."""
