import yaml

CFG_PATH = 'resources/config.yaml'

class ParameterManager:
    _instance = None

    def __new__(cls, config_path=CFG_PATH):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init(config_path)
        return cls._instance

    def _init(self, config_path):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"[ParameterManager] Loaded config from {config_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

    def get(self, section, key, default=None):
        try:
            return self.config[section][key]
        except KeyError:
            if default is not None:
                return default
            raise KeyError(f"Parameter not found: [{section}][{key}]")

# ✅ Esempio di utilizzo:
if __name__ == "__main__":
    params = ParameterManager()

    host = params.get('server', 'host')
    port = params.get('server', 'port')
    word_list_files = params.get('game', 'word_list_files')

    print(f"Host: {host}, Port: {port}")
    print(f"Word lists: {word_list_files}")
