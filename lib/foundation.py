from lib.capsule.app import application as cmd_app_capsule


def boot():
    register_app_capsule()


def register_jwt_authenticate():
    pass


def register_app_capsule():
    cmd_app_capsule.register()
