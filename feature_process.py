
feature_map = {}

class FeatureMapping(object):
    
    def mapping(self, feature_name, feaure_value):
        return feature_map[feature_name][feaure_value]

class FeatureList(object):
    twitter_lst = ['$.text', '$.source', '$.retweet_count', '$.geo', '$.place',
                   'len("$.entities.hashtags")', 'len("$.entities.media")',
                   '$.user.verified', '$.user.followers_count', '$.user.statuses_count',
                   '$.user.description', '$.user.friends_count', '$.user.location',
                   '$.user.geo_enabled']
    facebook_lst = ['likes', 'share', 'comment']

    def __init__(self, socialmedia_type):
        self.socialmedia_type = socialmedia_type
        self.current = 0
        
    def __iter__(self):
        return self
    
    def next(self):
        ret = None
        if self.socialmedia_type == 'twitter':
            if self.current >= len(self.twitter_lst):
                raise StopIteration
            ret = self.twitter_lst[self.current]
            self.current += 1
        elif self.socialmedia_type == 'facebook':
            if self.current >= len(self.facebook_lst):
                raise StopIteration
            ret = self.facebook_lst[self.current]
            self.current += 1
        
        return ret

if __name__ == '__main__':
    f_lst = FeatureList('twitter')
    for f in f_lst:
        print f
