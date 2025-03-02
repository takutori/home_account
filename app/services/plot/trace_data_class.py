from typing import Any
import dataclasses


@dataclasses.dataclass
class TracesData:
    def __init__(self):
        self._trace_names: list[str] = []
        self._traces: list[Any] = []

    @property
    def trace_names(self):
        return self._trace_names

    @property
    def traces(self):
        return self._traces

    @property
    def trace_len(self) -> int:
        return len(self._traces)

    def append(self, trace_name: str, trace: Any):
        """
        traceとその名前を追加する

        Parameters
        ----------
        trace_name : str
            追加したいtraceの名前
        trace : Any
            追加したいtrace
        """
        self._trace_names.append(trace_name)
        self._traces.append(trace)

    def get_index_from_name(self, trace_names: list[str]):
        return [self._trace_names.index(name) for name in trace_names]

    def get_bool_from_name(self, search_trace_names: list[str]) -> list[bool]:
        """
        指定されたtrace_nameに該当するindexはTrueに、それ以外はFalseにしたリストを出力する。

        Parameters
        ----------
        search_trace_names : list[str]
            指定するtraceの名前のリスト

        Returns
        -------
        list[bool]
            該当するtraceのindexではTrue, それ以外はFalseにしたリスト
        """
        return list(map(lambda x: x in search_trace_names, self._trace_names))
