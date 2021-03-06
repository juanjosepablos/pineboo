# -*- coding: utf-8 -*-
"""PNAction Module."""

from pineboolib.core.utils.struct import ActionStruct

from typing import Union


class PNAction(object):
    """
    PNAction Class.

    This class contains information on actions to open forms.

    It is used to automatically link forms with your script,
    interface and source table.

    @author InfoSiAL S.L.
    """

    """
    Nombre de la accion
    """
    _name: str

    """
    Nombre del script asociado al formulario de edición de registros
    """
    _script_form_record: str

    """
    Nombre del script asociado al formulario maestro
    """
    _script_form: str

    """
    Nombre de la tabla origen para el formulario maestro
    """
    _table: str

    """
    Nombre del formulario maestro
    """
    _form: str

    """
    Nombre del formulario de edición de registros
    """
    _form_record: str

    """
    Texto para la barra de título del formulario maestro
    """
    _caption: str

    """
    Descripción
    """
    _description: str

    def __init__(self, action: Union[str, ActionStruct]) -> None:
        """Initialize."""

        self._name = ""
        self._caption = ""
        self._description = ""
        self._form = ""
        self._form_record = ""
        self._script_form = ""
        self._script_form_record = ""
        self._table = ""

        if isinstance(action, str):
            self.setName(action)

        elif isinstance(action, ActionStruct):
            self.setName(action.name)
            if action.mainscript is not None:
                self.setScriptForm(action.mainscript)
            if action.scriptformrecord is not None:
                self.setScriptFormRecord(action.scriptformrecord)
            if action.mainform is not None:
                self.setForm(action.mainform)
            if action.form is not None:
                self.setFormRecord(action.form)
            if action.alias is not None:
                self.setCaption(action.alias)
        else:
            raise Exception("Unsupported action %r" % action)

    def __repr__(self):
        """Return the values ​​in a text string."""

        return (
            "<PNAction name=%r scriptForm=%r scriptFormRecord=%r form=%r formRecord=%r caption=%r>"
            % (
                self._name,
                self._script_form,
                self._script_form_record,
                self._form,
                self._form_record,
                self._caption,
            )
        )

    def setName(self, name: str) -> None:
        """Set the name of the action."""

        self._name = name

    def setScriptFormRecord(self, script_form_record: str) -> None:
        """Set the name of the script associated with the record editing form."""

        self._script_form_record = "%s.qs" % script_form_record

    def setScriptForm(self, script_form: str) -> None:
        """Set the name of the script associated with the master form."""

        self._script_form = "%s.qs" % script_form

    def setTable(self, table: str) -> None:
        """Set the name of the source table of the master form."""

        self._table = table

    def setForm(self, form: str) -> None:
        """Set the name of the master form."""

        self._form = "%s.ui" % form

    def setFormRecord(self, form_record: str) -> None:
        """Set the name of the record editing form."""

        self._form_record = "%s.ui" % form_record

    def setCaption(self, caption: str) -> None:
        """Set the text of the title bar of the master form."""

        self._caption = caption

    def setDescription(self, description: str) -> None:
        """Set description."""

        self._description = description

    def name(self) -> str:
        """Get the name of the action."""

        return self._name

    def scriptFormRecord(self) -> str:
        """Get the name of the script associated with the record editing form."""

        return self._script_form_record

    def scriptForm(self) -> str:
        """Get the name of the script associated with the master form."""

        return self._script_form

    def table(self) -> str:
        """Get the table associated with the action."""

        return self._table

    def caption(self) -> str:
        """Get the text from the form's title bar."""

        return self._caption

    def description(self) -> str:
        """Get the description."""

        return self._description

    def form(self) -> str:
        """Get the name of the mestro form."""

        return self._form

    def formRecord(self) -> str:
        """Get the name of the record editing form."""

        return self._form_record
