import pickle
from feature_process import FeatureMapping
import feature_process
from text_processing import TextProcessing
from sklearn.cross_validation import train_test_split

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
    print 'f1-score : ',fsc
    print 'accuracy : ',acc
    print y_pred
    print y_test
    
if __name__ == '__main__':
    create_training_data()
    
    