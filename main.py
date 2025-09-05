# main.py (Versão Interativa Completa)

from controller import FacadeSingletonController
from exceptions import *
from models import Usuario
from typing import Optional

# Funções de interface para USUÁRIO LOGADO
def menu_usuario(controller: FacadeSingletonController, usuario_logado: Usuario):
    while True:
        print("\n--- Menu do Usuário ---")
        print(f"Logado como: {usuario_logado.nome}")
        print("1. Fazer Nova Reserva")
        print("2. Minhas Reservas")
        print("3. Cancelar Reserva")
        print("4. Consultar Disponibilidade de Salas")
        print("5. Logout")
        
        opcao = input("Escolha uma opção: ")

        try:
            if opcao == '1':
                print("\n--- Salas Disponíveis ---")
                salas = controller.sala_manager.listar_salas()
                for sala in salas: print(sala)
                sala_id = int(input("Digite o ID da sala desejada: "))
                data = input("Digite a data (DD/MM/AAAA): ")
                hora_inicio = input("Digite a hora de início (HH:MM): ")
                hora_fim = input("Digite a hora de término (HH:MM): ")
                controller.cadastrar_reserva(usuario_logado, sala_id, data, hora_inicio, hora_fim)
                print("\n✅ Reserva efetuada com sucesso!")

            elif opcao == '2':
                print("\n--- Minhas Reservas ---")
                reservas = controller.listar_minhas_reservas(usuario_logado)
                if not reservas: print("Você não possui reservas.")
                for r in reservas: print(r)
            
            elif opcao == '3':
                reserva_id = int(input("Digite o ID da reserva a ser cancelada: "))
                controller.cancelar_reserva(reserva_id, usuario_logado)
                print("\n✅ Reserva cancelada com sucesso!")

            elif opcao == '4':
                data = input("Digite a data para consulta (DD/MM/AAAA): ")
                disponibilidade = controller.consultar_disponibilidade(data)
                print("\n--- Disponibilidade para", data, "---")
                for sala, horarios in disponibilidade.items():
                    print(f"Sala: {sala} - Horários Ocupados: {', '.join(horarios) if horarios else 'Nenhum'}")

            elif opcao == '5':
                print("\nLogout efetuado.")
                return # Sai do menu do usuário e volta para o menu principal
            else:
                print("\n❌ Opção inválida.")
        
        except (ValidarCamposException, PermissaoNegadaException, EntidadeNaoEncontradaException,
                ConflitoDeReservaException, LimiteDeReservasException, UsuarioBloqueadoException) as e:
            print(f"\n❌ ERRO: {e}")
        except ValueError:
            print("\n❌ ERRO: Entrada inválida. Certifique-se de digitar números onde for solicitado.")
        except Exception as e:
            print(f"\n❌ Ocorreu um erro inesperado: {e}")

# Funções de interface para ADMINISTRADOR LOGADO
def menu_admin(controller: FacadeSingletonController, usuario_logado: Usuario):
    while True:
        print("\n--- Menu do Administrador ---")
        print(f"Logado como: {usuario_logado.nome} (Admin)")
        print("\n-- Gerenciar Reservas --")
        print("1. Ver Todas as Reservas de um Usuário")
        print("\n-- Gerenciar Salas --")
        print("2. Cadastrar Nova Sala")
        print("3. Listar Todas as Salas")
        print("4. Excluir Sala")
        print("\n-- Gerenciar Usuários --")
        print("5. Listar Todos os Usuários")
        print("6. Bloquear Usuário")
        print("\n-- Relatórios --")
        print("7. Relatório de Utilização de Salas")
        print("\n8. Logout")
        
        opcao = input("Escolha uma opção: ")
        
        try:
            if opcao == '1':
                login_alvo = input("Digite o login do usuário para ver as reservas: ")
                reservas = controller.admin_listar_reservas_usuario(usuario_logado, login_alvo)
                if not reservas: print(f"Nenhuma reserva encontrada para o usuário '{login_alvo}'.")
                for r in reservas: print(r)

            elif opcao == '2':
                nome = input("Nome da sala: ")
                capacidade = int(input("Capacidade da sala: "))
                recursos = input("Recursos (separados por vírgula): ").split(',')
                controller.admin_cadastrar_sala(usuario_logado, nome, capacidade, [r.strip() for r in recursos])
                print("\n✅ Sala cadastrada com sucesso!")

            elif opcao == '3':
                salas = controller.admin_listar_salas(usuario_logado)
                for s in salas: print(s)

            elif opcao == '4':
                sala_id = int(input("Digite o ID da sala a ser excluída: "))
                controller.admin_excluir_sala(usuario_logado, sala_id)
                print("\n✅ Sala excluída com sucesso!")

            elif opcao == '5':
                usuarios = controller.admin_listar_usuarios(usuario_logado)
                for u in usuarios: print(u)

            elif opcao == '6':
                login_alvo = input("Digite o login do usuário a ser bloqueado: ")
                controller.admin_bloquear_usuario(usuario_logado, login_alvo)
                print(f"\n✅ Usuário '{login_alvo}' bloqueado com sucesso.")

            elif opcao == '7':
                relatorio = controller.admin_gerar_relatorio_uso(usuario_logado)
                print("\n--- Relatório de Reservas Ativas por Sala ---")
                for sala, count in relatorio.items():
                    print(f"Sala: {sala} - Total de Reservas: {count}")
            
            elif opcao == '8':
                print("\nLogout efetuado.")
                return
            else:
                print("\n❌ Opção inválida.")

        except (ValidarCamposException, PermissaoNegadaException, EntidadeNaoEncontradaException) as e:
            print(f"\n❌ ERRO: {e}")
        except ValueError:
            print("\n❌ ERRO: Entrada inválida. Certifique-se de digitar números onde for solicitado.")
        except Exception as e:
            print(f"\n❌ Ocorreu um erro inesperado: {e}")

# Menu Principal (Deslogado)
def main():
    controller = FacadeSingletonController.get_instance()
    
    while True:
        print("\n--- Sistema de Reservas (Menu Principal) ---")
        print("1. Fazer Login")
        print("2. Cadastrar Novo Usuário")
        print("3. Sair")
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            try:
                login = input("Login: ")
                senha = input("Senha: ")
                sucesso, usuario_logado = controller.autenticar_usuario(login, senha)
                
                if sucesso:
                    print(f"\n✅ Login bem-sucedido!")
                    if usuario_logado.perfil == 'admin':
                        menu_admin(controller, usuario_logado)
                    else:
                        menu_usuario(controller, usuario_logado)
                else:
                    print("\n❌ Login ou senha inválidos.")
            except Exception as e:
                print(f"\n❌ ERRO: {e}")

        elif opcao == '2':
            try:
                nome = input("Nome completo: ")
                login = input("Login: ")
                senha = input("Senha: ")
                controller.cadastrar_usuario(nome, login, senha)
                print("\n✅ Usuário cadastrado com sucesso! Agora você pode fazer login.")
            except Exception as e:
                print(f"\n❌ ERRO: {e}")

        elif opcao == '3':
            print("\nSaindo do sistema. Até logo!")
            break
        else:
            print("\n❌ Opção inválida.")


if __name__ == "__main__":
    print("Bem-vindo ao sistema! Para começar, use o login padrão de administrador:")
    print("Login: admin | Senha: admin")
    main()