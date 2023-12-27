from flask import Flask, render_template, request, redirect, url_for
from csvOT2transfer import get_opentrons_script
from waitress import serve
import pandas as pd

app = Flask(__name__,template_folder="template/htmls")

@app.route('/')
@app.route('/index', methods=['POST'])
def index():
    
    if request.method == 'POST':
        # Get form inputs
        protocol = request.form.get('protocol')
        user = request.form.get('user')
        samplenumber = request.form.get('samples')
        inputformat = request.form.get('inputformat') 
        outputformat = request.form.get('outputformat') 
                
        # Handle CSV file upload
        if 'myfile' in request.files:
            file = request.files['myfile']
            if file.filename != '':
                # Save the uploaded CSV file
                csv_filename = 'uploaded_file.csv'
                file.save(csv_filename)

                # Process CSV data
                userdata = pd.read_csv(csv_filename)
                
                # Generate Python file using user inputs and CSV data
                finished_protocols = get_opentrons_script(protocol,user,samplenumber,inputformat,outputformat,userdata)

                if not bool(finished_protocols[1]):
                    finished_protocol1 = finished_protocols[1]
                if not bool(finished_protocols[2]):
                    finished_protocol2 = finished_protocols[2]
                if not bool(finished_protocols[3]):
                    finished_protocol3 = finished_protocols[3]

                # Redirect to the OT2transfer route
                return redirect(url_for('OT2transfer'))

    return render_template("/index.html")


@app.route('/OT2transfer', methods=['POST'])
def get_OT2transfer():
    
    
    return render_template("OT2transfer.html",)
    

if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    