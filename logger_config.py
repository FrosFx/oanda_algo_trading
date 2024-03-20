"""
Set and configure logging functionality
"""

import datetime
import logging
import os

# Set the log level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Define the log format and log file name
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create a logger object with the name "Binance-Connector"
logger = logging.getLogger("Oanda-Connector")

# Set the log level
logger.setLevel(LOG_LEVEL)

# Set the log format
formatter = logging.Formatter(LOG_FORMAT)

# The `handler` is used to display log messages on the console
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Add the `handler` to the logger
logger.addHandler(handler)


# Define the logs directory
logs_dir = "./logs"

# Check if the directory exists, if not, create it
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Define the log file name with the current date and time
FILENAME = f"{logs_dir}/{datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.log"

# The `file_handler` is used to write log messages to a log file
file_handler = logging.FileHandler(FILENAME)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
