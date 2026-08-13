import unittest
from stt_mvp.schema import record_kind_for_schema,validate_record_kind
class SchemaTests(unittest.TestCase):
 def test_closed_mapping(self):
  self.assertEqual(record_kind_for_schema("RunRecord@1").value,"RunRecord")
  for s in ("RunRecord@2","runrecord@1","Step@1"):
   with self.assertRaises(ValueError): record_kind_for_schema(s)
 def test_no_inference(self):
  with self.assertRaises(ValueError): validate_record_kind("RunRecord@1","TaskRecord")
