# memento.py — Caretaker + Memento p/ estado do sistema
from dataclasses import dataclass
from copy import deepcopy
from typing import Any, List

@dataclass(frozen=True)
class ReservationSnapshot:
    users: Any
    salas: Any
    reservas: Any

class HistoryService:
    def __init__(self, capacity: int = 50):
        self._undo_stack: List[ReservationSnapshot] = []
        self._redo_stack: List[ReservationSnapshot] = []
        self._capacity = capacity

    def push(self, snapshot: ReservationSnapshot):
        if len(self._undo_stack) >= self._capacity:
            self._undo_stack.pop(0)
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()

    def undo(self, current: ReservationSnapshot) -> ReservationSnapshot | None:
        if not self._undo_stack:
            return None
        snap = self._undo_stack.pop()
        self._redo_stack.append(current)
        return snap

    def redo(self, current: ReservationSnapshot) -> ReservationSnapshot | None:
        if not self._redo_stack:
            return None
        snap = self._redo_stack.pop()
        self._undo_stack.append(current)
        return snap
