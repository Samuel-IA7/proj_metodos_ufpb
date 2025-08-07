class RepositoryRAM:
    def init(self):
        self._data = {}

    def salvar(self, login, usuario):
        self._data[login] = usuario

    def carregar_todos(self):
        return self._data

    def existe(self, login):
        return login in self._data