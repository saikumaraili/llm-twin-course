from unittest import TestCase, mock
from crawlers.github import GithubCrawler

class TestGithubCrawlerSimplified(TestCase):
	@mock.patch('crawlers.github.RepositoryDocument.save')
	def test_extract_simplified(self, mock_save):
		# Instantiate GithubCrawler
		crawler = GithubCrawler()
		
		# Call extract method with a sample GitHub URL
		crawler.extract(link='https://github.com/saikumaraili/job-probability.git', user='saikumaraili')
		
		# Assert RepositoryDocument.save was called
		self.assertTrue(mock_save.called)
		# Optionally, check if save was called with expected data
		# self.assertEqual(mock_save.call_args[0][0], expected_data)