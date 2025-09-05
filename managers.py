# managers.py

# managers.py

from typing import Tuple, Optional, List, Dict # <- ADICIONE Dict AQUI
# ... resto do código
from datetime import datetime
from models import Usuario, Reserva, Sala
from repository import RepositoryRAM
from exceptions import *

# --- Constantes de Regras de Negócio ---
LIMITE_RESERVAS_ATIVAS = 3
HORA_ABERTURA = 7
HORA_FECHAMENTO = 22

class UserManager:
    """Gerencia as operações relacionadas a usuários."""
    def __init__(self, repositorio: RepositoryRAM):
        self.repositorio = repositorio

    def cadastrar_usuario(self, nome: str, login: str, senha: str, perfil: str = 'usuario') -> Usuario:
        if not all([nome, login, senha, perfil]):
            raise ValidarCamposException("Nome, login, senha e perfil não podem ser vazios.")
        
        if self.repositorio.buscar_usuario_por_login(login):
            raise ValidarCamposException(f"O login '{login}' já está em uso.")
        
        novo_usuario = Usuario(nome=nome, login=login, senha=senha, perfil=perfil)
        return self.repositorio.cadastrar_usuario(novo_usuario)

    def autenticar(self, login: str, senha: str) -> Tuple[bool, Optional[Usuario]]:
        if not login or not senha:
            raise ValidarCamposException("Login e senha são obrigatórios.")
            
        usuario = self.repositorio.buscar_usuario_por_login(login)
        if usuario and usuario.senha == senha:
            return (True, usuario)
        return (False, None)
        
    def bloquear_usuario(self, login: str):
        usuario = self.repositorio.buscar_usuario_por_login(login)
        if not usuario:
            raise EntidadeNaoEncontradaException("Usuário não encontrado.")
        usuario.bloqueado = True

class SalaManager:
    """Gerencia as operações relacionadas a salas."""
    def __init__(self, repositorio: RepositoryRAM):
        self.repositorio = repositorio

    def cadastrar_sala(self, nome: str, capacidade: int, recursos: List[str]) -> Sala:
        if not nome or capacidade <= 0:
            raise ValidarCamposException("Nome e capacidade (maior que zero) são obrigatórios.")
        nova_sala = Sala(sala_id=0, nome=nome, capacidade=capacidade, recursos=recursos)
        return self.repositorio.cadastrar_sala(nova_sala)

    def excluir_sala(self, sala_id: int):
        if not self.repositorio.buscar_sala_por_id(sala_id):
            raise EntidadeNaoEncontradaException("Sala não encontrada.")
        self.repositorio.excluir_sala(sala_id)

    def listar_salas(self) -> List[Sala]:
        return self.repositorio.listar_salas()

class ReservaManager:
    """Gerencia as operações relacionadas a reservas."""
    def __init__(self, repositorio: RepositoryRAM):
        self.repositorio = repositorio

    def _validar_conflito(self, nova_reserva: Reserva):
        reservas_no_dia = self.repositorio.listar_reservas_por_sala_e_data(
            nova_reserva.sala.sala_id, nova_reserva.data
        )
        
        # Converte strings de tempo para objetos time para comparação
        novo_inicio = datetime.strptime(nova_reserva.hora_inicio, "%H:%M").time()
        novo_fim = datetime.strptime(nova_reserva.hora_fim, "%H:%M").time()

        for r_existente in reservas_no_dia:
            inicio_existente = datetime.strptime(r_existente.hora_inicio, "%H:%M").time()
            fim_existente = datetime.strptime(r_existente.hora_fim, "%H:%M").time()
            # Verifica se há qualquer sobreposição de horários
            if max(novo_inicio, inicio_existente) < min(novo_fim, fim_existente):
                raise ConflitoDeReservaException(
                    f"Conflito! A sala já está reservada das {r_existente.hora_inicio} às {r_existente.hora_fim}."
                )

    def cadastrar_reserva(self, usuario: Usuario, sala: Sala, data: str, hora_inicio: str, hora_fim: str) -> Reserva:
        # [RF014] Validação de usuário bloqueado
        if usuario.bloqueado:
            raise UsuarioBloqueadoException("Usuário bloqueado não pode realizar novas reservas.")
            
        # [RF015] Validação de horário de funcionamento
        h_inicio = int(hora_inicio.split(':')[0])
        h_fim = int(hora_fim.split(':')[0])
        if not (HORA_ABERTURA <= h_inicio < HORA_FECHAMENTO and HORA_ABERTURA < h_fim <= HORA_FECHAMENTO):
             raise ValidarCamposException(f"Reservas permitidas apenas entre {HORA_ABERTURA}:00 e {HORA_FECHAMENTO}:00.")

        # [RF013] Validação de limite de reservas ativas
        reservas_ativas_usuario = self.repositorio.listar_reservas_ativas_por_usuario(usuario)
        if len(reservas_ativas_usuario) >= LIMITE_RESERVAS_ATIVAS:
            raise LimiteDeReservasException(f"Limite de {LIMITE_RESERVAS_ATIVAS} reservas ativas por usuário atingido.")
        
        nova_reserva = Reserva(reserva_id=0, usuario=usuario, sala=sala, data=data, hora_inicio=hora_inicio, hora_fim=hora_fim)
        
        # [RF004] Validação de disponibilidade (conflito)
        self._validar_conflito(nova_reserva)
        
        # [RF009] Simulação de Notificação
        print(f"\n[NOTIFICAÇÃO] Olá, {usuario.nome}! Sua reserva da sala '{sala.nome}' para {data} foi confirmada.")

        return self.repositorio.cadastrar_reserva(nova_reserva)
    
    def cancelar_reserva(self, reserva_id: int, usuario: Usuario) -> Reserva:
        reserva = self.repositorio.buscar_reserva_por_id(reserva_id)
        if not reserva:
            raise EntidadeNaoEncontradaException("Reserva não encontrada.")
        
        # Permite cancelar se for o dono da reserva OU se for admin
        if reserva.usuario.login != usuario.login and usuario.perfil != 'admin':
            raise PermissaoNegadaException("Você só pode cancelar suas próprias reservas.")
            
        reserva.status = 'cancelada'
        return reserva

    def consultar_disponibilidade(self, data: str) -> Dict[str, List[str]]:
        """Retorna um dicionário de salas e seus horários ocupados para uma data."""
        salas = self.repositorio.listar_salas()
        disponibilidade = {sala.nome: [] for sala in salas}
        
        reservas = self.repositorio.listar_reservas()
        for r in reservas:
            if r.data == data and r.status == 'ativa':
                disponibilidade[r.sala.nome].append(f"{r.hora_inicio}-{r.hora_fim}")
        return disponibilidade
        
    def listar_reservas_por_usuario(self, login: str) -> List[Reserva]:
        usuario = self.repositorio.buscar_usuario_por_login(login)
        if not usuario:
            raise EntidadeNaoEncontradaException("Usuário não encontrado.")
        
        todas_reservas = self.repositorio.listar_reservas()
        return [r for r in todas_reservas if r.usuario.login == login]

    def gerar_relatorio_uso_salas(self) -> Dict[str, int]:
        """Gera um relatório simples de contagem de reservas por sala."""
        relatorio = {}
        reservas = [r for r in self.repositorio.listar_reservas() if r.status == 'ativa']
        for r in reservas:
            relatorio[r.sala.nome] = relatorio.get(r.sala.nome, 0) + 1
        return relatorio