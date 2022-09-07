import yaml


class Parse:
    def __init__(self):
        with open('../info.yaml') as f:
            self.conf = yaml.full_load(f)
            sorted_data = yaml.dump(self.conf, sort_keys=True)

            for value in self.conf['Data']:
                print(value)

    def parsed_data(self):
        return self.conf
