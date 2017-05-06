# coding=utf-8

import urllib
import urllib2
import simplejson
import csv
import string

WRONG_COORDINATES_CSV = 'known_wrong_coordinates.csv'

STOLPERSTEINE_CSV = 'stolpersteine.csv'

GOOGLE_API_KEY = 'AIzaSyCu4u_tR8T4xxXF8synoXQlrLU-64u1X5M'


def load_csv(filename):
    data = []
    # beinhaltet die Daten für die neue CSV-datei

    # copiere die inhalte aus der stolpersteine-csv in "new_csv"
    with open(filename, 'r') as stolpersteine:
        filereader = csv.reader(stolpersteine)

        for line in filereader:
            data.append(line)
    return data


# noinspection SpellCheckingInspection
def get_geocode(address):
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

    :param address: Straße
    :return: lat, lng
    """
    # normalisiere die Adresse, d.h.
    parameters = {
        'key': GOOGLE_API_KEY,
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

        # wir nehmen "by default" das erste ergebnis. in 95% der Fälle ist dies korrekt.
        # die anderen Fälle werden mit der Zeit in "known_wrong_coordingates.csv" gepflegt.
        erg = ergebnisse[0]

        # jetzt suchen wir den Längen- und Breitengrad
        lat = erg['geometry']['location']['lat']
        lng = erg['geometry']['location']['lng']

    else:
        print 'FEHLER: ' + status
        # print 'Fehlermeldung: ' + json_response['status']

    return lat, lng


def address_is_in_list(name, street, addresslist):
    for line in addresslist:
        if string.lower(name) == string.lower(line[0]) and string.lower(street) == string.lower(line[1]):
            print 'Found duplicate: {0}, {1}'.format(name, street)
            return True, line[3], line[4]
    return False, None, None


# noinspection SpellCheckingInspection
def run():
    # Schritt 1: lade das .csv-file mit den bisher gesammelten Namen und Adressen

    line_nr = 0
    # damit ich weiß in welcher Zeile ich bin

    new_csv = load_csv(STOLPERSTEINE_CSV)
    known_wrong_addresses = load_csv(WRONG_COORDINATES_CSV)

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

            # prüfe ob die addresse schon in den "known_wrong_coordinates" ist.
            duplicate, knownlat, knownlng = address_is_in_list(line[0], line[1], known_wrong_addresses)

            if duplicate:
                # wenn es eine bekannte falsche addresse ist, nutze die bekannten Werte
                line.append(knownlat)
                line.append(knownlng)

            else:
                # für alle anderen Zeilen
                # die Adresse ist an der zweiten Stelle: (erinnerung: python fängt bei 0 an zu zählen!!)
                address = line[1]
                print 'suche adresse: ' + address

                lat, lng = get_geocode(address)

                # wenn wir -1 zurück bekommen, dann gab es einen Fehler und wir stoppen die Bearbeitung!
                if lat == -1:
                    print 'Fehler trat auf. füge leere Werte hinzu'
                    line.append("")
                    line.append("")

                    # beende die schleife komplett
                    # break
                    continue

                else:
                    # füge die beiden werte zur Zeile hinzu
                    line.append(lat)
                    line.append(lng)

        new_csv[line_nr] = line
        # die neue (erweiterte) Zeile wird zur neuen Datei hinzugefügt

        line_nr += 1
        # zähle 1 zur zeilennummer hinzu

    # Schritt 3: Schreibe die neuen Koordinaten zurück in die Datei
    with open(STOLPERSTEINE_CSV, 'w') as stolpersteine:
        filewriter = csv.writer(stolpersteine)

        for line in new_csv:
            filewriter.writerow(line)
            # wir überschreiben einfach die bisherige zeile mit den neuen Daten

    pass


if __name__ == "__main__":
    run()
