"""The two seal guards, which look alike and must not collapse into one.

They need opposite predicates, so they get separate codes and separate tests:

* `write_once=True` (`plan.sealed`) -- refuses to seal into a directory that
  already exists, whatever the id. Layer 4 of the V-1 fix: re-registering a plan
  must never destroy the copy of the plan originally committed to.

* `write_once=False` (content store) -- refuses a *different* id in an existing
  directory, but the **same** id may be re-sealed. That case is lawful and
  reachable: a crash between sealing and `ledger.append` leaves sealed items with
  no entry, and the retry re-seals all of them. Under strict linearity no
  duplicate entry exists, so the retry is legitimate. A guard refusing same-id
  re-seal would brick it.

Also here: chunk ordering past four digits (F-2), and the manifest's chunk count
being checked rather than merely recorded (V-5).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prevalence_kit import seal as seal_mod
from prevalence_kit.errors import Reason, Refusal
from prevalence_kit.seal import Manifest, SealedStore, _safe_id


@pytest.fixture
def key() -> bytes:
    return SealedStore.new_key()


# ------------------------------------------------- Layer 4: write-once store


def test_write_once_refuses_a_second_seal(tmp_path: Path, key: bytes) -> None:
    store = SealedStore(tmp_path / "plan.sealed", key, write_once=True)
    store.seal("__plan__", b'{"threshold":"0.5"}')

    with pytest.raises(Refusal) as exc:
        store.seal("__plan__", b'{"threshold":"0.05"}')
    assert exc.value.reason is Reason.SEAL_ALREADY_WRITTEN


def test_write_once_leaves_the_original_recoverable(tmp_path: Path, key: bytes) -> None:
    """The point of Layer 4: the first commitment survives the second attempt."""
    store = SealedStore(tmp_path / "plan.sealed", key, write_once=True)
    manifest = store.seal("__plan__", b'{"threshold":"0.5"}')
    with pytest.raises(Refusal):
        store.seal("__plan__", b'{"threshold":"0.05"}')
    assert store.unseal(manifest) == b'{"threshold":"0.5"}'


def test_write_once_accepts_the_first_seal(tmp_path: Path, key: bytes) -> None:
    store = SealedStore(tmp_path / "plan.sealed", key, write_once=True)
    manifest = store.seal("__plan__", b"first")
    assert store.unseal(manifest) == b"first"


# ---------------------------------------------- F-7: content store collision


def test_same_id_may_be_resealed(tmp_path: Path, key: bytes) -> None:
    """The crash-retry case. Refusing this would brick a lawful recovery."""
    store = SealedStore(tmp_path / "sealed", key)
    store.seal("item-1", b"first attempt")
    manifest = store.seal("item-1", b"second attempt after a crash")
    assert store.unseal(manifest) == b"second attempt after a crash"


def test_a_different_id_in_the_same_directory_is_refused(
    tmp_path: Path, key: bytes, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Forces the truncated-digest collision that 128 bits makes astronomical.

    The guard exists for the reachable consequence, not the probability: a
    collision would silently overwrite one item with another and nothing would
    detect it.
    """
    store = SealedStore(tmp_path / "sealed", key)
    store.seal("item-1", b"one")
    monkeypatch.setattr(seal_mod, "_safe_id", lambda _: _safe_id("item-1"))

    with pytest.raises(Refusal) as exc:
        store.seal("item-2-different", b"two")
    assert exc.value.reason is Reason.SEAL_ID_COLLISION


def test_stale_chunks_do_not_survive_a_reseal(tmp_path: Path, key: bytes) -> None:
    """A shorter second seal must not leave the tail of the first behind."""
    store = SealedStore(tmp_path / "sealed", key)
    store.seal("item-1", b"x" * (seal_mod.CHUNK_BYTES * 3))
    manifest = store.seal("item-1", b"short")
    store.verify_item(manifest)
    assert manifest.chunk_count == 1


# --------------------------------------------------- F-2: chunk order past 4 digits


def test_chunk_files_are_read_back_in_numeric_order(tmp_path: Path, key: bytes) -> None:
    """The property under test is lexicographic-versus-numeric sorting.

    "10000.bin" sorts *before* "9999.bin" lexicographically. At the real 64 KiB
    chunk size that boundary is any single item over 640 MB, and the symptom
    would be a tamper alarm on lawful data.

    **What this trades, stated rather than left for a reader to notice.** The
    end-to-end version -- seal 10,050 real chunks, verify, unseal -- proved the
    same property and took 112 seconds on every edit-run loop. This version
    writes the files directly and asserts the read-back order, and the test below
    pins the filename format they are written in. Together they cover the
    property; separately, each covers half, and composing them is an inference
    rather than a demonstration. That inference is the cost of a one-second test.
    """
    item_dir = tmp_path / "sealed" / _safe_id("big")
    item_dir.mkdir(parents=True)
    for i in range(10_050):
        (item_dir / f"{i:04d}.bin").write_bytes(str(i).encode())

    store = SealedStore(tmp_path / "sealed", key)
    order = [int(t.decode()) for t in store._tokens("big")]
    assert order == list(range(10_050))


def test_chunk_filenames_use_the_format_the_reader_expects(tmp_path: Path, key: bytes) -> None:
    """The other half of the split above: what `seal` actually writes."""
    monkeypatch_free_store = SealedStore(tmp_path / "sealed", key)
    manifest = monkeypatch_free_store.seal("item-1", b"content")
    names = sorted(p.name for p in (tmp_path / "sealed" / _safe_id("item-1")).glob("*.bin"))

    assert names == ["0000.bin"]
    assert manifest.chunk_count == 1
    assert all(seal_mod._chunk_index(Path(n)) == i for i, n in enumerate(names))


# ----------------------------------------------------- V-5: the count is checked


def test_a_count_disagreeing_with_the_digest_list_is_refused(tmp_path: Path, key: bytes) -> None:
    """D-14 asked for a manifest AND a count. The count was recorded, never read.

    It was possible to claim 999 chunks against one on disk and have `verify`
    pass, because `verify_structure` only compared against `len(chunk_digests)`.
    """
    store = SealedStore(tmp_path / "sealed", key)
    honest = store.seal("item-1", b"content")
    lying = Manifest(
        item_id=honest.item_id,
        chunk_digests=honest.chunk_digests,
        chunk_count=999,
        plaintext_bytes=honest.plaintext_bytes,
        plaintext_digest=honest.plaintext_digest,
    )

    with pytest.raises(Refusal) as exc:
        store.verify_item(lying)
    assert exc.value.reason is Reason.SEAL_MANIFEST_MISMATCH
    assert "disagrees with itself" in exc.value.detail


def test_an_honest_count_still_passes(tmp_path: Path, key: bytes) -> None:
    store = SealedStore(tmp_path / "sealed", key)
    manifest = store.seal("item-1", b"content")
    assert manifest.chunk_count == len(manifest.chunk_digests)
    store.verify_item(manifest)


def test_the_six_seal_reason_codes_are_distinct() -> None:
    codes = {
        Reason.SEAL_TAMPERED,
        Reason.SEAL_TRUNCATED,
        Reason.SEAL_REORDERED,
        Reason.SEAL_MANIFEST_MISMATCH,
        Reason.SEAL_ALREADY_WRITTEN,
        Reason.SEAL_ID_COLLISION,
    }
    assert len(codes) == 6
