from __future__ import annotations
import concurrent.futures
import logging
from logging.config import dictConfig
import sys
from pathlib import Path
import threading
from typing import List, Tuple, Any, Dict
import os
import sys
import time

# Constants and Configuration
from src.prompt import Prompt
from src.ui import generate_response, get_embedding, client
from tests.test_base import run_tests
LOGS_DIR = Path(__file__).resolve().parent.joinpath('logs')
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
tests_dir = os.path.join(current_dir, 'tests')
sys.path.append(tests_dir)
sys.path.append(src_dir)

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


def _paths(*args: str) -> List[Path]:
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
    """
    Initializes the application/runtime environment.

    This function configures the logging system based on predefined configurations
    and initializes the application by setting up necessary paths and logging information.

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
                - List[str]: A list of string arguments passed to the function.
                - List[Any]: A list of non-string arguments passed to the function.

    Notes:
        - This function initializes the logging system using predefined configurations
          stored in the `LOGGING_CONFIG` constant.
        - It creates necessary directories (vault, templates, output, logs, src) using
          the `_create_paths` function to ensure required directories exist.
        - The logger instance created here is used to log key information about the
          execution environment, such as source file, invocation directory, and working directory.
        - The function collects and processes command-line arguments (`sys.argv`), converting
          them into lowercase strings and filtering out empty strings.
        - Additional arguments (`*args` and `**kwargs`) are processed and categorized into
          `arguments` (string-based) and `misc_args` (non-string).

    Examples:
        To initialize the application:
        ```
        logger, paths, arguments, misc_args = main()
        ```

        To pass custom arguments and keyword arguments:
        ```
        logger, paths, arguments, misc_args = main("arg1", "arg2", key1="value1", key2=123)
        ```

    Raises:
        Exception: If there is an error creating directory paths due to file not found or
                   permission issues.

    """
    current_dir = Path(__file__).resolve().parent
    sys.path.append(str(current_dir))

    LOGS_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

    paths = _paths("vault", "templates", "output", "logs", "src")
    logger = logging.getLogger(__name__)
    logger.info(f'\n|Source_file: {__file__}||'
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
    Invoke the main function recursively for each argument.

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
    combined_logger = None
    combined_paths = []
    combined_arguments = []
    combined_misc_args = []

    for arg in args:
        if isinstance(arg, (tuple, list)):
            logger, paths, arguments, misc_args = curry_main(*arg, **kwargs)
        else:
            logger, paths, arguments, misc_args = main(arg, **kwargs)

        combined_logger = logger
        combined_paths.extend(paths)
        combined_arguments.extend(arguments)
        combined_misc_args.extend(misc_args)

    for k, v in kwargs.items():
        if isinstance(v, (tuple, list)):
            logger, paths, arguments, misc_args = curry_main(*v, **{k: kwargs[k]})
        else:
            logger, paths, arguments, misc_args = main(k=v, **kwargs)

        combined_logger = logger
        combined_paths.extend(paths)
        combined_arguments.extend(arguments)
        combined_misc_args.extend(misc_args)

    non_str_args = [arg for arg in args if not isinstance(arg, str)]
    if non_str_args:
        run_main_parallel(non_str_args, test_case_num=kwargs.get('test_case_num', None))

    return combined_logger, combined_paths, combined_arguments, combined_misc_args
def run_main_parallel(args, test_case_num=None):
    """
    Run the main function in parallel for each argument.

    This function utilizes Python's multiprocessing to execute the main function
    concurrently for each provided argument. Each subprocess inherits the logging
    configuration from the main process, including its root logger. By default,
    subprocess loggers are named after the entry point function of the process,
    which in this case is likely to be 'main()'. Therefore, log messages from
    subprocesses may appear with logger names such as 'main' or 'mp_main',
    depending on the logging configuration and multiprocessing implementation.

    Args:
        args (list): A list of arguments to pass to the main function.
        test_case_num (int, optional): The test case number. Defaults to None.
    """
    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Run main() for each argument in parallel
            futures = [executor.submit(main, arg, test_case_num=test_case_num) for arg in args]

            # Wait for all the tasks to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.exception(f"Error in test case {test_case_num} parallel execution: {e}")
    except Exception as e:
        logging.exception(f"Error in test case {test_case_num} parallel execution: {e}")

def wizard() -> None:
    print(r"""
                    ____ 
                  .'* *.'
               __/_*_*(_
              / _______ \
             _\_)/___\(_/_ 
            / _((\- -/))_ \
            \ \())(-)(()/ /
             ' \(((()))/ '
            / ' \)).))/ ' \
           / _ \ - | - /_  \
          (   ( .;''';. .'  )
          _\"__ /    )\ __"/_
            \/  \   ' /  \/
             .'  '...' ' )
              / /  |  \ \
             / .   .   . \
            /   .     .   \
           /   /   |   \   \
         .'   /    q    '.  '.
     _.-'    /     Qq     '-. '-._ 
 _.-'       |      QQq       '-.  '-. 
(_________/_|____.qQQQq.________)____)
    """)

    list(map(lambda char: (print(char, end="", flush=True), time.sleep(0.05)), "Welcome to moonlapse!"))
    print("All tests passed!")
    print("\n\n")


if __name__ == '__main__':
    # Test the main and curry_main functions with different combinations of arguments
    paths = _paths()
    wizard()
    test_cases = [
        (),
        ("arg1", "arg2",),
        (1, 2.0, "arg3",),
        ("arg1", "arg2",),
        (1, 2.0, "arg3", "arg4", "arg5",),
    ]

    for idx, test_args in enumerate(test_cases, start=1):
        print(f"Testing case {idx}...")
        logger, created_paths, arguments, misc_args = curry_main(*test_args, test_case_num=idx)
        print("Arguments:", arguments)
        print("Misc Args:", misc_args)
        print()

    run_tests()

    def main():
        """
        Main function to generate a response using the Prompt class.

        This function creates a Prompt instance, generates a response using the instance's generate_response method,
        and prints the response. It also handles any exceptions that may occur during the process.

        If no exception occurs, it prints a success message. If an exception occurs, it prints the exception message
        and a message about the client runtime environment not being connected.
        """
        try:
            prompt = Prompt(prompt="Hello, please explain the laws of calculus.")
            response = prompt.generate_response()
            print(response)
            print("All tests passed!")
            print("\n")
        except Exception as e:
            print(f"Error: {e}")
            print("httpx does not read the server, client runtime environment is configured but not connected.")
            print("\n")

    if __name__ == "__main__":
        main()