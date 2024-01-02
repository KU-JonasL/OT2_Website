from flask import Flask, render_template, request, redirect, send_file, send_from_directory, abort
from csvOT2transfer import get_opentrons_script
from waitress import serve
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import tempfile
import os

app = Flask(__name__,template_folder="template/htmls")


## App Config folders
app.config["Client_CSV"] = "static/client/csv"
app.config["Client_Scripts"] = "static/client/scripts"



# A route to serve temporary files

@app.route('/')
@app.route('/index', methods=['POST'])
def index():

    print("At index")

    if request.method == "POST":
        
        ##Naming of new template(s) selected (based on)
        protocolselect = request.form.get('protocol')[0]
        user = request.form.get('user')[0]
        today = datetime.today().strftime('%Y%m%d')
        naming = user+"_"+protocolselect+"_"+today+".csv"


        if request.files:
            
            myFile = request.files['myFile']

            filename = secure_filename(myFile.filename)

            if myFile.filename == "":
                return redirect(request.url)

            else:
                with open(f'static/client/csv/{naming}','w') as modified_csv:
                    new_csv = os.path.join(f'static/client/csv/{naming}', filename)
                    modified_csv.write(new_csv)
                            
            
            return send_from_directory

    return render_template('index.html')



@app.route('/OT2transfer/', methods=['POST'])
def get_OT2transfer():
    
                
    ## Arguments pasted in
    protocol = request.form.get('protocol')[0]
    user = request.form.get('user')[0]
    samplenumber = request.form.get('samples')[0]
    inputformat = request.form.get('inputformat')[0] 
    outputformat = request.form.get('outputformat')[0]
    

    ## User Data redirect into a dataframe 
    userinput = pd.DataFrame({'Protocol':[protocol],'User':[user],'SampleNumber':[samplenumber],'InputFormat':[inputformat],'OutputFormat':[outputformat]})

    ##Naming of new template(s) selected (based on)
    today = datetime.today().strftime('%Y%m%d')
    naming = user+"_"+protocol+"_"+today

    ## Exporting uer inputs
    with open(f'static/client/csv/{naming}_userinput.csv','w') as modified_csv:
        modified_csv.write(userinput)



    ## Downloading csv data
    file = get_csv(naming)
        

    try:
        ## Folder for user csv data files
        print("Trying the transferred file")
        
        userdata = pd.read_csv(file)
        

        ## Incorprate user data and input into the csvOT2transfer function.
        if file != '':
                get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

        elif file == '' and protocol != "Library":
                userdata = pd.read_csv(file)
                get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata = 0 )

        elif file == '' and protocol == "Library":
            return render_template('/index.html')

        finished_protocols = [0,0,0]

        if protocol == "Extraction":
            finished_protocols[0] = get_opentrons_script(f'{naming}_Extraction.py')

        elif protocol == "Library":
            finished_protocols[0] = get_opentrons_script(f'{naming}_covaris.py')
            finished_protocols[1] = get_opentrons_script(f'{naming}_BESTLibrary.py')
            finished_protocols[2] = get_opentrons_script(f'{naming}_BESTPurification.py')

        elif protocol == "qPCR":
            finished_protocols[0] = get_opentrons_script(f'{naming}_qPCR.py')

        elif protocol == "IndexPCR":
            finished_protocols[0] = get_opentrons_script(f'{naming}_IndexPCR.py')
            finished_protocols[1] = get_opentrons_script(f'{naming}_IndexPurification.py')
        
        
        
        return render_template(
            "/OT2transfer",
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
        print("Did not find a csv file")
        abort(404)

app.route("static/client/csv/<path:path>")
def get_csv(name):
    try:
        return send_from_directory(app.config["Client_CSV"],filename = name, as_attachment=True)
    except FileNotFoundError:
        abort(404)

app.route("static/client/scripts/<path:path>")
def get_OT2_script(name):
    try:
        return send_from_directory(app.config["Client_Scripts"],filename = name, as_attachment=True)
    except FileNotFoundError:
        abort(404)



## Script check
if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    