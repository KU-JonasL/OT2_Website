from flask import Flask, render_template, request
from csvOT2transfer import get_opentrons_script
from waitress import serve

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/OT2transfer')
def get_finished_protocols():
    ## Arguments past in
    protocol = request.args.get('protocol')
    user = request.args.get('user')
    samplenumber = request.args.get('samples')
    inputformat = request.args.get('inputformat') 
    outputformat = request.args.get('outputformat') 
    userdata = request.args.get('myFile')

    ## Check for no user data input for library protocols
    if protocol == "Library" and not bool(userdata.strip()):
        return "CSV file required for library building"
    
    ## Setting userdata to 0 for non-library protocols.
    if not bool(userdata.strip()):
        userdata = 0

    finished_protocols = get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

    if not bool(finished_protocols[1]):
        finished_protocol1 = finished_protocols[1]
    if not bool(finished_protocols[2]):
        finished_protocol2 = finished_protocols[2]
    if not bool(finished_protocols[3]):
        finished_protocol3 = finished_protocols[3]

    ## Check for code value (200 is good)
    if not finished_protocols['cod'] == 200:
        return render_template('csv-not-found.html')
        
    
    return render_template(
        "OT2transfer.html",
        title = finished_protocols['user']
    )
    
#    get_opentrons_script(name = user, template = "extraction", samples = "96"):
#    return render_template("")

if __name__ == "__main__":
    #app.run(host="0.0.0.0",port=8000)
    serve(app, host = "0.0.0.0", port = 8000)
    