import unittest
from stt_mvp.identity import H,uint64_be,record_id,raw_sha256,requirement_id
class IdentityTests(unittest.TestCase):
 def test_framing(self): self.assertNotEqual(H("a",b"bc"),H("ab",b"c")); self.assertEqual(uint64_be(1),b"\0\0\0\0\0\0\0\1")
 def test_raw_not_text(self): self.assertNotEqual(record_id("K","p",0,"00"*32),H("stt-record-v1",b"K",b"p",uint64_be(0),b"00"*32))
 def test_requirement_excludes_self_field(self):
  body = {"requirement_id": "old", "purpose": "deliver"}
  self.assertEqual(requirement_id("step", 0, body), requirement_id("step", 0, {"requirement_id": "new", "purpose": "deliver"}))
