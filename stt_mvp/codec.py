"""Canonical UTF-8 JSON encoding and strict decoding."""
import json
import math


class CodecError(ValueError):
    pass


def _reject_constant(value):
    raise CodecError("non-finite JSON number")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CodecError("duplicate JSON object key: %s" % key)
        result[key] = value
    return result


def canonical_json(value):
    """Return the sole canonical JSON representation, including its LF."""
    def check(item):
        if type(item) is float:
            raise CodecError("canonical control JSON permits integers, not floats")
        if isinstance(item, dict):
            for key, child in item.items():
                if type(key) is not str:
                    raise CodecError("JSON object keys must be strings")
                check(child)
        elif isinstance(item, (list, tuple)):
            for child in item:
                check(child)
    check(value)
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise CodecError(str(exc)) from exc
    return text.encode("utf-8") + b"\n"


def strict_json(data):
    if not isinstance(data, (bytes, bytearray)):
        raise CodecError("JSON input must be bytes")
    try:
        text = bytes(data).decode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, CodecError) as exc:
        raise CodecError(str(exc)) from exc
    if canonical_json(value) != bytes(data):
        raise CodecError("JSON bytes are not canonical")
    return value


def closed_object(value, required):
    if not isinstance(value, dict) or set(value) != set(required):
        raise CodecError("object fields are not exactly the closed schema")
    return value
