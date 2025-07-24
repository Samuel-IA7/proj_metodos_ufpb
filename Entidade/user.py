# user.py

class Usuario:
    def __init__(self, nome, login, senha):
        self.nome = nome
        self.login = login
        self.senha = senha

    def __str__(self):
        return f"Nome: {self.nome} | Login: {self.login}"
