from flask import Flask, render_template, request, send_file
from csvOT2transfer import get_opentrons_script
from waitress import serve
from werkzeug.utils import secure_filename
import pandas as pd
import tempfile
import os

app = Flask(__name__,template_folder="template/htmls")

# A route to serve temporary files
@app.route('/get_temporary_file/<path:file_path>')
def get_temporary_file(file_path):
    # Construct the full path to the file
    # Ensure file_path is secure to prevent directory traversal attacks
    # Return the file using send_file
    return send_file(file_path, as_attachment=True)



@app.route('/')
@app.route('/index', methods=['POST'])
def index():

    return render_template('index.html')



@app.route('/OT2transfer', methods=['POST'])
def get_OT2transfer():
    



    ## Arguments past in
    protocol = request.form.get('protocol')[0]
    user = request.form.get('user')[0]
    samplenumber = request.form.get('samples')[0]
    inputformat = request.form.get('inputformat')[0] 
    outputformat = request.form.get('outputformat')[0]
    
    ## Arguments in a dataframe 
    userinput = pd.DataFrame({'Protocol':[protocol],'User':[user],'SampleNumber':[samplenumber],'InputFormat':[inputformat],'OutputFormat':[outputformat]})

    ## Setting default values for the finished protocols
    finished_protocol1 = 0
    finished_protocol2 = 0
    finished_protocol3 = 0
    
    ## Getting the user data and incorporates it along the user inputs into the csvOT2transfer function.
    if 'myFile' in request.files:
        file = request.files['myFile']
        if file.filename != '' or protocol != "Library":
            filename = secure_filename(file.filename)
            file.save(filename) 
            userdata = pd.read_csv(filename)
    
            
            
            finished_protocols = get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

    elif 'myFile' not in request.files and protocol != "Library":
        userdata = 0
        finished_protocols = get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

    elif 'myFile' not in request.files and protocol == "Library":
        return 'Library protocols needs csv data' 

    if bool(finished_protocols[1]):
        finished_protocol1 = finished_protocols[1]
        download_temporary_file(finished_protocol1)  # Trigger download for protocol 1
    if bool(finished_protocols[2]):
        finished_protocol2 = finished_protocols[2]
        download_temporary_file(finished_protocol2)  # Trigger download for protocol 2
    if bool(finished_protocols[3]):
        finished_protocol3 = finished_protocols[3]
        download_temporary_file(finished_protocol3)  # Trigger download for protocol 3

            ## Check for code value (200 is good)
            #if not finished_protocols['cod'] == 200:
            #    return render_template('csv-not-found.html')
        
    
    return render_template(
        "OT2transfer.html",
        protocol = userinput['Protocol'],
        user = userinput['User'],
        samplenumber = userinput['SampleNumber'],
        inputformat = userinput['InputFormat'],
        outputformat = userinput['OutputFormat'],
        finished_protocol1 = finished_protocol1,
        finished_protocol2 = finished_protocol2,
        finished_protocol3 = finished_protocol3
    )
    
def download_temporary_file(file_path):
    # Make an AJAX request to your Flask server
    response = send_file(f'http://127.0.0.1:8000/get_temporary_file/{file_path}', as_attachment=True)
    # Handle the response to initiate file download
    return response


## Script check
if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    