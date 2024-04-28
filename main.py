from __future__ import annotations
import logging
from logging.config import dictConfig
import sys
from pathlib import Path
import threading
from typing import List, Tuple, Any, Dict

# Constants and Configuration
LOGS_DIR = Path(__file__).resolve().parent.joinpath('logs')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(levelname)s]%(asctime)s||%(name)s: %(message)s',
            'datefmt': '%Y-%m-%d~%H:%M:%S%z'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'app.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10
        }
    },
    'root': {
        'level': logging.INFO,
        'handlers': ['console', 'file']
    }
}

_lock = threading.Lock()

def _create_paths(*args: str) -> List[Path]:
    created_paths = []
    try:
        with _lock:
            for p in args:
                path = Path(__file__).resolve().parent / p
                path.mkdir(parents=True, exist_ok=True)
                created_paths.append(path)
    except (FileNotFoundError, PermissionError) as e:
        raise Exception(f"Error creating paths: {str(e)}")
    return created_paths

def main(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Tuple[logging.Logger, List[Path], List[str], List[Any]]:
    """Configures logging for the app.

    Args:
        *args: Tuple[Any]
            Positional arguments passed to the function.
        **kwargs: Dict[str, Any]
            Keyword arguments passed to the function.

    Returns:
        Tuple[logging.Logger, List[Path], List[str], List[Any]]:
            A tuple containing:
                - logging.Logger: The configured logger instance.
                - List[Path]: A list of created directory paths.
                - List[str]: A list of string arguments.
                - List[Any]: A list of non-string arguments.
    """
    current_dir = Path(__file__).resolve().parent
    sys.path.append(str(current_dir))

    LOGS_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

    paths = _create_paths("vault", "templates", "output", "logs", "src")
    logger = logging.getLogger(__name__)
    logger.info(f'\n|Source_file: {__file__}||'
                f'\n|Invocation_dir: {current_dir}||'
                f'\n|Working_dir: {current_dir}||')

    arguments = [str(_).lower().strip() for _ in sys.argv if len(_) > 0]
    misc_args = []

    for arg in args:
        if isinstance(arg, str):
            arguments.append(arg)
        else:
            misc_args.append(arg)

    for k, v in kwargs.items():
        if isinstance(v, str):
            arguments.append(f"{k}={v}")
        else:
            misc_args.append(v)

    logging.info(f'|Arguments: \n{arguments}||')
    logging.info(f'|Misc Args: \n{misc_args}||')
    return logger, paths, arguments, misc_args


if __name__ == '__main__':
    logger, created_paths, arguments, misc_args = main()
    print("Logger:", logger)
    print("Created paths:", created_paths)
    print("Arguments:", arguments)
    print("Misc Args:", misc_args)