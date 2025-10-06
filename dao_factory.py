# dao_factory.py (Abstract Factory)
from abc import ABC, abstractmethod
from repository import UserDAO, SalaDAO, ReservaDAO
from infra_ram import UserDAORAM, SalaDAORAM, ReservaDAORAM

class DAOFactory(ABC):
    @abstractmethod
    def users(self) -> UserDAO: ...
    @abstractmethod
    def salas(self) -> SalaDAO: ...
    @abstractmethod
    def reservas(self) -> ReservaDAO: ...

class RAMDAOFactory(DAOFactory):
    def __init__(self):
        self._user = UserDAORAM()
        self._sala = SalaDAORAM()
        self._reserva = ReservaDAORAM()

    def users(self) -> UserDAO: return self._user
    def salas(self) -> SalaDAO: return self._sala
    def reservas(self) -> ReservaDAO: return self._reserva
