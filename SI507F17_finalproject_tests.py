import unittest
import os
from SI507F17_finalproject import *


class TestYoutubeManager(unittest.TestCase):
    trend_manager = TrendManager()
    db_manager = trend_manager.youtube_db_manager

    def setUp(self):
        self.trend_manager.youtube_db_manager.truncate_tables()

    def test_query_gen(self):
        options1 = {'max_results': 12, 'region_code': 'US'}
        options2 = {'max_results': 12, 'region_code': 'KR'}
        options3 = {'max_results': 12, 'region_code': 'SE'}
        options4 = {'max_results': 12, 'region_code': 'CA'}
        expected_queries = [options1, options2, options3, options4]
        queries = self.trend_manager.reg_quries
        for i in range(4):
            expected_query = expected_queries[i]
            query = queries[i]
            self.assertEqual(query['max_results'], expected_query['max_results'])
            self.assertEqual(query['region_code'], expected_query['region_code'])

    def test_insert_to_db(self):
        # create region trend
        region_trend = self.create_sample_region_trend()
        # insert_to_db
        self.trend_manager.insert_to_db(region_trend)
        # check db result
        response = self.trend_manager.query_by_region('USA')
        self.assertTrue((response[0]['Title'] == 'video_test_title1') or (response[0]['Title'] == 'video_test_title2'))
        self.assertTrue((response[0]['ID'] == 'video_test_id1') or (response[0]['ID'] == 'video_test_id2'))

    def create_sample_video(self):
        video_info1 = {KIND: 'video', TITLE: 'video_test_title1', ID: 'video_test_id1'}
        video1 = Video(video_info1)
        return video1

    def test_video_create(self):
        video1 = self.create_sample_video()
        self.assertEqual(video1.id, 'video_test_id1')
        self.assertEqual(video1.kind, 'video')
        self.assertEqual(video1.title, 'video_test_title1')
        self.assertEqual(video1.url, 'http://www.youtube.com/embed/video_test_id1')

    def test_video_str(self):
        video1 = self.create_sample_video()
        video1_str = str(video1)
        self.assertEqual(video1_str, 'video_test_title1 (video_test_id1)')

    def test_video_repr(self):
        video1 = self.create_sample_video()
        video1_repr = repr(video1)
        self.assertEqual(video1_repr, 'video_test_id1')

    def create_sample_region_trend(self):
        video_info1 = {KIND: 'video', TITLE: 'video_test_title1', ID: 'video_test_id1'}
        video1 = Video(video_info1)
        video_info2 = {KIND: 'video', TITLE: 'video_test_title2', ID: 'video_test_id2'}
        video2 = Video(video_info2)
        video_list = [video1, video2]
        region_info = {CODE: 'US', REGION: 'USA'}
        region_trend = RegionTrend(region_info, video_list)
        return region_trend

    def test_region_trend_create(self):
        region_trend = self.create_sample_region_trend()
        self.assertEqual(region_trend.code, 'US')
        self.assertEqual(region_trend.region, 'USA')
        self.assertEqual(len(region_trend.videos), 2)

    def test_get_embed(self):
        region_trend = self.create_sample_region_trend()
        embedded = region_trend.get_info_to_embed()
        self.assertEqual(embedded[URLS][0], 'http://www.youtube.com/embed/video_test_id1')
        self.assertEqual(embedded[URLS][1], 'http://www.youtube.com/embed/video_test_id2')

    def test_repr(self):
        region_trend = self.create_sample_region_trend()
        self.assertEqual(repr(region_trend), 'USA')

    def test_init(self):
        self.assertTrue(self.db_manager.db_conn is not None)
        self.assertTrue(self.db_manager.db_conn is not None)

    def test_insert_region(self):
        region_data = {'Code': 'US', 'Name': 'USA'}
        self.db_manager.insert("Region", region_data)
        result = self.db_manager.select_all('Region')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Code'], 'US')
        self.assertEqual(result[0]['Name'], 'USA')

        # adding again will do nothing since the code is unique in the table
        self.db_manager.insert("Region", region_data)
        result = self.db_manager.select_all('Region')
        self.assertEqual(len(result), 1)

    def sample_region_to_db(self):
        region_data = {'Code': 'US', 'Name': 'USA'}
        self.db_manager.insert("Region", region_data)
        region_data = {'Code': 'KR', 'Name': 'Korea'}
        self.db_manager.insert("Region", region_data)

    def sample_video_to_db(self):
        video_data1 = {"ID": 'test_id1', "Title": 'test_title1', "Kind": 'video', "Code": 'US'}
        self.db_manager.insert("Video", video_data1)
        video_data2 = {"ID": 'test_id2', "Title": 'test_title2', "Kind": 'video', "Code": 'US'}
        self.db_manager.insert("Video", video_data2)

        video_data3 = {"ID": 'test_id1', "Title": 'test_title1', "Kind": 'video', "Code": 'KR'}
        self.db_manager.insert("Video", video_data3)

    def test_insert_video(self):
        self.sample_region_to_db()

        video_data = {"ID": 'test_id', "Title": 'test_title', "Kind": 'video', "Code": 'US'}
        self.db_manager.insert("Video", video_data)
        result = self.db_manager.select_all('Video')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['ID'], 'test_id')
        self.assertEqual(result[0]['Title'], 'test_title')
        self.assertEqual(result[0]['Code'], 'US')

        # insert same id with difference code should be a new entry
        video_data = {"ID": 'test_id', "Title": 'test_title', "Kind": 'video', "Code": 'KR'}
        self.db_manager.insert("Video", video_data)
        result = self.db_manager.select_all('Video')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['ID'], 'test_id')
        self.assertEqual(result[0]['Title'], 'test_title')
        self.assertEqual(result[0]['Code'], 'US')
        self.assertEqual(result[1]['ID'], 'test_id')
        self.assertEqual(result[1]['Title'], 'test_title')
        self.assertEqual(result[1]['Code'], 'KR')

    def test_inner_join_query(self):
        test_region = "USA"
        self.sample_region_to_db()
        self.sample_video_to_db()
        result = self.db_manager.inner_join_query(test_region)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Code'], 'US')
        self.assertEqual(result[1]['Code'], 'US')

    def tearDown(self):
        self.trend_manager.youtube_db_manager.truncate_tables()


class TestCache(unittest.TestCase):
    def setUp(self):
        self.cache_manager = CacheManager()
        self.cache_manager.clear_cache()

    def set_sample_resp(self, unique_ident, response):
        this_unique_ident = unique_ident
        this_response = response
        self.cache_manager.set_in_cache(this_unique_ident, this_response)

    def test_set_in_cache(self):
        unique_ident = 'https://www.googleapis.com/youtube/v3/videosmax_results-12_region_code-US'
        response = 'test response'
        self.set_sample_resp(unique_ident, response)
        self.assertTrue(unique_ident in self.cache_manager.cache_diction)
        self.assertTrue(response in self.cache_manager.cache_diction[unique_ident]['resp'])

    def test_set_in_cache_replace(self):
        unique_ident = 'https://www.googleapis.com/youtube/v3/videosmax_results-12_region_code-US'
        response = 'test response'
        self.set_sample_resp(unique_ident, response)
        response = 'test response_replace'
        self.set_sample_resp(unique_ident, response)

        self.assertEqual(len(self.cache_manager.cache_diction), 1)
        self.assertTrue(unique_ident in self.cache_manager.cache_diction)
        self.assertTrue(response in self.cache_manager.cache_diction[unique_ident]['resp'])
        self.assertTrue(len(self.cache_manager.cache_diction[unique_ident]['timestamp']) > 0)

    def test_get_from_cache(self):
        unique_ident = 'https://www.googleapis.com/youtube/v3/videosmax_results-12_region_code-US'
        response = 'test response'
        self.set_sample_resp(unique_ident, response)
        resp = self.cache_manager.get_from_cache(unique_ident)
        self.assertEqual(resp, 'test response')

    def tearDown(self):
        os.remove(CACHE_FNAME)


if __name__ == "__main__":
    unittest.main(verbosity=2)
