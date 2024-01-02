from flask import Flask, render_template, request, redirect, send_from_directory, abort,url_for
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





# A route to serve temporary files

@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
def index():

    return render_template('/index.html')



@app.route('/OT2transfer', methods=['POST', 'GET'])
def get_OT2transfer():
    
    ## Arguments pasted in
    protocol = request.form.get('protocol')[0]["Name"]
    user = request.form.get('user')[0]["Name"]
    samplenumber = request.form.get('samples')[0]   
    inputformat = request.form.get('inputformat')[0]["Name"]
    outputformat = request.form.get('outputformat')[0]["Name"]
        
    ## User Data redirect into a dataframe 
    userinput = pd.DataFrame({'Protocol':[protocol],'User':[user],'SampleNumber':[samplenumber],'InputFormat':[inputformat],'OutputFormat':[outputformat]})

    return render_template(
    "/OT2transfer.html",
    protocol = userinput['Protocol'],
    user = userinput['User'],
    samplenumber = userinput['SampleNumber'],
    inputformat = userinput['InputFormat'],
    outputformat = userinput['OutputFormat'],
    )
        


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
    