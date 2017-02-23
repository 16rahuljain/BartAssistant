#Import packages
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib as URL
import urllib.request, urllib.parse, urllib.error
import json
import os

from flask import Flask
from flask import request
from flask import make_response
from xml.dom.minidom import parseString

app = Flask(__name__)

#Define webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    #Accept request payload
    req = request.get_json(silent=True, force=True)                             
    
    print("Request:")
    print(json.dumps(req, indent=4))
    
    #Call business logic    
    res = processRequest(req)                                                   

    #Prepare response message
    res = json.dumps(res, indent=4)
    r = make_response(res)                                                     
    r.headers['Content-Type'] = 'application/json'
    print(r)
    return r

#Execute business logic
def processRequest(req):

    # Check for correct action invocked
    if req.get("result").get("action") != "BARTAssistant":                  
        return {}
    
    # Extract input parameters
    result = req.get("result")                                                  
    parameters = result.get("parameters")
    src_stn = (parameters.get("src_stn")).upper()
    end_point = (parameters.get("end_point")).upper()
    key = os.getenv('API_KEY')
    full_speech = ""
    
    if len(src_stn)!= 4 or len(end_point) != 4 :
        return{
            "speech": "station code is not valid, please try again",
            "displayText": "station code is not valid, please try again",
            "source": "API.Bart.gov"
        }
    # Prepare and call API URL
    link = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig="+src_stn+"&key="+key
    str_data = URL.urlopen(link).read()
    dom = parseString(str_data)
                      
    for etd in dom.getElementsByTagName('etd'):
        raw_dest = etd.getElementsByTagName('destination')[0].firstChild.nodeValue
        dest_abbr = etd.getElementsByTagName('abbreviation')[0].firstChild.nodeValue
        cln_dest = raw_dest.replace("/"," ")
        dur = ""
        ls_min = ""
        
        if dest_abbr == end_point:
            full_speech = ""
        for min in etd.getElementsByTagName('minutes'):
            dur = min.firstChild.data
            ls_min = ls_min + dur + ","
        cln_ls_min = ls_min.rstrip(",")
        raw_speech = "Next " + cln_dest +" Train arriving in"+ " " + cln_ls_min + " minutes. "
        full_speech = full_speech + raw_speech
            break
        else:
            full_speech = "Direct train is not available"
    speech = full_speech.replace("Leaving","0")        
    
    return {
        "speech": speech,
        "displayText": speech,
        "source": "API.Bart.gov"
    }

# Execute python app
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')


