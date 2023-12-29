from flask import Flask, render_template, request, redirect, send_file, send_from_directory, abort
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

    if request.method == "POST":

        if request.files:
            
            myFile = request.files['myFile']

            filename = secure_filename(myFile.filename)

            if myFile.filename == "":
                return redirect(request.url)

            with tempfile.TemporaryDirectory() as temp_dir:
                myFile.save(os.path.join(temp_dir,filename))
                          
            
            return redirect(request.url)

    return render_template('index.html')



@app.route('/OT2transfer/<filename>', methods=['POST'])
def get_OT2transfer(filename):
    
    ## Arguments pasted in
    protocol = request.form.get('protocol')[0]
    user = request.form.get('user')[0]
    samplenumber = request.form.get('samples')[0]
    inputformat = request.form.get('inputformat')[0] 
    outputformat = request.form.get('outputformat')[0]
    
    ## User Data redirect into a dataframe 
    userinput = pd.DataFrame({'Protocol':[protocol],'User':[user],'SampleNumber':[samplenumber],'InputFormat':[inputformat],'OutputFormat':[outputformat]})

    ## Setting default values for the finished protocols
    finished_protocol1 = 0
    finished_protocol2 = 0
    finished_protocol3 = 0
    
    
    try:
        ## Folder for user csv data files
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file = os.path.join(temp_dir,filename)
            userdata = pd.read_csv(file)
        

        ## Incorprate user data and input into the csvOT2transfer function.
        if file != '':
                userdata = pd.read_csv(file)
                finished_protocols = get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

        elif file == '' and protocol != "Library":
                userdata = pd.read_csv(file)
                finished_protocols = get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

        elif file == '' and protocol == "Library":
            return render_template('/index.html')

        
        if bool(finished_protocols[1]):
            finished_protocol1 = finished_protocols[1]
            #download_temporary_file(finished_protocol1)  # Trigger download for protocol 1
        if bool(finished_protocols[2]):
            finished_protocol2 = finished_protocols[2]
            #download_temporary_file(finished_protocol2)  # Trigger download for protocol 2
        if bool(finished_protocols[3]):
            finished_protocol3 = finished_protocols[3]
            #download_temporary_file(finished_protocol3)  # Trigger download for protocol 3

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
            finished_protocol1=finished_protocols[1],
            finished_protocol2=finished_protocols[2],
            finished_protocol3=finished_protocols[3]
        )
    
    except FileNotFoundError:
        abort(404)
    
#def download_temporary_file(file_path):
    # Make an AJAX request to your Flask server
    #response = send_file(f'http://127.0.0.1:8000/get_temporary_file/{file_path}', as_attachment=True)
    # Handle the response to initiate file download
    #return response


## Script check
if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    