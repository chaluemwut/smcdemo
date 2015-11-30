'''
Created on Nov 30, 2015

@author: ubuntu
'''

class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''

class TextUtil(object):
    
    @staticmethod
    def text_href(text):
        import re
        match = re.findall(r'<a href="(.*?)".*>(.*)</a>', text)
        if match:
            return match[0][1]
        else:
            return ''
        