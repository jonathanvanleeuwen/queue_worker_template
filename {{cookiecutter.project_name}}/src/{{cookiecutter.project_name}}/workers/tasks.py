import csv
import io
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


def transform_data(data: dict, operation: str) -> dict[str, Any]:
    """
    Transform dictionary data based on the specified operation.

    Supported operations:
    - uppercase_keys: Convert all keys to uppercase
    - lowercase_keys: Convert all keys to lowercase
    - filter_nulls: Remove all keys with null/None values
    - sum_values: Sum all numeric values
    - count_keys: Count the number of keys
    - double_values: Double all numeric values

    Args:
        data: Dictionary to transform
        operation: Operation to perform

    Returns:
        Dictionary with status, result, and metadata
    """
    start_time = time.time()
    logger.info("Starting transform_data operation: %s", operation)

    try:
        if operation == "uppercase_keys":
            result = {k.upper(): v for k, v in data.items()}
        elif operation == "lowercase_keys":
            result = {k.lower(): v for k, v in data.items()}
        elif operation == "filter_nulls":
            result = {k: v for k, v in data.items() if v is not None}
        elif operation == "sum_values":
            numeric_values = [v for v in data.values() if isinstance(v, int | float)]
            result = {"sum": sum(numeric_values), "count": len(numeric_values)}
        elif operation == "count_keys":
            result = {"count": len(data)}
        elif operation == "double_values":
            result = {
                k: v * 2 if isinstance(v, int | float) else v for k, v in data.items()
            }
        else:
            raise ValueError(f"Unknown operation: {operation}")

        processing_time = time.time() - start_time
        logger.info("Completed transform_data in %.2f seconds", processing_time)

        return {
            "status": "success",
            "operation": operation,
            "result": result,
            "metadata": {
                "processing_time": processing_time,
                "input_size": len(data),
            },
        }

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error("Error in transform_data: %s", e, exc_info=True)
        return {
            "status": "error",
            "operation": operation,
            "error": str(e),
            "error_type": type(e).__name__,
            "metadata": {
                "processing_time": processing_time,
            },
        }


def process_csv(csv_string: str, operation: str) -> dict[str, Any]:
    """
    Process CSV data based on the specified operation.

    Supported operations:
    - to_json: Convert CSV to list of dictionaries
    - count_rows: Count number of rows (excluding header)
    - column_stats: Get statistics for numeric columns
    - get_headers: Return column headers
    - first_n_rows: Return first 10 rows as dictionaries

    Args:
        csv_string: CSV data as string
        operation: Operation to perform

    Returns:
        Dictionary with status, result, and metadata
    """
    start_time = time.time()
    logger.info("Starting process_csv operation: %s", operation)

    try:
        csv_file = io.StringIO(csv_string)
        reader = csv.DictReader(csv_file)
        rows = list(reader)

        if operation == "to_json":
            result = rows
        elif operation == "count_rows":
            result = {"row_count": len(rows)}
        elif operation == "column_stats":
            # Get statistics for numeric columns
            if not rows:
                result = {"message": "No data to analyze"}
            else:
                stats = {}
                for column in rows[0].keys():
                    numeric_values = []
                    for row in rows:
                        try:
                            numeric_values.append(float(row[column]))
                        except (ValueError, TypeError):
                            pass

                    if numeric_values:
                        stats[column] = {
                            "count": len(numeric_values),
                            "sum": sum(numeric_values),
                            "mean": sum(numeric_values) / len(numeric_values),
                            "min": min(numeric_values),
                            "max": max(numeric_values),
                        }
                result = stats
        elif operation == "get_headers":
            result = {
                "headers": list(rows[0].keys()) if rows else [],
                "column_count": len(rows[0]) if rows else 0,
            }
        elif operation == "first_n_rows":
            result = {"rows": rows[:10], "total_rows": len(rows)}
        else:
            raise ValueError(f"Unknown operation: {operation}")

        processing_time = time.time() - start_time
        logger.info("Completed process_csv in %.2f seconds", processing_time)

        return {
            "status": "success",
            "operation": operation,
            "result": result,
            "metadata": {
                "processing_time": processing_time,
                "total_rows": len(rows),
                "columns": len(rows[0]) if rows else 0,
            },
        }

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error("Error in process_csv: %s", e, exc_info=True)
        return {
            "status": "error",
            "operation": operation,
            "error": str(e),
            "error_type": type(e).__name__,
            "metadata": {
                "processing_time": processing_time,
            },
        }


def long_running_task(duration: int = 10) -> dict[str, Any]:
    """
    A simple long-running task for testing purposes.

    Args:
        duration: How long to run in seconds

    Returns:
        Dictionary with status and result
    """
    start_time = time.time()
    logger.info("Starting long_running_task for %d seconds", duration)

    try:
        time.sleep(duration)
        processing_time = time.time() - start_time

        return {
            "status": "success",
            "message": f"Completed after {duration} seconds",
            "metadata": {
                "requested_duration": duration,
                "actual_duration": processing_time,
            },
        }

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error("Error in long_running_task: %s", e, exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "metadata": {
                "processing_time": processing_time,
            },
        }
