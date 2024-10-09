# utils/helpers.py

import sys
import time
import logging
from utils.logging_utils import sanitize_message
from state import state

logger = logging.getLogger(__name__)

def load_model_with_retry(load_function, model_name, retries=3, delay=2):
    """
    Attempts to load a model with a specified number of retries and delay between attempts.

    Args:
        load_function (callable): The function to load the model.
        model_name (str): The name of the model to load.
        retries (int): Number of retry attempts.
        delay (int): Delay between retries in seconds.

    Returns:
        The loaded model.

    Raises:
        Exception: If all retry attempts fail.
    """
    attempt = 0
    while attempt < retries:
        try:
            model = load_function(model_name)
            return model
        except Exception as e:
            attempt += 1
            sanitized_error = sanitize_message(str(e))
            logger.warning(
                f"Attempt {attempt} to load model '{model_name}' failed: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            time.sleep(delay)
    raise Exception(f"All {retries} attempts to load model '{model_name}' have failed.")

def graceful_shutdown():
    """
    Gracefully shuts down the application.
    """
    logger.info("Gracefully shutting down the application...", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
    sys.exit(0)
