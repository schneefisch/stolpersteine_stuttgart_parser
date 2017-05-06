# coding=utf-8

import urllib2
import unicodecsv
from BeautifulSoup import BeautifulSoup as bs


def beautify_string(string):
    """
    diese Methode entfernt mir die Sonderzeichen, z.B. "&nbsp;" (leerzeichen) aus dem text.
    auch werden "," am Anfang und "ß" korrekt gemacht

    :param string:  der text / name der verschoenert werden soll
    :return: string
    """

    string = string.replace("&nbsp;", " ").replace("\\xdf", "ss").replace(",", " ")
    string = string.strip()

    if string[0] == ",":
        string = string[1:]

    string = string.strip()
    return string


def parse():
    """
    Das ist der eigentliche Parser

    -ich rufe die Stolpersteine-stuttgart website auf
    - lade alle stolpersteine
    - suche die Namen, Links und Straßen von den Stolpersteinen
    - speichere das in einer .csv datei ab

    :return:
    """

    print "start parsing"
    print "-------------"

    base_url = "http://www.stolpersteine-stuttgart.de/"
    url = "index.php?docid=196&mid=66"
    print "search for URL: " + base_url + url

    stolpersteine = []

    try:
        seite = urllib2.urlopen(base_url + url).read()
    except:
        print 'ups, ein Fehler ;)'
        return -1

    soup = bs(seite)
    # soup.prettify(formatter=lambda s: s.replace(u'\xa0', ' '))
    div = soup.find('div', {'class': 'SingleDoc KategorieDokument'})
    # print div
    list_elements = div.findAll('li')

    for element in list_elements:

        # check if the element has any content
        content_list = element.contents

        link = ""
        name = ""
        street = ""

        for content in content_list:
            try:
                tag_name = content.name
            except:
                tag_name = -1

            if tag_name == -1:
                # check for text element
                # it probably is the street-name if the length of the text is something larger than 3
                if len(content) > 3:
                    street = beautify_string(content)

                continue

            elif tag_name == "a":
                link = content.get('href')

                # check if the link already starts with "http".
                # if yes, then it is a direct link, for example for http://stolpersteine-cannstatt.de
                # otherwise add base-url
                if not link.startswith('http', 0, len(link)):
                    link = base_url + link

            elif tag_name == "span":
                link = ""

            else:
                continue

            # find name of the stone
            name = beautify_string(content.text)

        # store into list
        stolpersteine.append([name, street, link])

    print stolpersteine

    # speichere stolpersteine in .csv datei
    with open('stolpersteine.csv', 'wb') as myfile:
        wr = unicodecsv.writer(myfile)

        wr.writerow(["name", "strasse", "link"])

        for stein in stolpersteine:
            wr.writerow(stein)

    pass


# Start funktion. hiermit fängt das programm an
if __name__ == "__main__":
    parse()
