import json
import os
from persistencia.repository import Repository

class RepositoryFile(Repository):
    def init(self, caminho="usuarios.json"):
        self.caminho = caminho

    def salvar(self, usuarios):
        with open(self.caminho, "w") as f:
            json.dump({k: vars(v) for k, v in usuarios.items()}, f)

    def carregar(self):
        if not os.path.exists(self.caminho):
            return {}
        with open(self.caminho, "r") as f:
            data = json.load(f)
            from Entidade.user import Usuario
            return {k: Usuario(**v) for k, v in data.items()}