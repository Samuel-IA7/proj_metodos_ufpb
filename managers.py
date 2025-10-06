# managers.py — negócio com Memento + Strategy + Logger (Adapter)
from typing import Tuple, Optional, List, Dict
from datetime import datetime
from copy import deepcopy
from models import Usuario, Reserva, Sala
from repository import UserDAO, SalaDAO, ReservaDAO
from exceptions import *
from memento import ReservationSnapshot
from strategy_conflict import ConflictStrategy, StrictConflictStrategy
from adapter_logging import AppLogger  # <- NOVO

LIMITE_RESERVAS_ATIVAS = 3
HORA_ABERTURA = 7
HORA_FECHAMENTO = 22

# ---------- USER ----------
class UserManager:
    def __init__(self, user_dao: UserDAO, logger: AppLogger | None = None):
        self.user_dao = user_dao
        self.logger = logger

    def cadastrar_usuario(self, nome: str, login: str, senha: str, perfil: str = 'usuario') -> Usuario:
        if not all([nome, login, senha, perfil]):
            raise ValidarCamposException("Nome, login, senha e perfil não podem ser vazios.")
        if self.user_dao.get_by_login(login):
            raise ValidarCamposException(f"O login '{login}' já está em uso.")
        novo = Usuario(nome=nome, login=login, senha=senha, perfil=perfil)
        self.user_dao.add(novo)
        if self.logger: self.logger.info(f"Usuário cadastrado: {login}")
        return novo

    def autenticar(self, login: str, senha: str) -> Tuple[bool, Optional[Usuario]]:
        if not login or not senha:
            raise ValidarCamposException("Login e senha são obrigatórios.")
        u = self.user_dao.get_by_login(login)
        ok = bool(u and u.senha == senha)
        if self.logger: self.logger.info(f"Tentativa de login: {login} -> {'OK' if ok else 'FALHOU'}")
        return (True, u) if ok else (False, None)

    def bloquear_usuario(self, login: str):
        u = self.user_dao.get_by_login(login)
        if not u:
            raise EntidadeNaoEncontradaException("Usuário não encontrado.")
        u.bloqueado = True
        self.user_dao.update(u)
        if self.logger: self.logger.warning(f"Usuário bloqueado: {login}")

    def listar_usuarios(self) -> List[Usuario]:
        return list(self.user_dao.list_all())

# ---------- SALA ----------
class SalaManager:
    def __init__(self, sala_dao: SalaDAO, logger: AppLogger | None = None):
        self.sala_dao = sala_dao
        self.logger = logger

    def cadastrar_sala(self, nome: str, capacidade: int, recursos: List[str]) -> Sala:
        if not nome or capacidade <= 0:
            raise ValidarCamposException("Nome e capacidade (maior que zero) são obrigatórios.")
        nova = Sala(sala_id=0, nome=nome, capacidade=capacidade, recursos=recursos)
        s = self.sala_dao.add(nova)
        if self.logger: self.logger.info(f"Sala cadastrada: {s.nome} (ID {s.sala_id})")
        return s

    def excluir_sala(self, sala_id: int):
        if not self.sala_dao.get_by_id(sala_id):
            raise EntidadeNaoEncontradaException("Sala não encontrada.")
        self.sala_dao.delete(sala_id)
        if self.logger: self.logger.warning(f"Sala excluída: ID {sala_id}")

    def listar_salas(self) -> List[Sala]:
        return list(self.sala_dao.list_all())

# ---------- RESERVA ----------
class ReservaManager:
    def __init__(self, reserva_dao: ReservaDAO, user_dao: UserDAO, sala_dao: SalaDAO,
                 strategy: ConflictStrategy | None = None, logger: AppLogger | None = None):
        self.rdao = reserva_dao
        self.udao = user_dao
        self.sdao = sala_dao
        self.strategy: ConflictStrategy = strategy or StrictConflictStrategy()
        self.logger = logger

    # ------- MEMENTO: Originator -------
    def _snapshot(self) -> ReservationSnapshot:
        return ReservationSnapshot(
            users=deepcopy(list(self.udao.list_all())),
            salas=deepcopy(list(self.sdao.list_all())),
            reservas=deepcopy(list(self.rdao.list_all()))
        )

    def restore_from(self, snapshot: ReservationSnapshot):
        self.udao.replace_all(deepcopy(snapshot.users))
        self.sdao.replace_all(deepcopy(snapshot.salas))
        self.rdao.replace_all(deepcopy(snapshot.reservas))
        if self.logger: self.logger.info("Estado restaurado (Undo/Redo aplicado).")

    # ------- Conflito usando Strategy -------
    def _validar_conflito(self, nova: Reserva):
        reservas_no_dia = self.rdao.list_by_sala_data(nova.sala.sala_id, nova.data)
        self.strategy.validar(nova, reservas_no_dia)

    # ------- Regras de reserva -------
    def cadastrar_reserva(self, usuario: Usuario, sala: Sala, data: str, hora_inicio: str, hora_fim: str, history=None) -> Reserva:
        if history is not None:
            history.push(self._snapshot())

        if usuario.bloqueado:
            raise UsuarioBloqueadoException("Usuário bloqueado não pode realizar novas reservas.")
        h_inicio = int(hora_inicio.split(':')[0]); h_fim = int(hora_fim.split(':')[0])
        if not (HORA_ABERTURA <= h_inicio < HORA_FECHAMENTO and HORA_ABERTURA < h_fim <= HORA_FECHAMENTO):
            raise ValidarCamposException(f"Reservas permitidas apenas entre {HORA_ABERTURA}:00 e {HORA_FECHAMENTO}:00.")
        reservas_ativas = [r for r in self.rdao.list_all() if r.usuario.login == usuario.login and r.status == 'ativa']
        if len(reservas_ativas) >= LIMITE_RESERVAS_ATIVAS:
            raise LimiteDeReservasException(f"Limite de {LIMITE_RESERVAS_ATIVAS} reservas ativas por usuário atingido.")

        nova = Reserva(reserva_id=0, usuario=usuario, sala=sala, data=data, hora_inicio=hora_inicio, hora_fim=hora_fim)
        self._validar_conflito(nova)

        if self.logger: self.logger.info(f"Reserva criada: user={usuario.login}, sala={sala.nome}, {data} {hora_inicio}-{hora_fim}")
        print(f"\n[NOTIFICAÇÃO] Olá, {usuario.nome}! Sua reserva da sala '{sala.nome}' para {data} foi confirmada.")
        return self.rdao.add(nova)

    def cancelar_reserva(self, reserva_id: int, usuario: Usuario) -> Reserva:
        r = self.rdao.get_by_id(reserva_id)
        if not r:
            raise EntidadeNaoEncontradaException("Reserva não encontrada.")
        if r.usuario.login != usuario.login and usuario.perfil != 'admin':
            raise PermissaoNegadaException("Você só pode cancelar suas próprias reservas.")
        r.status = 'cancelada'
        self.rdao.update(r)
        if self.logger: self.logger.warning(f"Reserva cancelada: id={r.reserva_id}, por={usuario.login}")
        return r

    def consultar_disponibilidade(self, data: str) -> Dict[str, List[str]]:
        salas = list(self.sdao.list_all())
        disponibilidade = {s.nome: [] for s in salas}
        for r in self.rdao.list_all():
            if r.data == data and r.status == 'ativa':
                disponibilidade[r.sala.nome].append(f"{r.hora_inicio}-{r.hora_fim}")
        return disponibilidade

    def listar_reservas_por_usuario(self, login: str) -> List[Reserva]:
        return [r for r in self.rdao.list_all() if r.usuario.login == login]

    def gerar_relatorio_uso_salas(self) -> Dict[str, int]:
        rel: Dict[str, int] = {}
        for r in self.rdao.list_all():
            if r.status == 'ativa':
                rel[r.sala.nome] = rel.get(r.sala.nome, 0) + 1
        return rel
