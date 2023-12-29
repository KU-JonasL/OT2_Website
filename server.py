from flask import Flask, render_template, request
from csvOT2transfer import get_opentrons_script
from waitress import serve
import pandas as pd

app = Flask(__name__,template_folder="template/htmls")

@app.route('/')
@app.route('/index', methods=['POST'])
def index():

    file = request.files['myFile'] # Replace this with the actual filename used during upload

    if file.filename == '':
        return "No selected file"

    # Save the uploaded file to a location
    file.save("uploads/" + file.filename)
    
    csv_data = pd.read_csv("uploads/" + file.filename)

    return render_template('csv_template.html', csv_data=csv_data)


@app.route('/OT2transfer', methods=['POST'])
def get_OT2transfer():
    import pandas as pd

    ## Arguments past in
    protocol = request.form.get('protocol')
    user = request.form.get('user')
    samplenumber = request.form.get('samples')
    inputformat = request.form.get('inputformat') 
    outputformat = request.form.get('outputformat') 
    
    userdata = pd.read_csv("uploads/User_Data.csv")
    
    #csvfile = request.files['myFile'].filename
    
    
    ## Check for no user data input for library protocols
    #if protocol == "Library" and not bool(userdata.strip()):
    #    return "CSV file required for library building"
    
    ### Setting userdata to 0 for non-library protocols.
    #if not bool(userdata.strip()):
    #    userdata = 0

    finished_protocols = get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

    if bool(finished_protocols[1]):
        finished_protocol1 = finished_protocols[1]
    if bool(finished_protocols[2]):
        finished_protocol2 = finished_protocols[2]
    if bool(finished_protocols[3]):
        finished_protocol3 = finished_protocols[3]

    ## Check for code value (200 is good)
    #if not finished_protocols['cod'] == 200:
    #    return render_template('csv-not-found.html')
        
    
    return render_template(
        "OT2transfer.html",
        protocol,user,samplenumber,inputformat,outputformat,
        finished_protocol1 = finished_protocols[1],
        finished_protocol2 = finished_protocols[2],
        finished_protocol3 = finished_protocols[3]
    )
    

if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    