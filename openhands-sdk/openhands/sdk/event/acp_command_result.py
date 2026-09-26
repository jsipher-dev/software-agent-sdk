"""ACPCommandResultEvent — surfaces the output of an ACP slash-command.

When a user runs an ACP slash-command (e.g. Kiro's ``/context``, ``/usage``,
``/model``) the ACP server executes it and returns a human-readable ``message``
plus an optional structured ``data`` payload. Previously the SDK collapsed that
response to a bare ``success`` boolean and discarded the message/data, so the
command appeared to "do nothing" in the UI even though it ran successfully.

This event carries the command's result into the OpenHands event stream so the
output (the context breakdown, the usage summary, etc.) renders in the chat and
is persisted, exactly like any other conversation event.
"""

from __future__ import annotations

from typing import Any

from rich.text import Text

from openhands.sdk.event.base import Event
from openhands.sdk.event.types import SourceType


class ACPCommandResultEvent(Event):
    """Result of an ACP slash-command executed on the live session.

    Not an ``LLMConvertibleEvent`` — the command output is user-facing display
    only and does not participate in LLM message conversion.
    """

    source: SourceType = "agent"
    # The slash-command that was executed, normalized with a single leading
    # slash for display (e.g. ``/context``, ``/usage``).
    command: str
    # The ACP server's success flag for the command.
    success: bool = True
    # Human-readable output returned by the command (the text the user should
    # see, e.g. the context breakdown or usage summary). ``None`` when the
    # server returned no message.
    message: str | None = None
    # Optional structured payload returned by the command (e.g. Kiro's
    # ``breakdown`` / ``usageBreakdowns``). Kept for clients that want to render
    # a richer view; ``None`` when the server returned no data.
    data: dict[str, Any] | None = None
    # Provider label (e.g. the ACP agent name) for display/attribution.
    provider: str | None = None

    @property
    def visualize(self) -> Text:
        content = Text()
        header = self.command if self.command.startswith("/") else f"/{self.command}"
        content.append(header, style="bold cyan")
        if not self.success:
            content.append("  (failed)", style="red")
        if self.message:
            content.append("\n")
            content.append(self.message)
        return content

    def __str__(self) -> str:
        msg = self.message or ""
        if len(msg) > 80:
            msg = msg[:77] + "..."
        return (
            f"{self.__class__.__name__} ({self.source}): "
            f"command={self.command!r} success={self.success} "
            f"message={msg!r}"
        )
