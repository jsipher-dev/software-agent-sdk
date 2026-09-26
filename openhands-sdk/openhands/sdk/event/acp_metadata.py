"""ACPMetadataEvent — surfaces per-turn ACP usage metadata as OpenHands events.

Some ACP servers report per-turn usage via a provider-specific extension
notification rather than the standard ``UsageUpdate`` / ``PromptResponse.usage``
channels. Kiro CLI, for example, sends ``_kiro.dev/metadata`` after each turn
with credits consumed, the percentage of the context window used, and the turn
duration. This event carries that data into the OpenHands event stream so
clients can display it (e.g. "Credits: 0.21 | Context: 12%") without having to
understand the provider-specific wire format.

Credits and context percentage are provider-defined units, deliberately kept
distinct from the LLM cost (USD) and ``context_window`` (tokens) metrics so they
are never mislabeled as dollars or token counts.
"""

from __future__ import annotations

from rich.text import Text

from openhands.sdk.event.base import Event
from openhands.sdk.event.types import SourceType


class ACPMetadataEvent(Event):
    """Per-turn usage metadata reported by an ACP server extension.

    Not an ``LLMConvertibleEvent`` — this metadata does not participate in LLM
    message conversion; it is display/telemetry only.
    """

    source: SourceType = "agent"
    # Credits consumed for the turn (provider-defined unit, e.g. Kiro credits).
    # ``None`` when the provider does not report credits.
    credits: float | None = None
    # Percentage of the context window used (0-100), if reported.
    context_usage_percentage: float | None = None
    # Wall-clock duration of the turn in milliseconds, if reported.
    turn_duration_ms: int | None = None
    # Provider label (e.g. the ACP agent name) for display/attribution.
    provider: str | None = None

    @property
    def visualize(self) -> Text:
        content = Text()
        parts: list[str] = []
        if self.credits is not None:
            parts.append(f"Credits: {self.credits:.2f}")
        if self.context_usage_percentage is not None:
            parts.append(f"Context: {self.context_usage_percentage:.0f}%")
        if self.turn_duration_ms is not None:
            parts.append(f"Time: {self.turn_duration_ms / 1000:.0f}s")
        content.append(" | ".join(parts) if parts else "ACP metadata", style="dim")
        return content

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} ({self.source}): "
            f"credits={self.credits} "
            f"context_usage_percentage={self.context_usage_percentage} "
            f"turn_duration_ms={self.turn_duration_ms}"
        )
