class Usuario:
    def init(self, nome: str, login: str, senha: str):
        self.nome = nome
        self.login = login
        self.senha = senha

    def str(self):
        return f"Nome: {self.nome} | Login: {self.login}"

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "login": self.login,
            "senha": self.senha
        }

    @classmethod
    def from_dict(cls, dados: dict):
        return cls(dados["nome"], dados["login"], dados["senha"])