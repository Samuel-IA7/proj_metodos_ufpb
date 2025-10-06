# strategy_conflict.py
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from models import Reserva
from exceptions import ConflitoDeReservaException

class ConflictStrategy(ABC):
    """Interface da Strategy: diferentes políticas de detecção de conflito."""
    @abstractmethod
    def validar(self, nova: Reserva, reservas_existentes: List[Reserva]) -> None:
        ...

class StrictConflictStrategy(ConflictStrategy):
    """Não permite qualquer sobreposição entre [inicio, fim)."""
    def validar(self, nova: Reserva, reservas_existentes: List[Reserva]) -> None:
        novo_ini = datetime.strptime(nova.hora_inicio, "%H:%M").time()
        novo_fim = datetime.strptime(nova.hora_fim, "%H:%M").time()
        for r in reservas_existentes:
            ini = datetime.strptime(r.hora_inicio, "%H:%M").time()
            fim = datetime.strptime(r.hora_fim, "%H:%M").time()
            if max(novo_ini, ini) < min(novo_fim, fim):
                raise ConflitoDeReservaException(
                    f"Conflito! Sala já reservada de {r.hora_inicio} a {r.hora_fim}."
                )

class LenientConflictStrategy(ConflictStrategy):
    """
    Permite pequena margem de 5 min entre fim/início adjacentes.
    Ex.: fim 10:00 e início 10:04 ainda conflita; 10:05 não conflita.
    """
    def __init__(self, margem_minutos: int = 5):
        self.margem = margem_minutos

    def validar(self, nova: Reserva, reservas_existentes: List[Reserva]) -> None:
        novo_ini_dt = datetime.strptime(nova.hora_inicio, "%H:%M")
        novo_fim_dt = datetime.strptime(nova.hora_fim, "%H:%M")
        for r in reservas_existentes:
            ini_dt = datetime.strptime(r.hora_inicio, "%H:%M")
            fim_dt = datetime.strptime(r.hora_fim, "%H:%M")

            # Se a distância entre os intervalos for menor que a margem, considera conflito
            dist_apos = (novo_ini_dt - fim_dt).total_seconds() / 60.0  # nova começa após fim existente
            dist_antes = (ini_dt - novo_fim_dt).total_seconds() / 60.0  # existente começa após fim nova
            sobrepoe = not (dist_apos >= self.margem or dist_antes >= self.margem)
            if sobrepoe:
                raise ConflitoDeReservaException(
                    f"Tolerância excedida próximo de {r.hora_inicio}-{r.hora_fim}."
                )
