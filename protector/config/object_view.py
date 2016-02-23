class ObjectView(object):
    """
    Creates an object from a dict
    Example:
    config = {"hello": "world"}
    config_object = ObjectView(config)
    assert(config_object.hello == "world")
    """

    def __init__(self, d):
        self.__dict__ = d

    def __repr__(self):
        output = []
        for k, v in self.__dict__.items():
            key = "{}:".format(k)
            output.append("{:<15}{}".format(key, v))
        return "\n".join(output)


