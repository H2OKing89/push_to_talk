# utils/helpers.py

import logging
from state.state_manager import state
from utils.logging_utils import sanitize_message

logger = logging.getLogger(__name__)

def graceful_shutdown():
    """Gracefully shuts down the application."""
    logger.info("Initiating graceful shutdown...", extra={'correlation_id': state.correlation_id})
    # Add any cleanup or saving tasks here before exit
    exit(0)

def load_model_with_retry(model_name, logger, correlation_id, trace_id):
    """Attempts to load a model with retry logic."""
    logger.info(f"Loading model {model_name} with retry logic", extra={'correlation_id': correlation_id, 'trace_id': trace_id})
    try:
        # Replace this part with actual model loading logic, for example:
        # model = whisper.load_model(model_name)
        import whisper  # Ensure whisper is imported
        model = whisper.load_model(model_name)
        if not model:
            raise ValueError("Model loading failed.")
        return model
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Failed to load model: {sanitized_error}",
            extra={'correlation_id': correlation_id, 'trace_id': trace_id}
        )
        raise e
