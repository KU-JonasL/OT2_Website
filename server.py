from flask import Flask, render_template, request, redirect, send_file, send_from_directory, abort,url_for
from csvOT2transfer import get_opentrons_script
from waitress import serve
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import tempfile 
import os

app = Flask(__name__,template_folder="template/htmls")


    


app.config["Client_CSV"] = os.path.join(app.root_path, 'template', 'client', 'csv')
app.config["Client_Scripts"] = os.path.join(app.root_path, 'template', 'client', 'pythonscripts')



@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
def index():

    return render_template('/index.html')



@app.route('/OT2transfer', methods=['POST', 'GET'])
def get_OT2transfer():
    
    if request.method == "POST":

        ## Arguments pasted in
        protocol = request.form['protocol']
        user = request.form['user']
        samplenumber = request.form['samples']
        inputformat = request.form['inputformat']
        outputformat = request.form['outputformat']

        ## Naming
        today = datetime.today().strftime('%Y%m%d')
        naming = user+"_"+protocol+"_"+today 

        ## User Data redirect into a dataframe 
        userinput = pd.DataFrame({'Protocol':[protocol],'User':[user],'SampleNumber':[samplenumber],'InputFormat':[inputformat],'OutputFormat':[outputformat]})

        ## Looking for csv file contents.
        try:
            if request.files['myFile'] != "":
                userdata = request.files['myFile']
                userdata.filename = secure_filename(userdata.filename)
                #userdata = pd.read_csv(userfile,header=0)
                get_opentrons_script(protocol, user, samplenumber, inputformat, outputformat, userdata = userdata)

            elif request.files['myFile'] == "" and protocol == "Library":
                return render_template("/index")

            elif request.files['myFile'] == "":
                userdata = ""
                get_opentrons_script(protocol, user, samplenumber, inputformat, outputformat, userdata = userdata)

            ## Creating the python files
            if protocol == "Extraction":
                finished_protocol1 = get_OT2_script(f'{naming}_Extraction.py')
                

            elif protocol == "Library":
                finished_protocol1 = get_OT2_script(f'{naming}_covaris.py')
                finished_protocol2 = get_OT2_script(f'{naming}_BESTLibrary.py')
                finished_protocol3 = get_OT2_script(f'{naming}_BESTPurification.py')

            elif protocol == "qPCR":
                finished_protocols1 = get_OT2_script(f'{naming}_qPCR.py')

            elif protocol == "IndexPCR":
                finished_protocols1 = get_OT2_script(f'{naming}_IndexPCR.py')
                finished_protocols2 = get_OT2_script(f'{naming}_IndexPurification.py')
            

            return render_template(
            "/OT2transfer.html",
            protocol = userinput['Protocol'],
            user = userinput['User'],
            samplenumber = userinput['SampleNumber'],
            inputformat = userinput['InputFormat'],
            outputformat = userinput['OutputFormat'],
            finished_protocol1 = finished_protocol1,
            finished_protocol2 = finished_protocol2,
            finished_protocol3 = finished_protocol3)
        
        except:
            return render_template("/index")


        
    
    else:
        return render_template("/index")
        


@app.route("/get-csv/<path:name>")
def get_csv(name):
    try:
        return send_from_directory(app.config["Client_CSV"], name, as_attachment=True)
    except FileNotFoundError:
        print("Did not find csv file")
        abort(404)

@app.route("/get-script/<path:name>")
def get_OT2_script(name):
    try:
        return send_from_directory(app.config["Client_Scripts"], name, as_attachment=True)
    except FileNotFoundError:
        print("Did not find csv file")
        abort(404)


## Script check
if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    