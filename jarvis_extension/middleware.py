import functools
import traceback
from datetime import datetime
from jarvis_extension.logger import jarvis_logger

def log_event_decorator(event_type="GENERIC_EVENT"):
    """Decorator to log a function's execution and its result."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            session_id = "CURRENT_SESSION" # Ideally pull from context
            
            # Extract possible session info from context (if exists)
            # This is a generalized approach
            try:
                # Store call info
                jarvis_logger.log(
                    event_type=event_type, 
                    session_id=session_id, 
                    function=func.__name__,
                    args=str(args),
                    kwargs=str(kwargs)
                )

                result = func(*args, **kwargs)
                
                # Optionally log result
                jarvis_logger.log(
                    event_type="RESULT_" + event_type, 
                    session_id=session_id, 
                    function=func.__name__,
                    result=str(result)
                )
                
                return result
            except Exception as e:
                # Auto-log errors
                error_trace = traceback.format_exc()
                jarvis_logger.error(
                    session_id=session_id, 
                    error_msg=str(e), 
                    function=func.__name__,
                    trace=error_trace
                )
                raise e # Re-raise to not break Jarvis logic
        return wrapper
    return decorator

# --- WRAPPER HELPERS (Plug & Play) ---

def wrap_and_log_input(func, session_id="CURRENT_SESSION"):
    """Wrap any user-input capture function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str):
            jarvis_logger.user_input(session_id, result)
        return result
    return wrapper

def wrap_and_log_api(func, service_name, session_id="CURRENT_SESSION"):
    """Wrap any API call function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        jarvis_logger.api_call(session_id, service_name, args=str(args), kwargs=str(kwargs))
        return func(*args, **kwargs)
    return wrapper

def wrap_and_log_error(func, session_id="CURRENT_SESSION"):
    """Wrap function to auto-log errors."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            jarvis_logger.error(session_id, str(e), traceback=traceback.format_exc())
            raise e
    return wrapper
