"""Logger module."""
import logging

FORMAT = "%(name)s - %(asctime)s - %(levelname)s | %(message)s"
log_handler = logging.StreamHandler()
log_formatter = logging.Formatter(fmt=FORMAT)
log_handler.setFormatter(log_formatter)


class Logger(logging.Logger):
    """Logger class.

    This class is used to create a logger object that can be used to log messages.
    """

    def __init__(self, name: str) -> None:
        """Initialize the logger.

        Args:
            name (str): Name of the logger.
        """
        super().__init__(name)
        self.addHandler(log_handler)
