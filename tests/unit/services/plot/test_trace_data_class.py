import pytest
from app.services.plot.trace_data_class import TracesData




class TestTracesData:
    def test_append(self):
        traces = TracesData()
        traces.append(trace_name="test", trace=2)

        assert traces.traces == [2]
        assert traces.trace_names == ["test"]

    def test_get_index_from_name(self):
        traces = TracesData()
        for name, value in zip(["a", "b", "c", "d", "e"], range(5)):
            traces.append(trace_name=name, trace=value)

        assert traces.get_index_from_name(trace_names=["a", "d"]) == [0, 3]
        assert traces.get_index_from_name(trace_names=["c"]) == [2]
        assert traces.get_index_from_name(trace_names=["b", "e"]) == [1, 4]
