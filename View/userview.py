# userview.py

from Control import UserManager

class UserView:
    def __init__(self):
        self.manager = UserManager()

    def exibir_menu(self):
        while True:
            print("\n--- MENU ---")
            print("1. Cadastrar usuário")
            print("2. Listar usuários")
            print("3. Fazer login")
            print("0. Sair")
            opcao = input("Escolha uma opção: ")

            if opcao == "1":
                self.cadastrar_usuario()
            elif opcao == "2":
                self.listar_usuarios()
            elif opcao == "3":
                self.fazer_login()
            elif opcao == "0":
                print("Saindo...")
                break
            else:
                print("Opção inválida.")

    def cadastrar_usuario(self):
        nome = input("Nome: ")
        login = input("Login: ")
        senha = input("Senha: ")
        sucesso, msg = self.manager.cadastrar_usuario(nome, login, senha)
        print(msg)

    def listar_usuarios(self):
        usuarios = self.manager.listar_usuarios()
        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return
        print("Usuários cadastrados:")
        for u in usuarios:
            print(u)

    def fazer_login(self):
        login = input("Login: ")
        senha = input("Senha: ")
        sucesso, usuario = self.manager.autenticar(login, senha)
        if sucesso:
            print(f"Login bem-sucedido. Bem-vindo(a), {usuario.nome}!")
        else:
            print("Login ou senha incorretos.")
