# controller.py — Memento + Strategy + Logger Adapter (SEM Template Method)
from typing import Tuple, Optional, List, Dict
from models import Usuario, Reserva, Sala
from managers import UserManager, ReservaManager, SalaManager
from exceptions import *
from dao_factory import RAMDAOFactory
from memento import HistoryService
from strategy_conflict import LenientConflictStrategy, StrictConflictStrategy
from adapter_logging import PythonLoggingAdapter

class FacadeSingletonController:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if FacadeSingletonController._instance is not None:
            raise Exception("Esta é uma classe Singleton! Use o método get_instance().")

        factory = RAMDAOFactory()
        self.user_dao = factory.users()
        self.sala_dao = factory.salas()
        self.reserva_dao = factory.reservas()

        # Adapter de logging
        self.logger = PythonLoggingAdapter("app")

        # Managers recebem logger
        self.user_manager = UserManager(self.user_dao, logger=self.logger)
        self.sala_manager = SalaManager(self.sala_dao, logger=self.logger)
        self.reserva_manager = ReservaManager(self.reserva_dao, self.user_dao, self.sala_dao, logger=self.logger)

        # Caretaker do Memento (histórico de estados)
        self.history = HistoryService(capacity=100)

        # Admin padrão
        if not list(self.user_manager.listar_usuarios()):
            self.user_manager.cadastrar_usuario("Admin Padrão", "admin", "admin", "admin")

    # --- Usuário ---
    def cadastrar_usuario(self, nome: str, login: str, senha: str) -> Usuario:
        return self.user_manager.cadastrar_usuario(nome, login, senha)

    def autenticar_usuario(self, login: str, senha: str) -> Tuple[bool, Optional[Usuario]]:
        return self.user_manager.autenticar(login, senha)

    # --- Reserva ---
    def cadastrar_reserva(self, usuario: Usuario, sala_id: int, data: str, hora_inicio: str, hora_fim: str) -> Reserva:
        sala = self.sala_dao.get_by_id(sala_id)
        if not sala:
            raise EntidadeNaoEncontradaException(f"Sala com ID {sala_id} não encontrada.")
        return self.reserva_manager.cadastrar_reserva(usuario, sala, data, hora_inicio, hora_fim, history=self.history)

    def cancelar_reserva(self, reserva_id: int, usuario_logado: Usuario) -> Reserva:
        self.history.push(self.reserva_manager._snapshot())
        return self.reserva_manager.cancelar_reserva(reserva_id, usuario_logado)

    def consultar_disponibilidade(self, data: str) -> Dict[str, List[str]]:
        return self.reserva_manager.consultar_disponibilidade(data)

    def listar_minhas_reservas(self, usuario: Usuario) -> List[Reserva]:
        return [r for r in self.reserva_dao.list_all() if r.usuario.login == usuario.login]

    # --- ADMIN ---
    def _check_admin(self, usuario: Usuario):
        if not usuario or usuario.perfil != 'admin':
            raise PermissaoNegadaException("Ação permitida apenas para administradores.")

    def admin_cadastrar_sala(self, usuario_logado: Usuario, nome: str, capacidade: int, recursos: List[str]) -> Sala:
        self._check_admin(usuario_logado)
        self.history.push(self.reserva_manager._snapshot())
        return self.sala_manager.cadastrar_sala(nome, capacidade, recursos)

    def admin_excluir_sala(self, usuario_logado: Usuario, sala_id: int):
        self._check_admin(usuario_logado)
        self.history.push(self.reserva_manager._snapshot())
        self.sala_manager.excluir_sala(sala_id)

    def admin_listar_salas(self, usuario_logado: Usuario) -> List[Sala]:
        self._check_admin(usuario_logado)
        return self.sala_manager.listar_salas()

    def admin_listar_usuarios(self, usuario_logado: Usuario) -> List[Usuario]:
        self._check_admin(usuario_logado)
        return self.user_manager.listar_usuarios()

    def admin_bloquear_usuario(self, usuario_logado: Usuario, login_alvo: str):
        self._check_admin(usuario_logado)
        if usuario_logado.login == login_alvo:
            raise ValidarCamposException("Administrador não pode bloquear a si mesmo.")
        self.history.push(self.reserva_manager._snapshot())
        self.user_manager.bloquear_usuario(login_alvo)

    def admin_gerar_relatorio_uso(self, usuario_logado: Usuario) -> Dict[str, int]:
        self._check_admin(usuario_logado)
        return self.reserva_manager.gerar_relatorio_uso_salas()

    def admin_listar_reservas_usuario(self, usuario_logado: Usuario, login_alvo: str) -> List[Reserva]:
        self._check_admin(usuario_logado)
        return self.reserva_manager.listar_reservas_por_usuario(login_alvo)

    # --- MEMENTO: Undo/Redo ---
    def desfazer(self) -> str:
        snap = self.history.undo(self.reserva_manager._snapshot())
        if not snap:
            return "Nada para desfazer."
        self.reserva_manager.restore_from(snap)
        return "Operação desfeita com sucesso."

    def refazer(self) -> str:
        snap = self.history.redo(self.reserva_manager._snapshot())
        if not snap:
            return "Nada para refazer."
        self.reserva_manager.restore_from(snap)
        return "Operação refeita com sucesso."

    # --- STRATEGY: alternar política de conflito ---
    def definir_estrategia_conflito(self, modo: str) -> str:
        if modo.lower().startswith("leni"):
            self.reserva_manager.strategy = LenientConflictStrategy()
            return "Estratégia de conflito definida para: leniente (margem 5min)."
        else:
            self.reserva_manager.strategy = StrictConflictStrategy()
            return "Estratégia de conflito definida para: estrito (sem sobreposição)."
