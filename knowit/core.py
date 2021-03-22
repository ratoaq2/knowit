import typing
from logging import NullHandler, getLogger

logger = getLogger(__name__)
logger.addHandler(NullHandler())

T = typing.TypeVar('T')


class Reportable(typing.Generic[T]):
    """Reportable abstract class."""

    def __init__(
            self,
            name: str,
            description: typing.Optional[str] = None,
            reportable: bool = True,
    ):
        """Initialize the object."""
        self.name = name
        self._description = description
        self.reportable = reportable

    @property
    def description(self) -> str:
        """Rule description."""
        return self._description or self.name

    def report(self, value: T, context: typing.MutableMapping) -> None:
        """Report unknown value."""
        if not value or not self.reportable:
            return

        if 'report' in context:
            report_map = context['report'].setdefault(self.description, {})
            if value not in report_map:
                report_map[value] = context['path']
        logger.info('Invalid %s: %r', self.description, value)
