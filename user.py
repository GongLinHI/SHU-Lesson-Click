import yaml


class User:
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    username: str = config['username']
    password: str = config['password']
