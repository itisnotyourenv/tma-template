from dishka import Provider, Scope, from_context

from src.application.interfaces.auth import AuthService


class AuthProvider(Provider):
    scope = Scope.APP
    auth_service = from_context(provides=AuthService)
