# -*- coding=utf-8 -*-

from bootstrap import create_app

app = create_app(environ='default')

if __name__ == "__main__":
    app.run()
