import unittest
from stt_mvp.codec import canonical_json, strict_json, CodecError
class CodecTests(unittest.TestCase):
 def test_canonical(self): self.assertEqual(canonical_json({"b":1,"a":"x"}), b'{"a":"x","b":1}\n')
 def test_reject(self):
  for v in (b'{"a":1,"a":2}\n',b'{"a":NaN}\n',b'{ "a":1}\n'):
   with self.assertRaises(CodecError): strict_json(v)
 def test_float_is_not_control_integer(self):
  with self.assertRaises(CodecError): canonical_json({"a": 1.0})
