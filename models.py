# models.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class Usuario:
    """Representa o modelo de um usuário no sistema."""
    nome: str
    login: str
    senha: str
    perfil: str = 'usuario'  # Pode ser 'usuario' ou 'admin'
    bloqueado: bool = False

    def __str__(self):
        status = "Bloqueado" if self.bloqueado else "Ativo"
        return f"Usuário(nome='{self.nome}', login='{self.login}', perfil='{self.perfil}', status='{status}')"

@dataclass
class Sala:
    """Representa o modelo de uma sala de estudos."""
    sala_id: int
    nome: str
    capacidade: int
    recursos: List[str] = field(default_factory=list)

    def __str__(self):
        return f"Sala ID: {self.sala_id} | Nome: {self.nome} | Capacidade: {self.capacidade} | Recursos: {', '.join(self.recursos)}"

@dataclass
class Reserva:
    """Representa o modelo de uma reserva de sala."""
    reserva_id: int
    usuario: Usuario
    sala: Sala
    data: str
    hora_inicio: str
    hora_fim: str
    status: str = 'ativa' # Pode ser 'ativa', 'cancelada'

    def __str__(self):
        return (f"Reserva ID: {self.reserva_id} | Sala: {self.sala.nome} | "
                f"Data: {self.data} | Horário: {self.hora_inicio}-{self.hora_fim} | "
                f"Usuário: {self.usuario.nome} | Status: {self.status.upper()}")