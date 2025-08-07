from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def salvar(self, usuarios: dict):
        pass

    @abstractmethod
    def carregar(self) -> dict:
        pass