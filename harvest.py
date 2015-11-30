# -*- coding: utf-8 -*-
import tweepy, json, abc, pickle, time
import ConfigParser
from objectpath import Tree
from threading import Thread
from feature_process import FeatureList, FeatureMapping
from text_processing import TextUtil, TextProcessing
import feature_process
from sklearn.cross_validation import train_test_split

config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

twitter_feature_lst = []
facebook_feature_lst = []
set_msg = set()
set_tweet = []
cred_label = {0:1,
2:0,
3:1,
4:1,
11:1,
20:1,
31:1,
39:1,
43:1,
48:1,
56:1,
57:1,
58:1,
81:1,
83:1,
92:1,
95:1,
}

is_not_important = {9:0,
13:0,
18:0,
19:0,
23:0,
28:0,
29:0,
33:0,
34:0,
37:0,
40:0,
44:0,
46:0,
50:0,
55:0,
59:0,
61:0,
62:0,
63:0,
72:0,
73:0,
78:0,
84:0,
86:0,
88:0,
97:0,
98:0,
103:0    
}

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
        s = api.search(q=keyword)
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
        twitter_keyword = ['คชาชาต', 'ประวิตร', 'อุดมเดช', 'เพื่อไทย', 'คุณหญิงจารุวรรณ',
                           'ราชภักดิ์', 'สุเทพ', 'คสช.', 'กินข้าว', 'แฟน', 'รัสเซีย',
                           'ขอนแก่นโมเดล', 'กรีซ', 'อาจารย์', 'ไปเที่ยวกัน', 'StrongerPor‬']
        result = TwitterHarvest.process(self, twitter_keyword)
        for t_msg in result:
            msg = t_msg[0]
            if msg not in set_msg:
                set_tweet.append(t_msg)
            set_msg.add(msg)

class HarvestRunner(Thread):
    
    def run(self):
        print 'start process'
        while len(set_tweet) < 100:
            print 'start harvest', len(set_tweet), ' set message ', len(set_msg)
            h = Harvest()
            h.process()
            time.sleep(40)
        pickle.dump(set_tweet, open('data/harvest.data', 'wb'))
        pickle.dump(set_msg, open('data/message.data', 'wb'))
        print 'end process'

def print_message():
    msg_lst = pickle.load(open('data/harvest.data', 'rb'))
    for i in range(0, len(msg_lst)):
        print '******************* ', i
        print msg_lst[i][0]
        print '************ end ******'
        
def create_training_data():
    data_lst = pickle.load(open('data/harvest.data', 'rb'))
    feature_process.feature_map['source'] = {'Google':1, 'Twitter for iPad':2, 'Echofon':3,
                                             'Bitly':4, 'twitterfeed':5, 'Twitter for iPhone':6,
                                             'Foursquare':7, 'Facebook':8, 'Twitter for Android':9,
                                             'TweetDeck':10, 'Twitter Web Client':11}
    feature_process.feature_map['geo'] = ['None']
    feature_process.feature_map['place'] = ['None']
    feature_process.feature_map['verified'] = ['False']
    feature_process.feature_map['geo_enabled'] = ['False']
    y = []
    x = []
    for i in range(0, len(data_lst)):        
        try:
            label = is_not_important[i]
        except Exception as e:
            label = 1
        
        data = data_lst[i]
        text = TextProcessing.process(data[0])
        source = FeatureMapping.mapping('source', data[1])
        re_tweet = data[2]
        geo = FeatureMapping.mapping_other('geo', data[3])
        place = FeatureMapping.mapping_other('place', data[4])
        hash_tag = data[5]
        media = data[6]
        verified = FeatureMapping.mapping_other('verified', data[7])
        follower = data[8]
        statues = data[9]
        desc = TextProcessing.process(data[10])
        friend = data[11]
        location = TextProcessing.process(data[12])
        geo_enabled = FeatureMapping.mapping_other('geo_enabled', data[13])
        
        y.append(label)
        x.append([text, source, re_tweet, geo, place, hash_tag, media, verified, follower, statues, desc, friend, location, geo_enabled])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import f1_score, accuracy_score
    clf = RandomForestClassifier()
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    fsc = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    print fsc, acc
    print y_pred
    print y_test
                    
if __name__ == '__main__':
    create_training_data()
#     for key, value in cred_label.iteritems():
#         print key
#     print_message()
#     HarvestRunner().start()
