class AppException(Exception):
    """Базовое исключение для всего приложения"""
    pass


class UserAlreadyExistsError(AppException):
    """Пользователь с таким email уже существует"""
    pass


class InvalidCredentialsError(AppException):
    """Неверный email или пароль"""
    pass


class GameNotFoundError(AppException):
    """Игра не найдена"""
    pass


class GameAlreadyExistsError(AppException):
    """Игра уже была добавлена"""
    pass

class WishlistAlreadyExistsError(AppException):
    """Эта игра уже есть в вишлисте пользователя"""
    pass

class WishlistNotFoundError(AppException):
    """Запись в вишлисте не найдена"""
    pass

class AccessDeniedError(AppException):
    """Попытка изменить чужой вишлист"""
    pass