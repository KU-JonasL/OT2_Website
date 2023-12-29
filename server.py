from flask import Flask, render_template, request
from csvOT2transfer import get_opentrons_script
from waitress import serve
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__,template_folder="template/htmls")

@app.route('/')
@app.route('/index', methods=['POST'])
def index():

    return render_template('index.html')


@app.route('/OT2transfer', methods=['POST'])
def get_OT2transfer():
   
    ## Arguments past in
    protocol = request.form.get('protocol')
    user = request.form.get('user')
    samplenumber = request.form.get('samples')
    inputformat = request.form.get('inputformat') 
    outputformat = request.form.get('outputformat') 
    
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
    
        

    
            ## Setting userdata to 0 for non-library protocols.
            if not bool(userdata.strip()):
                userdata = 0

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
        protocol = userinput['Protocol'],
        user = userinput['User'],
        samplenumber = userinput['SampleNumber'],
        inputformat = userinput['InputFormat'],
        outputformat = userinput['OutputFormat'],
        finished_protocol1 = finished_protocol1,
        finished_protocol2 = finished_protocol2,
        finished_protocol3 = finished_protocol3
    )
    

if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    