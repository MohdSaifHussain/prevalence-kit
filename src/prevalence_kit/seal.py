"""The sealed store: chunked Fernet, with an ordered manifest over the sequence.

Fernet authenticates each chunk on its own. It says nothing about whether the
chunks are all there, or in the right order. So each sealed item also carries an
ordered list of ciphertext digests and a total count, and that manifest is bound
into the ledger entry for the ingest step.

We chose Fernet over Cobblestone-128, which implements the C2SP chunked-
encryption spec and would have solved sequence integrity natively (D-9). Having
declined the spec that solves this, we carry the obligation here (D-14).

Digests are taken over *ciphertext*, so someone without the key can still check
that the sequence is intact. They cannot tell a tampered chunk from a
substituted one -- that needs the key -- and `verify_structure` says so rather
than guessing.

Still leaks: chunk count and sizes reveal approximate plaintext length.
SECURITY.md section 3.7.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from cryptography.fernet import Fernet, InvalidToken

from .canonical import JSONObject, JSONValue, digest_bytes
from .errors import Reason, Refusal

CHUNK_BYTES = 64 * 1024
"""Plaintext bytes per chunk. Fernet holds the whole chunk in memory, so this
bounds memory use regardless of item size."""


@dataclass(frozen=True, slots=True)
class Manifest:
    """What the ledger commits to for one sealed item."""

    item_id: str
    chunk_digests: tuple[str, ...]  # ordered, over ciphertext
    chunk_count: int
    plaintext_bytes: int
    plaintext_digest: str

    def as_record(self) -> JSONObject:
        return {
            "item_id": self.item_id,
            "chunk_digests": list(self.chunk_digests),
            "chunk_count": self.chunk_count,
            "plaintext_bytes": self.plaintext_bytes,
            "plaintext_digest": self.plaintext_digest,
        }

    @classmethod
    def from_record(cls, raw: JSONValue) -> Self:
        if not isinstance(raw, Mapping):
            raise Refusal(
                Reason.LEDGER_BROKEN,
                "A seal record in the ledger is not a mapping.",
                "The ledger has been edited. Restore it from your record.",
            )
        digests = raw["chunk_digests"]
        if not isinstance(digests, Sequence) or isinstance(digests, str):
            raise Refusal(
                Reason.LEDGER_BROKEN,
                "A seal record's chunk_digests is not a list.",
                "The ledger has been edited. Restore it from your record.",
            )
        return cls(
            item_id=str(raw["item_id"]),
            chunk_digests=tuple(str(d) for d in digests),
            chunk_count=int(str(raw["chunk_count"])),
            plaintext_bytes=int(str(raw["plaintext_bytes"])),
            plaintext_digest=str(raw["plaintext_digest"]),
        )

    def preview(self) -> JSONObject:
        """The safe view. Never the content -- length and digest only."""
        return {
            "item_id": self.item_id,
            "bytes": self.plaintext_bytes,
            "digest": self.plaintext_digest[:16],
            "chunks": self.chunk_count,
        }


class SealedStore:
    """One directory of sealed items. `root/<dir>/0000.bin`, zero-padded.

    Two guards live here and they have deliberately opposite predicates. Writing
    one guard for both would break one of the two cases, so they have separate
    codes and separate tests:

    * ``write_once=True`` -- the store refuses to seal into a directory that
      already exists, whatever the item id. Used for ``plan.sealed`` (Layer 4 of
      the V-1 fix): re-registering a plan must never destroy the copy of the plan
      that was originally committed to.

    * ``write_once=False`` (default, content store) -- a directory refuses a
      *different* item id, but the **same** id may be re-sealed. That case is
      lawful and reachable: a crash between sealing and ``ledger.append`` leaves
      sealed items with no entry, and the retry re-seals all of them. Under
      strict linearity no duplicate entry exists, so the retry is legitimate, and
      a guard that refused same-id re-seal would brick it.
    """

    def __init__(self, root: Path, key: bytes | None = None, *, write_once: bool = False) -> None:
        self.root = root
        self._fernet = Fernet(key) if key else None
        self.write_once = write_once

    @staticmethod
    def new_key() -> bytes:
        return Fernet.generate_key()

    @property
    def fernet(self) -> Fernet:
        if self._fernet is None:
            raise RuntimeError(
                "This operation needs the sealing key; the store was opened without one."
            )
        return self._fernet

    def seal(self, item_id: str, plaintext: bytes) -> Manifest:
        """Encrypt and write one item. Returns the manifest to bind into the ledger."""
        item_dir = self.root / _safe_id(item_id)
        self._guard(item_dir, item_id)
        item_dir.mkdir(parents=True, exist_ok=True)
        (item_dir / OWNER_FILE).write_text(_full_id(item_id), encoding="utf-8")
        for stale in item_dir.glob("*.bin"):
            stale.unlink()
        digests: list[str] = []
        for i in range(0, max(len(plaintext), 1), CHUNK_BYTES):
            token = self.fernet.encrypt(plaintext[i : i + CHUNK_BYTES])
            (item_dir / f"{len(digests):04d}.bin").write_bytes(token)
            digests.append(digest_bytes(token))
        return Manifest(
            item_id=item_id,
            chunk_digests=tuple(digests),
            chunk_count=len(digests),
            plaintext_bytes=len(plaintext),
            plaintext_digest=digest_bytes(plaintext),
        )

    def unseal(self, manifest: Manifest) -> bytes:
        """Decrypt one item. Verifies first -- we never hand back unchecked bytes.

        Callers log this. Nothing in this tool unseals as a side effect.
        """
        self.verify_item(manifest)
        plaintext = b"".join(self.fernet.decrypt(t) for t in self._tokens(manifest.item_id))
        if digest_bytes(plaintext) != manifest.plaintext_digest:
            raise Refusal(
                Reason.SEAL_TAMPERED,
                f"Item {manifest.item_id} decrypted, but its contents do not match the record.",
                "The sealed store no longer holds what the ledger says it holds.",
            )
        return plaintext

    def verify_item(self, manifest: Manifest) -> None:
        """Full check: authenticate every chunk, then check the sequence.

        Order matters and is deliberate. Authentication runs first so a chunk
        whose bytes were edited reports SEAL_TAMPERED, rather than surfacing as a
        generic digest mismatch. Only chunks that genuinely authenticate can then
        be judged as truncated, reordered, or substituted.
        """
        for i, token in enumerate(self._tokens(manifest.item_id)):
            try:
                self.fernet.decrypt(token)
            except InvalidToken as exc:
                raise Refusal(
                    Reason.SEAL_TAMPERED,
                    f"Chunk {i} of item {manifest.item_id} failed authentication.",
                    "Those bytes were changed after sealing. Restore the sealed store.",
                ) from exc
        self.verify_structure(manifest)

    def verify_structure(self, manifest: Manifest) -> None:
        """Sequence check only.

        Distinguishes truncation from reordering from substitution by comparing
        the ordered list first, then the multiset. Without the multiset step a
        reorder and a substitution both look like "the digest at position i is
        wrong", and one reason code for both would tell an operator nothing.

        **This method needs no key** -- digests are taken over ciphertext, so
        someone holding only the sealed store can call it directly and check that
        the sequence is intact. **`verify_run` does not offer that as a mode**:
        it needs the key for the plan and the estimate, and it refuses
        `KEY_MISSING` before reaching here. The docstring used to claim the
        keyless path as if `verify` provided it, which it does not. A keyless
        audit mode is genuinely worth having and is carried as obligation O-14
        for Phase 2, not smuggled in here. V-10.
        """
        observed = [digest_bytes(t) for t in self._tokens(manifest.item_id)]
        expected = list(manifest.chunk_digests)

        # The manifest carries a count as well as a list, and both are checked.
        # A count recorded and never compared is a field, not a guard: it was
        # possible to set chunk_count to 999 against one chunk on disk and have
        # verify pass. D-14 asked for both halves. V-5.
        if manifest.chunk_count != len(expected):
            raise Refusal(
                Reason.SEAL_MANIFEST_MISMATCH,
                f"Item {manifest.item_id}: the record says {manifest.chunk_count} chunks "
                f"but lists {len(expected)} digests. The record disagrees with itself.",
                "The ledger entry was edited. Restore it from your record.",
            )
        if len(observed) != manifest.chunk_count:
            raise Refusal(
                Reason.SEAL_TRUNCATED
                if len(observed) < manifest.chunk_count
                else Reason.SEAL_MANIFEST_MISMATCH,
                f"Item {manifest.item_id} has {len(observed)} chunks on disk; "
                f"the record says {manifest.chunk_count}.",
                "The sealed store does not match the record. Restore it.",
            )

        if len(observed) < len(expected):
            raise Refusal(
                Reason.SEAL_TRUNCATED,
                f"Item {manifest.item_id} has {len(observed)} chunks; "
                f"the record says {len(expected)}.",
                "Chunks are missing from the sealed store. Restore it from your record.",
            )
        if len(observed) > len(expected):
            raise Refusal(
                Reason.SEAL_MANIFEST_MISMATCH,
                f"Item {manifest.item_id} has {len(observed)} chunks; "
                f"the record says {len(expected)}.",
                "Chunks were added to the sealed store. Restore it from your record.",
            )
        if observed == expected:
            return
        if Counter(observed) == Counter(expected):
            first = next(
                i for i, (o, e) in enumerate(zip(observed, expected, strict=True)) if o != e
            )
            raise Refusal(
                Reason.SEAL_REORDERED,
                f"Item {manifest.item_id} has all its chunks, "
                f"but they are out of order from chunk {first}.",
                "The chunk files were renamed or swapped. Restore them from your record.",
            )
        raise Refusal(
            Reason.SEAL_MANIFEST_MISMATCH,
            f"Item {manifest.item_id} contains a chunk the record does not list.",
            "A chunk was replaced with different sealed content. Restore from your record.",
        )

    def _guard(self, item_dir: Path, item_id: str) -> None:
        """Refuse the two ways a seal could destroy or shadow existing evidence."""
        if not item_dir.exists():
            return
        if self.write_once:
            raise Refusal(
                Reason.SEAL_ALREADY_WRITTEN,
                f"{self.root.name} already holds a sealed copy and is write-once.",
                "This workspace already holds a measurement. Start a new one rather "
                "than overwriting what was originally committed to.",
            )
        owner = item_dir / OWNER_FILE
        recorded = owner.read_text(encoding="utf-8").strip() if owner.exists() else ""
        if recorded and recorded != _full_id(item_id):
            raise Refusal(
                Reason.SEAL_ID_COLLISION,
                f"The sealed directory for item {item_id} already belongs to a different item.",
                "Two item ids collided in the sealed store. Rename one of them, or "
                "report this -- it should be vanishingly rare.",
            )

    def _tokens(self, item_id: str) -> list[bytes]:
        item_dir = self.root / _safe_id(item_id)
        if not item_dir.is_dir():
            raise Refusal(
                Reason.SEAL_TRUNCATED,
                f"Item {item_id} is not in the sealed store.",
                "The whole item is missing. Restore the sealed store from your record.",
            )
        return [p.read_bytes() for p in sorted(item_dir.glob("*.bin"), key=_chunk_index)]


OWNER_FILE = ".itemid"
"""Holds the item id's full digest, so a truncated-directory collision is caught
rather than silently overwriting another item. F-7."""


def _chunk_index(path: Path) -> int:
    """Sort chunks numerically.

    Lexicographic order breaks once the index needs a fifth digit: "10000.bin"
    sorts before "9999.bin". At 64 KiB chunks that is any item over 640 MB, and
    the symptom would be a tamper alarm on lawful data. F-2.
    """
    return int(path.stem)


def _full_id(item_id: str) -> str:
    return digest_bytes(item_id.encode("utf-8"))


def _safe_id(item_id: str) -> str:
    """Item ids come from input files, so they never become path components raw.

    Truncated to 128 bits for a readable directory name; `OWNER_FILE` carries the
    full digest so a collision is detected rather than silently overwriting.
    """
    return _full_id(item_id)[:32]
