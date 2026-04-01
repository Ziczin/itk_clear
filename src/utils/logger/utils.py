from typing import Any, Dict, List
from dataclasses import dataclass, field


class ConsoleOutputType:
    """Допустимые значения для формата вывода в консоль"""

    PRETTY = "pretty"
    COMPACT = "compact"
    PLAIN = "plain"

    @classmethod
    def values(cls) -> List[str]:
        """Возвращает список всех допустимых значений"""
        return [cls.PRETTY, cls.COMPACT, cls.PLAIN]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Проверяет, является ли значение допустимым"""
        return value in cls.values()


@dataclass
class LogContext:
    """Контекст логирования с trace_id и стеком вызовов"""

    trace_id: str
    trace_stack: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def push_trace(self, name: str) -> None:
        """Добавляет элемент в стек trace"""
        self.trace_stack.append(name)

    def pop_trace(self) -> None:
        """Удаляет последний элемент из стека trace"""
        if self.trace_stack:
            self.trace_stack.pop()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует контекст в словарь для логирования"""
        return {"context": self.trace_id, "trace": self.trace_stack.copy()}
