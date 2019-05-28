import yaml

class Config:
    CONFIG_FILENAME = 'config.yml'

    def __init__(self, section):
        self._load_config(section)

    def _load_config(self, section):
      with open(self.CONFIG_FILENAME) as stream:
          try:
              self.config = yaml.safe_load(stream)[section]
          except yaml.YAMLError as e:
              print(e)
