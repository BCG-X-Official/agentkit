import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsoleColor:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def colored_message(message, color):
    """Helper function to wrap a message with a given console color."""
    return f"{color}{message}{ConsoleColor.RESET}"

system_logger = logging.getLogger("system")
user_logger = logging.getLogger("user")

# Prevent log message propagation to the root logger
system_logger.propagate = False
user_logger.propagate = False

system_handler = logging.FileHandler("system_logs.log")
system_handler.setLevel(logging.INFO)

system_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
system_handler.setFormatter(system_formatter)

system_logger.addHandler(system_handler)
system_logger.setLevel(logging.INFO)

user_handler = logging.StreamHandler()
user_handler.setLevel(logging.INFO)

user_formatter = logging.Formatter("%(message)s")
user_handler.setFormatter(user_formatter)

user_logger.addHandler(user_handler)
user_logger.setLevel(logging.INFO)

def log_message(message: str, level: str = "info", target: str = "user", color: str = ConsoleColor.RESET):
    colored_msg = colored_message(message, color)

    logger = system_logger if target == "system" else user_logger
    log_func = getattr(logger, level, logger.info)

    log_func(colored_msg)

def trace(func):
    """Decorator to log function entry, exit, and exceptions."""
    def wrapper(*args, **kwargs):
        log_message(f"Entering {func.__name__} with args: {args} kwargs: {kwargs}",
                    level="info", color=ConsoleColor.BLUE)
        try:
            result = func(*args, **kwargs)
            log_message(f"Exiting {func.__name__} with result: {result}",
                        level="info", color=ConsoleColor.GREEN)
            return result
        except Exception as e:
            log_message(f"Exception in {func.__name__}: {e}",
                        level="error", color=ConsoleColor.RED)
            raise  # Reraise the exception after logging it
    return wrapper