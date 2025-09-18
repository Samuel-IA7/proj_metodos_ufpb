# infra_ram.py (Implementações em memória)
from typing import Dict, Iterable, Optional, List
from models import Usuario, Sala, Reserva
from repository import UserDAO, SalaDAO, ReservaDAO

# --------- USERS ----------
class UserDAORAM(UserDAO):
    def __init__(self):
        self._by_id: Dict[int, Usuario] = {}
        self._id_of_login: Dict[str, int] = {}
        self._next_id = 1

    def _alloc_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def add(self, u: Usuario) -> None:
        uid = self._alloc_id()
        self._by_id[uid] = u
        self._id_of_login[u.login] = uid

    def get_by_login(self, login: str) -> Optional[Usuario]:
        uid = self._id_of_login.get(login)
        return self._by_id.get(uid) if uid else None

    def get_by_id(self, uid: int) -> Optional[Usuario]:
        return self._by_id.get(uid)

    def list_all(self) -> Iterable[Usuario]:
        return list(self._by_id.values())

    def update(self, u: Usuario) -> None:
        uid = self._id_of_login.get(u.login)
        if uid:
            self._by_id[uid] = u

    def delete(self, uid: int) -> None:
        u = self._by_id.pop(uid, None)
        if u:
            self._id_of_login.pop(u.login, None)

# --------- SALAS ----------
class SalaDAORAM(SalaDAO):
    def __init__(self):
        self._salas: Dict[int, Sala] = {}
        self._next_id = 1

    def add(self, s: Sala) -> Sala:
        s.sala_id = self._next_id
        self._salas[s.sala_id] = s
        self._next_id += 1
        return s

    def get_by_id(self, sala_id: int) -> Optional[Sala]:
        return self._salas.get(sala_id)

    def list_all(self) -> Iterable[Sala]:
        return list(self._salas.values())

    def delete(self, sala_id: int) -> bool:
        return self._salas.pop(sala_id, None) is not None

# --------- RESERVAS ----------
class ReservaDAORAM(ReservaDAO):
    def __init__(self):
        self._reservas: Dict[int, Reserva] = {}
        self._next_id = 1

    def add(self, r: Reserva) -> Reserva:
        r.reserva_id = self._next_id
        self._reservas[r.reserva_id] = r
        self._next_id += 1
        return r

    def get_by_id(self, rid: int) -> Optional[Reserva]:
        return self._reservas.get(rid)

    def list_all(self) -> Iterable[Reserva]:
        return list(self._reservas.values())

    def list_by_sala_data(self, sala_id: int, data: str) -> List[Reserva]:
        return [
            r for r in self._reservas.values()
            if r.sala.sala_id == sala_id and r.data == data and r.status == 'ativa'
        ]

    def update(self, r: Reserva) -> None:
        if r.reserva_id in self._reservas:
            self._reservas[r.reserva_id] = r

    def delete(self, rid: int) -> None:
        self._reservas.pop(rid, None)
