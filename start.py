# coding=utf-8

import urllib2
from BeautifulSoup import BeautifulSoup as bs


def parse():
    print "start parsing"
    print "-------------"

    url = "http://www.stolpersteine-stuttgart.de/index.php?docid=196&mid=66"
    print "search for URL: " + url

    seite = None
    try:
        seite = urllib2.urlopen(url).read()
    except:
        print 'ups, ein Fehler ;)'
        return -1

    soup = bs(seite)
    div = soup.find('div', {'id': 'seitenanker-top'})
    div.find

    print 'habe alle list elemente'

# Start funktion. hiermit fängt das programm an
if __name__ == "__main__":
    parse()
    pass