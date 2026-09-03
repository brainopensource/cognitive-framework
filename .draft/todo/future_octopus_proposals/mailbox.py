"""Mailboxes: the only channel between roles.

Roles never share memory, never call each other, and never observe each
other's episodes. They publish content-addressed artifacts and read the
artifacts their declared dependencies published. That restriction is what
makes a topology replayable: the input to any role is a set of digests.

A mailbox is append-only. There is no update and no delete, so a child cannot
retroactively change what a sibling already read.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..canonicalisation.digest import digest_of

__all__ = ["Message", "Mailbox", "MailboxError"]


class MailboxError(RuntimeError):
    """An illegal mailbox operation — publishing an undeclared kind, etc."""


@dataclass(frozen=True, slots=True)
class Message:
    """One published artifact, addressed by the digest of its content."""

    sender: str
    kind: str
    payload: Mapping[str, Any]
    #: Digest of the payload; also the artifact's address in the blob store.
    digest: str = ""

    def __post_init__(self) -> None:
        if not self.sender.strip():
            raise MailboxError("message requires a sender role")
        if not self.kind.strip():
            raise MailboxError("message requires a kind")
        if not isinstance(self.payload, Mapping):
            raise MailboxError("message payload must be a mapping")
        if not self.digest:
            object.__setattr__(self, "digest", digest_of(dict(self.payload)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender": self.sender,
            "kind": self.kind,
            "digest": self.digest,
            "payload": dict(self.payload),
        }


class Mailbox:
    """Append-only artifact exchange for one plan instance."""

    def __init__(self, correlation_id: str = "") -> None:
        self.correlation_id = correlation_id
        self._messages: list[Message] = []

    def publish(
        self,
        sender: str,
        kind: str,
        payload: Mapping[str, Any],
        *,
        allowed_kinds: Sequence[str] | None = None,
    ) -> Message:
        """Append a message. Enforces the role's declared `publishes` set.

        Enforcing the declared kinds here means a role cannot quietly become a
        channel for something the plan never authorised.
        """
        if allowed_kinds is not None and kind not in allowed_kinds:
            raise MailboxError(
                f"role {sender!r} may publish {sorted(allowed_kinds)}, not {kind!r}")
        message = Message(sender=sender, kind=kind, payload=payload)
        self._messages.append(message)
        return message

    def read(
        self,
        *,
        senders: Sequence[str] | None = None,
        kind: str | None = None,
    ) -> tuple[Message, ...]:
        """Read messages, filtered. Order is publication order and is stable."""
        results = tuple(
            message for message in self._messages
            if (senders is None or message.sender in senders)
            and (kind is None or message.kind == kind)
        )
        return results

    def inbox_for(self, depends_on: Sequence[str]) -> tuple[Message, ...]:
        """Everything this role is entitled to see: its dependencies' output."""
        if not depends_on:
            return ()
        return self.read(senders=tuple(depends_on))

    @property
    def digests(self) -> tuple[str, ...]:
        return tuple(message.digest for message in self._messages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "messages": [message.to_dict() for message in self._messages],
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "Mailbox":
        """Rebuild on resume, preserving digests exactly."""
        mailbox = cls(str(raw.get("correlation_id", "")))
        for entry in raw.get("messages") or ():
            mailbox._messages.append(Message(
                sender=str(entry["sender"]),
                kind=str(entry["kind"]),
                payload=dict(entry.get("payload") or {}),
                digest=str(entry.get("digest", "")),
            ))
        return mailbox

    def __len__(self) -> int:
        return len(self._messages)
