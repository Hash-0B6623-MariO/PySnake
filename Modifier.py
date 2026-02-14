class Modifier:
    """ Base class. """
    @classmethod
    def getGroup(cls, path):
        with open(path, 'r') as f:
            return f.read().splitlines()
        return 


