# exceptions.py

class ValidarCamposException(Exception):
    """Exceção para erros de validação de campos genéricos."""
    pass

class PermissaoNegadaException(Exception):
    """Exceção para quando um usuário tenta executar uma ação de administrador."""
    pass

class EntidadeNaoEncontradaException(Exception):
    """Exceção para quando uma sala, usuário ou reserva não é encontrado."""
    pass

class ConflitoDeReservaException(Exception):
    """Exceção para quando há um conflito de horário em uma reserva."""
    pass

class LimiteDeReservasException(Exception):
    """Exceção para quando um usuário atinge seu limite de reservas ativas."""
    pass

class UsuarioBloqueadoException(Exception):
    """Exceção para quando um usuário bloqueado tenta fazer uma reserva."""
    pass