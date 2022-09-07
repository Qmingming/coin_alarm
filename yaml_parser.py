import yaml


class YamlParser:
    def __init__(self, filename):
        self.conf = None
        self.filename = filename;

    def parse(self):
        with open(self.filename) as f:
            self.conf = yaml.full_load(f)
            #sorted_data = yaml.dump(self.conf, sort_keys=True)

            #for value in self.conf['Data']:
            #    print(value)

            #print(self.conf)
            return self.conf
