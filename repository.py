# repository.py

from typing import Dict, List, Optional
from models import Usuario, Reserva, Sala

# Implementação em Memória (RepositoryRAM)
# A interface (classe abstrata Repository) foi omitida por brevidade,
# mas a implementação abaixo serve como a camada de dados.

class RepositoryRAM:
    """Implementação do repositório que salva os dados em memória."""

    def __init__(self):
        # Usuários
        self._usuarios: Dict[str, Usuario] = {}
        
        # Salas
        self._salas: Dict[int, Sala] = {}
        self._sala_id_counter = 1
        
        # Reservas
        self._reservas: Dict[int, Reserva] = {}
        self._reserva_id_counter = 1

    # --- Métodos de Usuário ---
    def cadastrar_usuario(self, usuario: Usuario) -> Usuario:
        self._usuarios[usuario.login] = usuario
        return usuario

    def buscar_usuario_por_login(self, login: str) -> Optional[Usuario]:
        return self._usuarios.get(login)

    def listar_usuarios(self) -> List[Usuario]:
        return list(self._usuarios.values())

    # --- Métodos de Sala ---
    def cadastrar_sala(self, sala: Sala) -> Sala:
        sala.sala_id = self._sala_id_counter
        self._salas[sala.sala_id] = sala
        self._sala_id_counter += 1
        return sala

    def buscar_sala_por_id(self, sala_id: int) -> Optional[Sala]:
        return self._salas.get(sala_id)

    def listar_salas(self) -> List[Sala]:
        return list(self._salas.values())

    def excluir_sala(self, sala_id: int) -> bool:
        if sala_id in self._salas:
            del self._salas[sala_id]
            return True
        return False
        
    # --- Métodos de Reserva ---
    def cadastrar_reserva(self, reserva: Reserva) -> Reserva:
        reserva.reserva_id = self._reserva_id_counter
        self._reservas[reserva.reserva_id] = reserva
        self._reserva_id_counter += 1
        return reserva

    def buscar_reserva_por_id(self, reserva_id: int) -> Optional[Reserva]:
        return self._reservas.get(reserva_id)

    def listar_reservas(self) -> List[Reserva]:
        return list(self._reservas.values())
        
    def listar_reservas_por_sala_e_data(self, sala_id: int, data: str) -> List[Reserva]:
        return [r for r in self._reservas.values() if r.sala.sala_id == sala_id and r.data == data and r.status == 'ativa']
        
    def listar_reservas_ativas_por_usuario(self, usuario: Usuario) -> List[Reserva]:
        return [r for r in self._reservas.values() if r.usuario.login == usuario.login and r.status == 'ativa']