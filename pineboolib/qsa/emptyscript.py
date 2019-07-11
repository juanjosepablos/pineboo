# -*- coding: utf-8 -*-
from pineboolib.pncontrolsfactory import FormDBWidget
from pineboolib.application.types import Object


class interna(object):
    ctx = Object()

    def __init__(self, context=None) -> None:
        self.ctx = context

    def init(self) -> None:
        self.ctx.interna_init()


class oficial(interna):
    def __init__(self, context=None):
        super(oficial, self).__init__(context)


class head(oficial):
    def __init__(self, context=None):
        super(head, self).__init__(context)


class ifaceCtx(head):
    def __init__(self, context=None):
        super(ifaceCtx, self).__init__(context)


class FormInternalObj(FormDBWidget):
    def _class_init(self) -> None:
        # DEBUG:: Const Declaration:
        self.iface = ifaceCtx(self)

    def interna_init(self) -> None:
        pass


form = None