from typing import Callable
import logging


class DelayedObjectProxyLoader(object):
    logger = logging.getLogger("application.DelayedObjectProxyLoader")

    def __init__(self, obj: Callable, *args, **kwargs) -> None:
        """
        Constructor
        """
        self._name = "unnamed-loader"
        if "name" in kwargs:
            self._name = kwargs["name"]
            del kwargs["name"]
        self._obj = obj
        self._args = args
        self._kwargs = kwargs
        self.loaded_obj = None

    def __load(self):
        """
        Carga un objeto nuevo
        @return objeto nuevo o si ya existe , cacheado
        """
        self.logger.debug("DelayedObjectProxyLoader: loading %s %s( *%s **%s)", self._name, self._obj, self._args, self._kwargs)

        self.loaded_obj = self._obj(*self._args, **self._kwargs)
        return self.loaded_obj

    def __getattr__(self, name):  # Solo se lanza si no existe la propiedad.
        """
        Retorna una función buscada
        @param name. Nombre del la función buscada
        @return el objecto del XMLAction afectado
        """
        obj_ = self.__load()
        return getattr(obj_, name, getattr(obj_.widget, name, None)) if obj_ else None