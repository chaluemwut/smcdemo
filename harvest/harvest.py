# -*- coding: utf-8 -*-
import tweepy, json, abc, pickle, time
import ConfigParser
from objectpath import Tree
from threading import Thread
from feature_process import FeatureList
from text_processing import TextUtil

config = ConfigParser.ConfigParser()
config.readfp(open('../config.ini'))

twitter_feature_lst = []
facebook_feature_lst = []
set_msg = set()
set_tweet = []

class BaseHarvest():
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def process(self, keyword_lst):
        pass
    

class TwitterHarvest(BaseHarvest):
    auth = tweepy.OAuthHandler(config.get('twitter', 'key'), config.get('twitter', 'key_password'))
    auth.set_access_token(config.get('twitter', 'access_tokey_key'), config.get('twitter', 'access_tokey_password'))
    
    def trends_harvest(self):
        api = tweepy.API(self.auth)
        json_data = api.trends_place(23424960)
        data = json_data[0]
        trends = data['trends']
        ret_lst = []
        for trend in trends:
            trand_data = trend['name']
            ret_lst.append(trand_data)
        return ret_lst
        
    def call_api(self, keyword):
        api = tweepy.API(self.auth)
        s = api.search(q=keyword, count=1)
        feature_value_list = []
        feature_data = []
        for tweet in s:
            tree = Tree(tweet._json)
            feature_list = FeatureList('twitter')
            for feature in feature_list:
                f_value = tree.execute(feature)
                if feature == '$.source':
                    f_value = TextUtil.text_href(f_value)
                feature_value_list.append(f_value)
            feature_data.append(feature_value_list)
        return feature_data
    
    def process(self, keyword_lst):
        BaseHarvest.process(self, keyword_lst)
        if len(keyword_lst) == 0:
            key_word_lst = self.trends_harvest()
        else:
            key_word_lst = keyword_lst
        result = []
        for key_word in key_word_lst:
            result.extend(self.call_api(key_word))
        return result
        
class FacebookHarvest(BaseHarvest):
    
    def process(self, keyword_lst):
        BaseHarvest.process(self)
    
class Harvest(TwitterHarvest, FacebookHarvest):
    
    def process(self):
        twitter_keyword = ['คชาชาต', 'ประวิตร', 'อุดมเดช', 'เพื่อไทย', 'คุณหญิงจารุวรรณ', 'ราชภักดิ์', 'สุเทพ']
        result = TwitterHarvest.process(self, twitter_keyword)
        for t_msg in result:
            msg = t_msg[0]
            if msg not in set_msg:
                set_tweet.append(t_msg)
            set_msg.add(msg)

class HarvestRunner(Thread):
    
    def run(self):
        print 'start process'
        while len(set_tweet) < 500:
            print 'start harvest', len(set_tweet), ' set message ', len(set_msg)
            h = Harvest()
            h.process()
            time.sleep(10)
        pickle.dump(set_tweet, open('data/harvest.data', 'wb'))
        pickle.dump(set_msg, open('data/message.data', 'wb'))
        print 'end process'
           
if __name__ == '__main__':
    HarvestRunner().start()