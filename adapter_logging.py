# adapter_logging.py
from __future__ import annotations
import logging
from abc import ABC, abstractmethod

class AppLogger(ABC):
    @abstractmethod
    def info(self, msg: str): ...
    @abstractmethod
    def warning(self, msg: str): ...
    @abstractmethod
    def error(self, msg: str): ...

class PythonLoggingAdapter(AppLogger):
    """Adapter que converte nossa interface AppLogger na lib 'logging' do Python."""
    def __init__(self, name: str = "reserva_logger"):
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            fmt = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
            handler.setFormatter(fmt)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def info(self, msg: str): self._logger.info(msg)
    def warning(self, msg: str): self._logger.warning(msg)
    def error(self, msg: str): self._logger.error(msg)
