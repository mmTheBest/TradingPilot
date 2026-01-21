from typing import Iterable


def _index(records: Iterable[dict], key_fields: list[str]) -> dict[tuple, dict]:
    indexed: dict[tuple, dict] = {}
    for record in records:
        key = tuple(record.get(field) for field in key_fields)
        indexed[key] = record
    return indexed


def diff_positions(prev: list[dict], new: list[dict], key_fields: list[str]) -> list[dict]:
    prev_index = _index(prev, key_fields)
    new_index = _index(new, key_fields)
    ops: list[dict] = []

    for key, record in new_index.items():
        if key not in prev_index:
            ops.append({"op": "add", "key": dict(zip(key_fields, key)), "after": record})
        elif record != prev_index[key]:
            ops.append(
                {
                    "op": "update",
                    "key": dict(zip(key_fields, key)),
                    "before": prev_index[key],
                    "after": record,
                }
            )

    for key, record in prev_index.items():
        if key not in new_index:
            ops.append({"op": "delete", "key": dict(zip(key_fields, key)), "before": record})

    return ops
