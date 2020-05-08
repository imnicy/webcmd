from bootstrap import create_manager

manager = create_manager(environ='default')

if __name__ == "__main__":
    manager.run()
