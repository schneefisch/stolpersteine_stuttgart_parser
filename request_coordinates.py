# coding=utf-8

import urllib
import urllib2
import simplejson
import csv

google_api_key = 'AIzaSyCu4u_tR8T4xxXF8synoXQlrLU-64u1X5M'


# noinspection SpellCheckingInspection
def get_geocode(address, name):
    """
    Diese Funktion holt für jede einzelne Straße die entsprechenden Geocoordinaten von Google

    Eine URL der geocode-api sieht so aus:
    https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY

    zurück kommt ein JSON objekt

    Antwort:
    {
       "results" : [
          {
             "address_components" : [
                {
                   "long_name" : "1600",
                   "short_name" : "1600",
                   "types" : [ "street_number" ]
                },
                {
                   "long_name" : "Amphitheatre Pkwy",
                   "short_name" : "Amphitheatre Pkwy",
                   "types" : [ "route" ]
                },
                {
                   "long_name" : "Mountain View",
                   "short_name" : "Mountain View",
                   "types" : [ "locality", "political" ]
                },
                {
                   "long_name" : "Santa Clara County",
                   "short_name" : "Santa Clara County",
                   "types" : [ "administrative_area_level_2", "political" ]
                },
                {
                   "long_name" : "California",
                   "short_name" : "CA",
                   "types" : [ "administrative_area_level_1", "political" ]
                },
                {
                   "long_name" : "United States",
                   "short_name" : "US",
                   "types" : [ "country", "political" ]
                },
                {
                   "long_name" : "94043",
                   "short_name" : "94043",
                   "types" : [ "postal_code" ]
                }
             ],
             "formatted_address" : "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
             "geometry" : {
                "location" : {
                   "lat" : 37.4224764,
                   "lng" : -122.0842499
                },
                "location_type" : "ROOFTOP",
                "viewport" : {
                   "northeast" : {
                      "lat" : 37.4238253802915,
                      "lng" : -122.0829009197085
                   },
                   "southwest" : {
                      "lat" : 37.4211274197085,
                      "lng" : -122.0855988802915
                   }
                }
             },
             "place_id" : "ChIJ2eUgeAK6j4ARbn5u_wAGqWA",
             "types" : [ "street_address" ]
          }
       ],
       "status" : "OK"
    }

    Status Codes:
    * OK = alles ok
    * ZERO_RESULTS = keine Ergebnisse für diese Adresse
    * OVER_QUERY_LIMIT = du hast zu viele Anfragen gestellt ;)
    * REQUEST_DENIED = Deine Anfrage wurde abgelehnt
    * INVALID_REQUEST = Etwas mit deiner Anfrage ist falsch, bsp die Parameter
    * UNKNOWN_ERROR = ein anderer Fehler ist aufgetreten

    bei etwas anderem als "OK" kann ein weiteres Feld
    "error_message" enthalten sein

    :param name: Name der gesuchten person
    :param address: Straße
    :return: lat, lng
    """
    # normalisiere die Adresse, d.h.
    parameters = {
        'key': google_api_key,
        'address': address + ', Stuttgart, Baden-Württemberg, Deutschland'
    }
    query_url = urllib.urlencode(parameters)
    url = 'https://maps.googleapis.com/maps/api/geocode/json?' + query_url

    json_response = simplejson.load(urllib2.urlopen(url))

    # prüfe zuerst den Status
    status = json_response['status']

    lat = -1
    # hier speichern wir den breitengrad

    lng = -1
    # hier speichern wir den längengrad

    if status == 'OK':
        # ergebnisse
        ergebnisse = json_response['results']

        # teste wie viele Ergebnisse wir bekommen haben,
        # es kann ja sein, dass es mehrere Straßen mit diesem Namen in Stuttgart gibt...
        if len(ergebnisse) > 1:
            counter = 0
            print '\n------------------------------------------------------------------------'
            print 'UPS, wir haben mehrere Ergebnisse für [' + name + ']. Bitte genau ansehen!!!'

            for location in ergebnisse:
                addresse_output = '%d: ' + location['formatted_address']
                print addresse_output % (counter)
                counter += 1

            print 'zum Beenden gib "q" ein.'
            nr = raw_input('Welches soll ich nehmen? (Python fängt bei 0 an zu zählen!): ')
            try:
                nr = int(nr)
            except:
                print 'konnte die nummer nicht konvertieren!'
                return lat, lng

            erg = ergebnisse[nr]

        else:
            erg = ergebnisse[0]

        # jetzt suchen wir den Längen- und Breitengrad
        lat = erg['geometry']['location']['lat']
        lng = erg['geometry']['location']['lng']

    else:
        print 'FEHLER: ' + status
        print 'Fehlermeldung: ' + json_response['error_message']

    return lat, lng


# noinspection SpellCheckingInspection
def run():
    # Schritt 1: lade das .csv-file mit den bisher gesammelten Namen und Adressen

    line_nr = 0
    # damit ich weiß in welcher Zeile ich bin

    new_csv = []
    # beinhaltet die Daten für die neue CSV-datei

    # copiere die inhalte aus der stolpersteine-csv in "new_csv"
    with open('stolpersteine.csv', 'r') as stolpersteine:
        filereader = csv.reader(stolpersteine)

        for line in filereader:
            new_csv.append(line)

    for line in new_csv:
        # Schritt 2: Für jede Adresse, lade die Geokoordinaten

        if line_nr == 0:
            # das ist die Titelzeile, die kann einfach kopiert werden
            if len(line) == 3:
                # dann sind bisher nur 'name', 'adresse', 'link' im titel.
                # füge 'lat' und 'long' hinzu, also breigengrad (lat) und längengrad (long)
                line.append('lat')
                line.append('long')

        elif len(line) == 5:
            # wenn bereits fünf stellen in der Zeile enthalten sind, dann haben wir hier shon
            # lat und long herausgesucht. überspringe die Zeile
            continue

        else:

            # wenn 5 felder eingetragen sind in dieser Zeile,
            # dann haben wir bereits lat und long in einem vorherigen Schritt!

            # für alle anderen Zeilen
            # die Adresse ist an der zweiten Stelle: (erinnerung: python fängt bei 0 an zu zählen!!)
            address = line[1]
            name = line[0]
            print 'suche adresse: ' + address

            lat, lng = get_geocode(address, name)

            # wenn wir -1 zurück bekommen, dann gab es einen Fehler und wir stoppen die Bearbeitung!
            if lat == -1:
                print 'stoppe bearbeitung'

                # beende die schleife komplett
                break

            else:
                # füge die beiden werte zur Zeile hinzu
                line.append(lat)
                line.append(lng)

        new_csv[line_nr] = line
        # die neue (erweiterte) Zeile wird zur neuen Datei hinzugefügt

        line_nr += 1
        # zähle 1 zur zeilennummer hinzu

    # Schritt 3: Schreibe die neuen Koordinaten zurück in die Datei
    with open('stolpersteine.csv', 'w') as stolpersteine:
        filewriter = csv.writer(stolpersteine)

        for line in new_csv:
            filewriter.writerow(line)
            # wir überschreiben einfach die bisherige zeile mit den neuen Daten

    pass


if __name__ == "__main__":
    run()
