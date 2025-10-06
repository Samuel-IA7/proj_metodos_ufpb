# main.py — SEM opções de relatório
from controller import FacadeSingletonController
from exceptions import *
from models import Usuario

def menu_usuario(controller: FacadeSingletonController, usuario_logado: Usuario):
    while True:
        print("\n--- Menu do Usuário ---")
        print("1. Consultar disponibilidade por data")
        print("2. Listar minhas reservas")
        print("3. Criar reserva")
        print("4. Cancelar minha reserva")
        print("5. Desfazer última ação")
        print("6. Refazer última ação")
        print("7. Sair para o menu principal")
        op = input("Opção: ").strip()

        try:
            if op == '1':
                data = input("Data (AAAA-MM-DD): ").strip()
                disp = controller.consultar_disponibilidade(data)
                print("\nDisponibilidade:")
                if not disp:
                    print("Nenhuma sala cadastrada.")
                else:
                    for sala_nome, blocos in disp.items():
                        print(f"- {sala_nome}: {', '.join(blocos) if blocos else 'Livre o dia todo'}")

            elif op == '2':
                reservas = controller.listar_minhas_reservas(usuario_logado)
                if not reservas:
                    print("\nVocê não possui reservas.")
                else:
                    print("\nMinhas reservas:")
                    for r in reservas:
                        print(f"ID {r.reserva_id} | Sala: {r.sala.nome} | {r.data} {r.hora_inicio}-{r.hora_fim} | Status: {r.status}")

            elif op == '3':
                sala_id = int(input("ID da sala: ").strip())
                data = input("Data (AAAA-MM-DD): ").strip()
                h_ini = input("Hora início (HH:MM): ").strip()
                h_fim = input("Hora fim (HH:MM): ").strip()
                r = controller.cadastrar_reserva(usuario_logado, sala_id, data, h_ini, h_fim)
                print(f"\n✅ Reserva criada! ID {r.reserva_id} | Sala {r.sala.nome} | {r.data} {r.hora_inicio}-{r.hora_fim}")

            elif op == '4':
                rid = int(input("ID da reserva: ").strip())
                r = controller.cancelar_reserva(rid, usuario_logado)
                print(f"\n✅ Reserva {r.reserva_id} cancelada.")

            elif op == '5':
                print(controller.desfazer())

            elif op == '6':
                print(controller.refazer())

            elif op == '7':
                break
            else:
                print("❌ Opção inválida.")

        except Exception as e:
            print(f"\nErro: {e}")

def menu_admin(controller: FacadeSingletonController, usuario_logado: Usuario):
    while True:
        print("\n=== Menu do Administrador ===")
        print("1. Cadastrar sala")
        print("2. Excluir sala")
        print("3. Listar salas")
        print("4. Listar usuários")
        print("5. Bloquear usuário")
        print("6. Gerar relatório de uso das salas (contagem por sala)")
        print("7. Listar reservas por usuário")
        print("8. Consultar disponibilidade por data")
        print("9. Desfazer última ação")
        print("10. Refazer última ação")
        print("11. Definir estratégia de conflito (estrito/leniente)")
        print("12. Sair para o menu principal")
        op = input("Opção: ").strip()

        try:
            if op == '1':
                nome = input("Nome da sala: ").strip()
                capacidade = int(input("Capacidade: ").strip())
                recursos_in = input("Recursos (separados por vírgula): ").strip()
                recursos = [r.strip() for r in recursos_in.split(",")] if recursos_in else []
                s = controller.admin_cadastrar_sala(usuario_logado, nome, capacidade, recursos)
                print(f"\n✅ Sala cadastrada: {s.nome} (ID {s.sala_id})")

            elif op == '2':
                sala_id = int(input("ID da sala: ").strip())
                controller.admin_excluir_sala(usuario_logado, sala_id)
                print("\n✅ Sala excluída.")

            elif op == '3':
                salas = controller.admin_listar_salas(usuario_logado)
                if not salas:
                    print("\nNenhuma sala cadastrada.")
                else:
                    print("\nSalas cadastradas:")
                    for s in salas:
                        print(f"ID {s.sala_id} | {s.nome} | Cap: {s.capacidade} | Recursos: {', '.join(s.recursos) if s.recursos else '—'}")

            elif op == '4':
                usuarios = controller.admin_listar_usuarios(usuario_logado)
                print("\nUsuários:")
                for u in usuarios:
                    status = "BLOQUEADO" if getattr(u, 'bloqueado', False) else "ativo"
                    print(f"- {u.login} | {u.nome} | perfil={u.perfil} | {status}")

            elif op == '5':
                alvo = input("Login do usuário a bloquear: ").strip()
                controller.admin_bloquear_usuario(usuario_logado, alvo)
                print("\n✅ Usuário bloqueado.")

            elif op == '6':
                rel = controller.admin_gerar_relatorio_uso(usuario_logado)
                if not rel:
                    print("\nNenhuma utilização registrada.")
                else:
                    print("\nRelatório de uso (reservas ativas por sala):")
                    for sala, qtd in rel.items():
                        print(f"- {sala}: {qtd}")

            elif op == '7':
                login_alvo = input("Login do usuário: ").strip()
                reservas = controller.admin_listar_reservas_usuario(usuario_logado, login_alvo)
                if not reservas:
                    print("\nSem reservas para este usuário.")
                else:
                    print("\nReservas do usuário:")
                    for r in reservas:
                        print(f"ID {r.reserva_id} | Sala: {r.sala.nome} | {r.data} {r.hora_inicio}-{r.hora_fim} | Status: {r.status}")

            elif op == '8':
                data = input("Data (AAAA-MM-DD): ").strip()
                disp = controller.consultar_disponibilidade(data)
                print("\nDisponibilidade:")
                if not disp:
                    print("Nenhuma sala cadastrada.")
                else:
                    for sala_nome, blocos in disp.items():
                        print(f"- {sala_nome}: {', '.join(blocos) if blocos else 'Livre o dia todo'}")

            elif op == '9':
                print(controller.desfazer())

            elif op == '10':
                print(controller.refazer())

            elif op == '11':
                modo = input("Escolha a estratégia (estrito/leniente): ").strip().lower()
                msg = controller.definir_estrategia_conflito(modo)
                print(f"\n✅ {msg}")

            elif op == '12':
                break
            else:
                print("❌ Opção inválida.")

        except Exception as e:
            print(f"\nErro: {e}")

def main():
    controller = FacadeSingletonController.get_instance()

    while True:
        print("\n--- Sistema de Reservas (Menu Principal) ---")
        print("1. Fazer Login")
        print("2. Cadastrar Novo Usuário")
        print("3. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            login = input("Login: ")
            senha = input("Senha: ")
            try:
                sucesso, usuario_logado = controller.autenticar_usuario(login, senha)
                if sucesso:
                    print("\n✅ Login bem-sucedido!")
                    if usuario_logado.perfil == 'admin':
                        menu_admin(controller, usuario_logado)
                    else:
                        menu_usuario(controller, usuario_logado)
                else:
                    print("\n❌ Login ou senha inválidos.")
            except Exception as e:
                print(f"\nErro: {e}")

        elif opcao == '2':
            try:
                nome = input("Nome completo: ")
                login = input("Login: ")
                senha = input("Senha: ")
                controller.cadastrar_usuario(nome, login, senha)
                print("\n✅ Usuário cadastrado com sucesso! Agora você pode fazer login.")
            except Exception as e:
                print(f"\nErro: {e}")

        elif opcao == '3':
            print("\nSaindo do sistema. Até logo!")
            break
        else:
            print("\n❌ Opção inválida.")

if __name__ == "__main__":
    print("Bem-vindo ao sistema! Para começar, use o login padrão de administrador:")
    print("Login: admin | Senha: admin")
    main()
