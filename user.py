import yaml


class User:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    username: str = config['username']
    password: str = config['password']
