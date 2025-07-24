# usermanager.py

from Entidade import Usuario

class UserManager:
    def __init__(self):
        self.usuarios = {}

    def cadastrar_usuario(self, nome, login, senha):
        if login in self.usuarios:
            return False, "Erro: login já existe."
        self.usuarios[login] = Usuario(nome, login, senha)
        return True, "Usuário cadastrado com sucesso."

    def listar_usuarios(self):
        return list(self.usuarios.values())

    def autenticar(self, login, senha):
        usuario = self.usuarios.get(login)
        if usuario and usuario.senha == senha:
            return True, usuario
        return False, None
