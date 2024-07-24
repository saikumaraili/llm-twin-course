import unittest
from unittest.mock import patch, MagicMock
from crawlers.github import GithubCrawler
from documents import RepositoryDocument

class TestGithubCrawler(unittest.TestCase):
	@patch('tempfile.mkdtemp', return_value='/tmp/fake_dir')
	@patch('os.chdir')
	@patch('subprocess.run')
	@patch('os.walk', return_value=[('/tmp/fake_dir/repo', [], ['README.md'])])
	@patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='content')
	@patch('shutil.rmtree')
	@patch('logging.info')
	def test_extract(self, mock_log, mock_rmtree, mock_open, mock_walk, mock_run, mock_chdir, mock_mkdtemp):
		# Mock the model's save method
		RepositoryDocument.save = MagicMock()

		crawler = GithubCrawler()
		crawler.extract('https://github.com/saikumaraili/job-probability', user='test_user')

		# Assert that the repository document was created with expected content
		RepositoryDocument.save.assert_called_once()
		saved_instance = RepositoryDocument.save.call_args[0][0]
		self.assertEqual(saved_instance.name, 'repo')
		self.assertEqual(saved_instance.link, 'https://github.com/saikumaraili/job-probability')
		self.assertEqual(saved_instance.owner_id, 'test_user')
		self.assertIn('README.md', saved_instance.content)
		self.assertEqual(saved_instance.content['README.md'], 'content')

		# Additional assertions can be made on the mocked methods if necessary

if __name__ == '__main__':
	unittest.main()