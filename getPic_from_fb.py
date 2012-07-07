# -*- coding: utf-8 -*-

import os
import sys
import json
import urllib
import urllib2
from urllib import urlencode
import webbrowser

class FQL(object):

    ## This class was made by ptwobrussell.
    ## please check original code.
    ## https://github.com/ptwobrussell/Mining-the-Social-Web.git

    ENDPOINT = 'https://api.facebook.com/method/'

    def __init__(self, access_token=None):
        self.access_token = access_token

    def _fetch(cls, url, params=None):
        conn = urllib2.urlopen(url, data=urlencode(params))
        try:
            return json.loads(conn.read())
        finally:
            conn.close()

    def query(self, q):
        if q.strip().startswith('{'):
            return self.multiquery(q)
        else:
            params = dict(query=q, access_token=self.access_token, format='json')
            url = self.ENDPOINT + 'fql.query'
            return self._fetch(url, params=params)

    def multiquery(self, q):
        params = dict(queries=q, access_token=self.access_token, format='json')
        url = self.ENDPOINT + 'fql.multiquery'
        return self._fetch(url, params=params)


if __name__ == '__main__':
    try:
	    ## First, you need to assign facebook application and get access-token.
        ## please get the access token from following web-site and copy&paste to file.
        ## http://miningthesocialweb.appspot.com/
        ACCESS_TOKEN = open('out/facebook.access_token').read()
        if ACCESS_TOKEN == '':
            print >> sys.stderr, "Check your token"
            exit()

        if not os.path.isdir('picture'):
            os.mkdir('picture')

        q = "select target_id from connection where source_id = me() and target_type = 'user'"

    except IOError, e:
        try:
            print >> sys.stderr, "IO Error"
            exit()
        except IndexError, e:
            print >> sys.stderr, "Index Error"
            exit()

    fql = FQL(access_token=ACCESS_TOKEN)

    ## 1. get persons id
    print "get person id start"
    persons = [str(t['target_id']) for t in fql.query(q)]
    print json.dumps(persons, indent=4)


    ## 2. get album id
    print "get album id start"
    cnt = 1
    work = []
    for i in persons:
        u = 'select aid from album where owner = %s' % (i)
        work += fql.query(u)
        print cnt
        cnt += 1

    albums = [str(t['aid']) for t in work]
    print json.dumps(albums, indent=4)


    ## 3. get photo id
    print "get photo id start"
    cnt = 1
    work2 = []
    for al in albums:
        e = 'select object_id from photo where aid = "%s"' % (al)
        work2 += fql.query(e)
        print cnt
        cnt += 1

    photos = [str(t['object_id']) for t in work2]
    while 'error_code' in photos: photos.remove('error_code')
    while 'request_args' in photos: photos.remove('request_args')
    print json.dumps(photos, indent=4)
    print "Abount photo count: %s" % (len(photos))


    ## 4. get photo url
    print "get photo url start"
    cnt = 1
    photo_srcs = []
    N = 30
    for k in range(len(photos) / N + 1):
        r = 'select src, width, height from photo_src where photo_id in (%s)' \
               % (','.join(photos[k * N:(k + 1) * N]))
        photo_srcs += fql.query(r)
        print cnt
        cnt += 1


	## 5. select picture : width=320 only
    print "get photo via urllib start"
    cnt = 1
    photo_src = []
    for photo in photo_srcs:
        if photo['width'] == 320:
            photo_src.append('<img src="' + photo['src'] + '">')
            filename = photo['src'].split('/')

            ## get picture
            try:
                urllib.urlretrieve(photo['src'], os.path.join(os.getcwd(), 'picture', filename[-1]))
            except:
                print >> sys.stderr, "Can't get this  picture '%s'" % (filename[-1])

            print cnt
            cnt += 1 


    ## 6. create HTML
    print "create HTML start"
    HTML_TEMPLATE = 'template.html'
    OUT = os.path.basename('get_picture.html')

    html = open(HTML_TEMPLATE).read() % (' '.join(photo_src[0:]))
    f = open(os.path.join(os.getcwd(), 'out', OUT), 'w')
    f.write(html)
    f.close()

    ## if you want to show these pictures in a browser, please execute following  command at your terminal.
    ## `open out/get_picture.html`
    #webbrowser.open('file://' + f.name)

