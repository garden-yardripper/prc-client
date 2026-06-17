from .fetch import _GetDataAsync, _GetDataSync

class AsyncClient(_GetDataAsync):
    pass

class Client(_GetDataSync):
    pass