'''
Created on Nov 30, 2015

@author: ubuntu
'''

class TextProcessing(object):
    
    @staticmethod
    def process(text):
        return len(text)

class TextUtil(object):
    
    @staticmethod
    def text_href(text):
        import re
        match = re.findall(r'<a href="(.*?)".*>(.*)</a>', text)
        if match:
            return match[0][1]
        else:
            return ''
        