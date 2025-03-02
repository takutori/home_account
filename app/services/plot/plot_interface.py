from abc import ABCMeta, abstractmethod

from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

from app.services.plot.trace_data_class import TracesData


class CreatePlotly(metaclass=ABCMeta):
    def __init__(self, accounting_interval: list[datetime] | None):
        self._accounting_interval = accounting_interval
        self._traces_data = TracesData()

    def create(self) -> go.Figure:
        fig = go.Figure(data=self.traces(), layout=self.layout())

        return fig

    @abstractmethod
    def traces(self):
        raise NotImplementedError

    @abstractmethod
    def layout(self, trace_name: list[str]):
        raise NotImplementedError



