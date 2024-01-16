from configparser import ConfigParser
from pathlib import Path

class Conf:
    def __init__(self):
        confDict = {}
        conf = ConfigParser()
        configPath = Path.cwd() / 'config.ini'
        conf.read(configPath)
        for k, v in conf.items():
            confDict[k] = dict(conf.items(k))

        confDict['screen']['white_list'] = confDict['screen']['white_list'].split(',')
        goodPath = []
        for path in confDict['screen']['white_list']:
            goodPath.append(str(Path(path)))
        confDict['screen']['white_list'] = goodPath
        # print(confDict['screen']['white_list'])
        self.confDict = confDict
    def getConf(self):
        return self.confDict

conf = Conf().getConf()
