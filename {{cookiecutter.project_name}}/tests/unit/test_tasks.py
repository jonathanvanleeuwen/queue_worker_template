from {{cookiecutter.project_name}}.workers.tasks import long_running_task, process_csv, transform_data


class TestTransformData:
    """Test transform_data worker task."""

    def test_uppercase_keys(self, sample_transform_data):
        result = transform_data(sample_transform_data, "uppercase_keys")
        assert result["status"] == "success"
        assert "NAME" in result["result"]
        assert "AGE" in result["result"]
        assert result["result"]["NAME"] == "John"

    def test_lowercase_keys(self):
        data = {"NAME": "John", "AGE": 30}
        result = transform_data(data, "lowercase_keys")
        assert result["status"] == "success"
        assert "name" in result["result"]
        assert "age" in result["result"]

    def test_filter_nulls(self, sample_transform_data):
        result = transform_data(sample_transform_data, "filter_nulls")
        assert result["status"] == "success"
        assert "country" not in result["result"]
        assert "name" in result["result"]

    def test_sum_values(self):
        data = {"a": 10, "b": 20, "c": 30, "d": "text"}
        result = transform_data(data, "sum_values")
        assert result["status"] == "success"
        assert result["result"]["sum"] == 60
        assert result["result"]["count"] == 3

    def test_count_keys(self, sample_transform_data):
        result = transform_data(sample_transform_data, "count_keys")
        assert result["status"] == "success"
        assert result["result"]["count"] == 4

    def test_double_values(self):
        data = {"a": 10, "b": 5, "c": "text"}
        result = transform_data(data, "double_values")
        assert result["status"] == "success"
        assert result["result"]["a"] == 20
        assert result["result"]["b"] == 10
        assert result["result"]["c"] == "text"

    def test_unknown_operation(self, sample_transform_data):
        result = transform_data(sample_transform_data, "unknown_op")
        assert result["status"] == "error"
        assert "Unknown operation" in result["error"]

    def test_metadata_included(self, sample_transform_data):
        result = transform_data(sample_transform_data, "count_keys")
        assert "metadata" in result
        assert "processing_time" in result["metadata"]
        assert result["metadata"]["input_size"] == 4


class TestProcessCSV:
    """Test process_csv worker task."""

    def test_to_json(self, sample_csv_data):
        result = process_csv(sample_csv_data, "to_json")
        assert result["status"] == "success"
        assert len(result["result"]) == 3
        assert result["result"][0]["name"] == "Alice"
        assert result["result"][1]["age"] == "30"

    def test_count_rows(self, sample_csv_data):
        result = process_csv(sample_csv_data, "count_rows")
        assert result["status"] == "success"
        assert result["result"]["row_count"] == 3

    def test_column_stats(self, sample_csv_data):
        result = process_csv(sample_csv_data, "column_stats")
        assert result["status"] == "success"
        assert "age" in result["result"]
        assert "score" in result["result"]
        assert result["result"]["age"]["mean"] == 30.0
        assert result["result"]["score"]["min"] == 87.2

    def test_get_headers(self, sample_csv_data):
        result = process_csv(sample_csv_data, "get_headers")
        assert result["status"] == "success"
        assert set(result["result"]["headers"]) == {"name", "age", "score"}
        assert result["result"]["column_count"] == 3

    def test_first_n_rows(self, sample_csv_data):
        result = process_csv(sample_csv_data, "first_n_rows")
        assert result["status"] == "success"
        assert len(result["result"]["rows"]) == 3
        assert result["result"]["total_rows"] == 3

    def test_unknown_operation(self, sample_csv_data):
        result = process_csv(sample_csv_data, "unknown_op")
        assert result["status"] == "error"
        assert "Unknown operation" in result["error"]

    def test_invalid_csv(self):
        result = process_csv("invalid,csv\ndata", "to_json")
        # Should still succeed with the data it can parse
        assert result["status"] == "success"

    def test_metadata_included(self, sample_csv_data):
        result = process_csv(sample_csv_data, "count_rows")
        assert "metadata" in result
        assert "processing_time" in result["metadata"]
        assert result["metadata"]["total_rows"] == 3
        assert result["metadata"]["columns"] == 3


class TestLongRunningTask:
    """Test long_running_task worker task."""

    def test_completes_successfully(self):
        result = long_running_task(duration=0)  # Use 0 for quick test
        assert result["status"] == "success"
        assert "metadata" in result
        assert "requested_duration" in result["metadata"]

    def test_duration_metadata(self):
        result = long_running_task(duration=0)
        assert result["metadata"]["requested_duration"] == 0
        assert "actual_duration" in result["metadata"]
