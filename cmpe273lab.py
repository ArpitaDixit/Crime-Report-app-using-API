import logging
logging.basicConfig(level=logging.DEBUG)
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
import time
import json
import urllib2
import datetime
from time import mktime
import dateutil.parser as dparser
import requests
from datetime import date
import collections

class Spotcrime(ServiceBase):

    @rpc(Float, Float, Float, _returns=Unicode)
    def checkcrime(self, lat, lon, radius):
        url = "https://api.spotcrime.com/crimes.json"
        url2 = "%s?lat=%s&lon=%s&radius=%s&key=." % (url, lat, lon, radius)
        muladd = False
        resp = requests.get(url2)
        json_data = json.loads(resp.content)

        crimestatdict = {}
        json_output = {
            "total_crime": 0,
            "the_most_dangerous_streets": [],
            "crime_type_count": {},
            "event_time_count": {
                "12:01am-3am": 0,
                "3:01am-6am": 0,
                "6:01am-9am": 0,
                "9:01am-12noon": 0,
                "12:01pm-3pm": 0,
                "3:01pm-6pm": 0,
                "6:01pm-9pm": 0,
                "9:01pm-12midnight": 0
            }
        }
        for crime in json_data['crimes']:
            if(crime['address'].find(" & ") != -1 or crime['address'].find(" AND ") != -1 ):
                muladd = True
                if(crime['address'].find(" AND ") != -1 ):
                    str1 = crime['address'].split(' AND ')
                else:
                    str1 = crime['address'].split(' & ')
                if(crimestatdict.has_key(str1[0])):
                    cnt1 = crimestatdict.get(str1[0])
                    cnt1 += 1
                    crimestatdict.update({str1[0]: cnt1})
                else:
                    crimestatdict.update({str1[0]: 1})
                if (crimestatdict.has_key(str1[1])):
                    cnt1 = crimestatdict.get(str1[1])
                    cnt1 += 1
                    crimestatdict.update({str1[1]: cnt1})
                else:
                    crimestatdict.update({str1[1]: 1})
            else:
                if (crimestatdict.has_key(crime['address'])):
                    cnt1 = crimestatdict.get(crime['address'])
                    cnt1 += 1
                    crimestatdict.update({crime['address']: cnt1})
                else:
                    crimestatdict.update({crime['address'] : 1})         
            if (json_output["crime_type_count"].has_key(crime['type'])):
                val = json_output["crime_type_count"].get(crime['type'])
                val +=1
                json_output["crime_type_count"].update({crime['type']: val})
            else:
                json_output["crime_type_count"].update({crime['type']: 1})
            date1 = dparser.parse(crime['date'])
            date1.strftime('%m/%d/%y %H:%M:%S')
            time1 = date1.time()
            if (time1 >= datetime.time(0, 1) and time1 <= datetime.time(3, 0)):
                val = json_output["event_time_count"].get("12:01am-3am")
                val +=1
                json_output["event_time_count"]["12:01am-3am"] = val
            if (time1 >= datetime.time(3, 1) and time1 <= datetime.time(6, 0)):
                val = json_output["event_time_count"].get("3:01am-6am")
                val +=1
                json_output["event_time_count"]["3:01am-6am"] = val
            if (time1 >= datetime.time(6, 1) and time1 <= datetime.time(9, 0)):
                val = json_output["event_time_count"].get("6:01am-9am")
                val +=1
                json_output["event_time_count"]["6:01am-9am"] = val
            if (time1 >= datetime.time(9, 1) and time1 <= datetime.time(12, 0)):
                val = json_output["event_time_count"].get("9:01am-12noon")
                val +=1
                json_output["event_time_count"]["9:01am-12noon"] = val
            if (time1 >= datetime.time(12, 1) and time1 <= datetime.time(15, 0)):
                val = json_output["event_time_count"].get("12:01pm-3pm")
                val +=1
                json_output["event_time_count"]["12:01pm-3pm"] = val
            if (time1 >= datetime.time(15, 1) and time1 <= datetime.time(18, 0)):
                val = json_output["event_time_count"].get("3:01pm-6pm")
                val +=1
                json_output["event_time_count"]["3:01pm-6pm"] = val
            if (time1 >= datetime.time(18, 1) and time1 <= datetime.time(21, 0)):
                val = json_output["event_time_count"].get("6:01pm-9pm")
                val +=1
                json_output["event_time_count"]["6:01pm-9pm"] = val
            if( time1 >= datetime.time(21,1) and ( time1 <= datetime.time(23,59)) or time1 == datetime.time(0,0) ):
                val = json_output["event_time_count"].get("9:01pm-12midnight")
                val +=1
                json_output["event_time_count"]["9:01pm-12midnight"] = val
        Topstreet = dict(collections.Counter(crimestatdict).most_common(3))
        json_output['the_most_dangerous_streets'] = Topstreet.keys()
        total_crime = json_output["event_time_count"]["12:01am-3am"] + json_output["event_time_count"]["3:01am-6am"] + json_output["event_time_count"]["6:01am-9am"] + json_output["event_time_count"]["9:01am-12noon"] + json_output["event_time_count"]['12:01pm-3pm'] + json_output["event_time_count"]["3:01pm-6pm"] + json_output["event_time_count"]['6:01pm-9pm'] + json_output["event_time_count"]["9:01pm-12midnight"]
        json_output['total_crime'] = total_crime
        if(total_crime == 0):
            json_output["event_time_count"]
        return json_output

application = Application([Spotcrime],
    tns='spyne.examples.crimereport',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)
if __name__ == '__main__':

    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)

    server = make_server('127.0.0.1', 8000, wsgi_app)

    server.serve_forever()
