from Entidade import Usuario
from excecoes import ValidaCampoException
from excecoes import Repository  # Interface
from typing import Tuple, Optional
from Entidade.user import Usuario
from persistencia.repository_file import RepositoryFile
from excecoes import ValidaCampoException


class UserManager:
    def init(self, persistencia: Repository):
        self.persistencia = persistencia
        self.usuarios: dict[str, Usuario] = self.persistencia.carregar_dados() or {}

    def cadastrar_usuario(self, nome: str, login: str, senha: str) -> Tuple[bool, str]:
        if not nome or not login or not senha:
            raise ValidaCampoException("Todos os campos devem ser preenchidos.")

        if login in self.usuarios:
            return False, "Erro: login já existe."

        self.usuarios[login] = Usuario(nome, login, senha)
        self.persistencia.salvar_dados(self.usuarios)
        return True, "Usuário cadastrado com sucesso."

    def listar_usuarios(self) -> list[Usuario]:
        return list(self.usuarios.values())

    def autenticar(self, login: str, senha: str) -> Tuple[bool, Optional[Usuario]]:
        usuario = self.usuarios.get(login)
        if usuario and usuario.senha == senha:
            return True, usuario
        return False, None