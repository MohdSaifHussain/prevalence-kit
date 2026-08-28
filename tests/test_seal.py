"""The sealed store, and the four ways a chunk sequence can be wrong.

D-14 is the director's binding addition: Fernet authenticates each chunk, the
manifest authenticates the sequence. These tests exist to prove the four failure
modes produce four *different* reason codes. If any two collapse into one, the
gate has not been built -- an operator told only "the seal is wrong" learns
nothing about what happened.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.seal import CHUNK_BYTES, SealedStore


@pytest.fixture
def store(tmp_path: Path) -> SealedStore:
    return SealedStore(tmp_path / "sealed", SealedStore.new_key())


@pytest.fixture
def big(store: SealedStore):  # type: ignore[no-untyped-def]
    """Four chunks, so truncation and reordering are both expressible."""
    plaintext = bytes(range(256)) * ((CHUNK_BYTES * 3 + 17) // 256 + 1)
    return plaintext, store.seal("big", plaintext)


def chunks(store: SealedStore, item_id: str) -> list[Path]:
    from prevalence_kit.seal import _safe_id

    return sorted((store.root / _safe_id(item_id)).glob("*.bin"))


# --------------------------------------------------------- positive controls


def test_roundtrip(store: SealedStore) -> None:
    """A gate that refuses everything proves nothing. This is the accept case."""
    plaintext = "harmful text with unicode: é中\U0001f600".encode()
    manifest = store.seal("item-1", plaintext)
    assert store.unseal(manifest) == plaintext


def test_intact_multichunk_verifies(store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    plaintext, manifest = big
    assert manifest.chunk_count == 4
    store.verify_item(manifest)  # must not raise
    assert store.unseal(manifest) == plaintext


def test_structure_check_needs_no_key(tmp_path: Path, store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    """An outside auditor without the key can still check the sequence."""
    _, manifest = big
    keyless = SealedStore(store.root)
    keyless.verify_structure(manifest)  # must not raise


def test_ciphertext_differs_across_seals(store: SealedStore) -> None:
    """Fernet IVs are random, so identical plaintext must not produce identical bytes."""
    a = store.seal("a", b"same")
    b = store.seal("b", b"same")
    assert a.chunk_digests != b.chunk_digests
    assert a.plaintext_digest == b.plaintext_digest


def test_preview_never_carries_content(store: SealedStore) -> None:
    manifest = store.seal("item-1", b"SENTINEL-do-not-print")
    assert "SENTINEL" not in str(manifest.preview())


# --------------------------------------------------------- negative controls


def test_tampered_chunk(store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    _, manifest = big
    path = chunks(store, "big")[1]
    raw = bytearray(path.read_bytes())
    raw[-1] ^= 0xFF
    path.write_bytes(bytes(raw))

    with pytest.raises(Refusal) as exc:
        store.verify_item(manifest)
    assert exc.value.reason is Reason.SEAL_TAMPERED


def test_truncated_drops_final_chunk(store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    """Exit check E9b."""
    _, manifest = big
    chunks(store, "big")[-1].unlink()

    with pytest.raises(Refusal) as exc:
        store.verify_item(manifest)
    assert exc.value.reason is Reason.SEAL_TRUNCATED


def test_reordered_swaps_two_chunks(store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    """Exit check E9c. Every chunk still authenticates; only the order is wrong."""
    _, manifest = big
    a, b = chunks(store, "big")[0], chunks(store, "big")[1]
    a_bytes, b_bytes = a.read_bytes(), b.read_bytes()
    a.write_bytes(b_bytes)
    b.write_bytes(a_bytes)

    with pytest.raises(Refusal) as exc:
        store.verify_item(manifest)
    assert exc.value.reason is Reason.SEAL_REORDERED


def test_substituted_chunk_from_elsewhere(store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    """A validly sealed chunk from another item. Authenticates, but is not ours."""
    _, manifest = big
    store.seal("other", b"y" * 64)
    chunks(store, "big")[0].write_bytes(chunks(store, "other")[0].read_bytes())

    with pytest.raises(Refusal) as exc:
        store.verify_item(manifest)
    assert exc.value.reason is Reason.SEAL_MANIFEST_MISMATCH


def test_extra_chunk_appended(store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    _, manifest = big
    store.seal("other", b"z" * 64)
    (chunks(store, "big")[-1].parent / "9999.bin").write_bytes(
        chunks(store, "other")[0].read_bytes()
    )

    with pytest.raises(Refusal) as exc:
        store.verify_item(manifest)
    assert exc.value.reason is Reason.SEAL_MANIFEST_MISMATCH


def test_missing_item_entirely(store: SealedStore, big) -> None:  # type: ignore[no-untyped-def]
    _, manifest = big
    for p in chunks(store, "big"):
        p.unlink()
    chunks(store, "big")[0].parent.rmdir() if chunks(store, "big") else None

    with pytest.raises(Refusal) as exc:
        store.verify_item(manifest)
    assert exc.value.reason is Reason.SEAL_TRUNCATED


def test_the_four_reason_codes_are_distinct(store: SealedStore) -> None:
    """The point of D-14, asserted directly rather than inferred from four tests."""
    codes = {
        Reason.SEAL_TAMPERED,
        Reason.SEAL_TRUNCATED,
        Reason.SEAL_REORDERED,
        Reason.SEAL_MANIFEST_MISMATCH,
    }
    assert len(codes) == 4
