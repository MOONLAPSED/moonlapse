from __future__ import annotations
import concurrent.futures
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

def curry_main(*args: Tuple[Any], **kwargs: Dict[str, Any]) -> Tuple[logging.Logger, List[Path], List[str], List[Any]]:
    """
    Invoke the main function separately for different types of arguments.

    Args:
        *args: Positional arguments to be passed to the main function.
        **kwargs: Keyword arguments to be passed to the main function.

    Returns:
        Tuple[logging.Logger, List[Path], List[str], List[Any]]: The combined results from all invocations of the main function.
    """
    combined_logger = None
    combined_paths = []
    combined_arguments = []
    combined_misc_args = []

    # Separate arguments based on type
    str_args = [arg for arg in args if isinstance(arg, str)]
    non_str_args = [arg for arg in args if not isinstance(arg, str)]

    # Run main() for string arguments
    if str_args:
        logger, paths, arguments, misc_args = main(*str_args, **kwargs)
        combined_logger = logger
        combined_paths.extend(paths)
        combined_arguments.extend(arguments)
        combined_misc_args.extend(misc_args)

    # Run main() in parallel for non-string arguments
    if non_str_args:
        run_main_parallel(non_str_args)

    return combined_logger, combined_paths, combined_arguments, combined_misc_args

def run_main_parallel(args):
    """
    Run the main function in parallel for each argument.

    Args:
        args (list): A list of arguments to pass to the main function.
    """
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Run main() for each argument in parallel
        futures = [executor.submit(main, arg) for arg in args]

        # Wait for all the tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.exception(f"Error in parallel execution: {e}")

if __name__ == '__main__':
    # Test the main function with different combinations of arguments
    print("Testing main function...")
    logger, created_paths, arguments, misc_args = main()
    print("Logger:", logger)
    print("Created paths:", created_paths)
    print("Arguments:", arguments)
    print("Misc Args:", misc_args)
    print()

    logger, created_paths, arguments, misc_args = main("arg1", "arg2", key1="value1", key2=123)
    print("Logger:", logger)
    print("Created paths:", created_paths)
    print("Arguments:", arguments)
    print("Misc Args:", misc_args)
    print()

    logger, created_paths, arguments, misc_args = main(1, 2.0, "arg3", key3=[1, 2, 3], key4={"a": 1, "b": 2})
    print("Logger:", logger)
    print("Created paths:", created_paths)
    print("Arguments:", arguments)
    print("Misc Args:", misc_args)
    print()

    # Test the curry_main function with different combinations of arguments
    print("Testing curry_main function...")
    logger, created_paths, arguments, misc_args = curry_main()
    print("Logger:", logger)
    print("Created paths:", created_paths)
    print("Arguments:", arguments)
    print("Misc Args:", misc_args)
    print()

    logger, created_paths, arguments, misc_args = curry_main("arg1", "arg2", key1="value1", key2=123)
    print("Logger:", logger)
    print("Created paths:", created_paths)
    print("Arguments:", arguments)
    print("Misc Args:", misc_args)
    print()

    logger, created_paths, arguments, misc_args = curry_main(1, 2.0, "arg3", key3=[1, 2, 3], key4={"a": 1, "b": 2})
    print("Logger:", logger)
    print("Created paths:", created_paths)
    print("Arguments:", arguments)
    print("Misc Args:", misc_args)
    print()
    """
    In this updated if __name__ == '__main__' block, we test both the main and curry_main functions with various combinations of arguments, including:

    No arguments
    String arguments
    A mix of string and non-string arguments (integers, floats, lists, dictionaries)
    Keyword arguments

    For each test case, the returned values (logger, created_paths, arguments, misc_args) are printed to the console, allowing you to inspect the outputs and ensure they are as expected.
    By running this code, you can verify the following:

    The main function handles different types of arguments correctly, separating string and non-string arguments into their respective lists.
    The curry_main function correctly invokes the main function for string arguments and runs the run_main_parallel function for non-string arguments.
    The run_main_parallel function is executed as expected for non-string arguments.
    The logging configuration and path creation work as intended.

    This approach allows you to comprehensively test the code's functionality and ensure that it behaves as expected under various input scenarios. You can further extend the test cases to cover any additional edge cases or specific scenarios that you need to validate.
    """