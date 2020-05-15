from .base import Base
from ..capsule.command import Command
from ..capsule.resource import Resource


class User(Base):

    name = 'user'
    info = 'User and profile management for cmd platform.'

    show_on_help = True

    def commands(self):
        return [
            Command(name='index', help_string='User app for imnicy.com', pro=True,
                    init='$scope.ui.addWarning(\'You should enter cmd <cmd>help app user</cmd> get more help.\');'),

            Command(name='signin', help_string='Login command.', aliases=['hi', 'login'],
                    example='user signin | user hi',
                    init='$scope.apps.user.signin();', command='lib.commands.user.login'),

            Command(name='signout', help_string='Logout command.', aliases=['bye', 'logout'],
                    example='user signout | user bye',
                    init='$scope.apps.user.signout();', command='lib.commands.user.logout'),

            Command(name='signup', help_string='Signup command.', aliases=['join', 'register'],
                    example='user signup | user join',
                    init='$scope.apps.user.signup();', command='lib.commands.user.register'),

            Command(name='resend', help_string='Resend your confirmation mail.',
                    example='user resend email@example.com', arguments=['email'], pro=True,
                    init='$scope.apps.user.resend(email);', command='lib.commands.user.resend'),

            Command(name='recover', help_string='Recover your account.', arguments=['credential?'],
                    example='user recover| user forget email@exmpla.com', aliases=['forget', 'retrieve'],
                    pro=True, init='$scope.apps.user.recover(credential);', command='lib.commands.user.recover'),

            Command(name='show', help_string='Show profile of cmd user.', aliases=['profile', 'info'],
                    example='user show | user show example', arguments=['username?'], pro=True, auth_level=0,
                    init='$scope.apps.user.show(username);', command='lib.commands.user.show'),

            Command(name='update', help_string='Update your profile.', example='user update', pro=True, auth_level=0,
                    init='$scope.apps.user.update();', command='lib.commands.user.update')
        ]

    def controller(self):
        return Resource.load('scripts/apps/user.js')
