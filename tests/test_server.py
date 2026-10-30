import importlib.util, pathlib, unittest
from unittest.mock import patch
p=pathlib.Path(__file__).resolve().parents[1]/'server.py'
s=importlib.util.spec_from_file_location('server',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
class ServerTests(unittest.TestCase):
 def test_list(self): self.assertEqual(len(m.handle({'method':'tools/list'})['tools']),2)
 def test_paths(self):
  for path in ['https://evil.test/story/api/x','/story/api/../x','/other']:
   with self.assertRaises(ValueError): m.query(path,{})
 def test_search(self):
  with patch.object(m,'query',return_value={'code':2000}) as q:
   result=m.handle({'method':'tools/call','params':{'name':'search_douyin_users','arguments':{'keyword':'AI'}}})
   q.assert_called_once_with('/story/api/dyData/searchUser',{'keyword':'AI','offset':0})
   self.assertNotIn('isError',result)
 def test_bad_argument(self):
  r=m.handle({'method':'tools/call','params':{'name':'search_douyin_users','arguments':{'keyword':''}}})
  self.assertTrue(r['isError'])
if __name__=='__main__': unittest.main()
