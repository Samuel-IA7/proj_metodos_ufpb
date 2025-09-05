# controller.py

from typing import Tuple, Optional, List, Dict
from models import Usuario, Reserva, Sala
from repository import RepositoryRAM
from managers import UserManager, ReservaManager, SalaManager
from exceptions import *

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
        
        self.repository = RepositoryRAM()
        self.user_manager = UserManager(self.repository)
        self.reserva_manager = ReservaManager(self.repository)
        self.sala_manager = SalaManager(self.repository)
        
        # Cria um usuário administrador padrão se não houver nenhum
        if not self.repository.listar_usuarios():
            self.user_manager.cadastrar_usuario("Admin Padrão", "admin", "admin", "admin")
    
    # --- Métodos de Usuário ---
    def cadastrar_usuario(self, nome: str, login: str, senha: str) -> Usuario:
        return self.user_manager.cadastrar_usuario(nome, login, senha)

    def autenticar_usuario(self, login: str, senha: str) -> Tuple[bool, Optional[Usuario]]:
        return self.user_manager.autenticar(login, senha)

    # --- Métodos de Reserva ---
    def cadastrar_reserva(self, usuario: Usuario, sala_id: int, data: str, hora_inicio: str, hora_fim: str) -> Reserva:
        sala = self.repository.buscar_sala_por_id(sala_id)
        if not sala:
            raise EntidadeNaoEncontradaException(f"Sala com ID {sala_id} não encontrada.")
        return self.reserva_manager.cadastrar_reserva(usuario, sala, data, hora_inicio, hora_fim)
        
    def cancelar_reserva(self, reserva_id: int, usuario_logado: Usuario) -> Reserva:
        return self.reserva_manager.cancelar_reserva(reserva_id, usuario_logado)
        
    def consultar_disponibilidade(self, data: str) -> Dict[str, List[str]]:
        return self.reserva_manager.consultar_disponibilidade(data)
        
    def listar_minhas_reservas(self, usuario: Usuario) -> List[Reserva]:
        todas = self.repository.listar_reservas()
        return [r for r in todas if r.usuario.login == usuario.login]

    # --- Métodos de ADMIN ---
    def _check_admin(self, usuario: Usuario):
        if not usuario or usuario.perfil != 'admin':
            raise PermissaoNegadaException("Ação permitida apenas para administradores.")
            
    def admin_cadastrar_sala(self, usuario_logado: Usuario, nome: str, capacidade: int, recursos: List[str]) -> Sala:
        self._check_admin(usuario_logado)
        return self.sala_manager.cadastrar_sala(nome, capacidade, recursos)

    def admin_excluir_sala(self, usuario_logado: Usuario, sala_id: int):
        self._check_admin(usuario_logado)
        self.sala_manager.excluir_sala(sala_id)

    def admin_listar_salas(self, usuario_logado: Usuario) -> List[Sala]:
        self._check_admin(usuario_logado)
        return self.sala_manager.listar_salas()
        
    def admin_listar_usuarios(self, usuario_logado: Usuario) -> List[Usuario]:
        self._check_admin(usuario_logado)
        return self.repository.listar_usuarios()
        
    def admin_bloquear_usuario(self, usuario_logado: Usuario, login_alvo: str):
        self._check_admin(usuario_logado)
        if usuario_logado.login == login_alvo:
            raise ValidarCamposException("Administrador não pode bloquear a si mesmo.")
        self.user_manager.bloquear_usuario(login_alvo)

    def admin_gerar_relatorio_uso(self, usuario_logado: Usuario) -> Dict[str, int]:
        self._check_admin(usuario_logado)
        return self.reserva_manager.gerar_relatorio_uso_salas()

    def admin_listar_reservas_usuario(self, usuario_logado: Usuario, login_alvo: str) -> List[Reserva]:
        self._check_admin(usuario_logado)
        return self.reserva_manager.listar_reservas_por_usuario(login_alvo)