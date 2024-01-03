from flask import Flask, render_template, request, redirect, send_file, send_from_directory, abort,url_for
#from csvOT2transfer import get_opentrons_script
from waitress import serve
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import tempfile 
import os
import io
import zipfile

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
        protocol = request.form["protocol"]
        user = request.form["user"]
        samplenumber = request.form["samples"]
        inputformat = request.form["inputformat"]
        outputformat = request.form["outputformat"]

        ## Naming
        today = datetime.today().strftime('%Y%m%d')
        naming = user+"_"+protocol+"_"+today 

        ## User Data redirect into a dataframe 
        userinput = pd.DataFrame({'Protocol':[protocol],'User':[user],'SampleNumber':[samplenumber],'InputFormat':[inputformat],'OutputFormat':[outputformat]})

        ## Looking for csv file contents.
        try:
            if request.files["myFile"] != "":
                userdata = request.files["myFile"]
                userdata.filename = secure_filename(userdata.filename)
                #userdata = pd.read_csv(userfile,header=0)
                #get_opentrons_script(protocol, user, samplenumber, inputformat, outputformat, userdata = userdata)


                zip_scripts_url = url_for('get_opentrons_script', protocol = protocol, user = user, samplenumber = samplenumber, inputformat = inputformat, outputformat = outputformat, userdata = userdata, _external=True)
    

            elif request.files["myFile"] == "" and protocol == "Library":
                return render_template("/csv-not-found")

            elif request.files["myFile"] == "":
                userdata = ""
                #get_opentrons_script(protocol, user, samplenumber, inputformat, outputformat, userdata = userdata)
                zip_scripts_url = url_for('get_opentrons_script', protocol = protocol, user = user, samplenumber = samplenumber, inputformat = inputformat, outputformat = outputformat, userdata = userdata, _external=True)
    

            ## Creating the python files
            return render_template(
                "/OT2transfer.html",
                protocol = userinput['Protocol'],
                user = userinput['User'],
                samplenumber = userinput['SampleNumber'],
                inputformat = userinput['InputFormat'],
                outputformat = userinput['OutputFormat'],
                get_opentrons_script = zip_scripts_url)
                    

                                                 
            
        
        except FileNotFoundError:
            return render_template("/index.html")
      
    
    else:
        return render_template("/index.html")




@app.route("/get_OT2_scripts")
def get_opentrons_script(protocol = "Extraction", user = "Antton", samplenumber = 96, inputformat = "LVLSXS200", outputformat = "LVLSXS200", userdata = 0):

    ## Creating a csv from User Inputs
    csv_user_input =pd.DataFrame({'Protocol':[protocol],
    'User':[user],
    'SampleNumber':[samplenumber],
    'InputFormat':[inputformat],
    'OutputFormat':[outputformat]})

    ## Prepare the inputs types for transfer
    csv_input_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_input.values])
    csv_input_raw_str = f"{', '.join(csv_user_input.columns)}\n{csv_input_values}"

    ## Cleaning up the inputs before merge
    csv_input_raw_str = csv_input_raw_str.replace("nan", "").replace("(", "").replace(")", "")


    ## Read data from User_Data.csv if available
    csv_user_data = pd.read_csv(userdata, header=0)

    ## Prepare the data types for transfer
    csv_data_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_data.values])
    csv_data_raw_str = f"{', '.join(csv_user_data.columns)}\n{csv_data_values}"

    ## Cleaning up the data before merge
    csv_data_raw_str = csv_data_raw_str.replace("nan", "").replace("(", "").replace(")", "")
    


    ###### Read the content of the TEMPLATE.py and loading it in a modified protocol ######

    #### DNA Extraction
    if csv_user_input['Protocol'][0] == "Extraction":
        ## Opening Template Extraction
        with open(f'template/templates_Protocols/Template_Protocol_DREX-NucleicAcidExtraction_OT2.py','r') as template_file:
            template_content = template_file.read()
        
        ## Modifying Template 
        modified_content = template_content.replace("1# User Input here", f"'''\n{csv_input_raw_str}\n'''")
        modified_content = modified_content.replace("1# User Data here", f"'''\n{csv_data_raw_str}'''")
        
        # Write the modified content to a Python script files

        with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
            temp_file.write(modified_content)
            temp_filename1 = temp_file.name

        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, mode="w") as zipf:
            # Add temporary files to the ZIP archive
            zipf.write(temp_filename1, arcname='finished_protocol1.py')

        # Move to the beginning of the ZIP data stream
        zip_data.seek(0)

        # Return the ZIP file as an attachment
        return send_file(zip_data,as_attachment=True,download_name='opentrons_scripts.zip',mimetype='application/zip')
        


    #### Library Building
    elif csv_user_input['Protocol'][0] == "Library":
        
        ## Opening Template; Covaris
        with open('template/templates_Protocols/Template_Protocol_CovarisSetup_OT2.py','r') as template_file:
            template_content1 = template_file.read()
        
        ## Modifying Template; Covaris
        modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content1 = modified_content1.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        # Write the modified content to temporary Python script files
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
            temp_file.write(modified_content1)
            temp_filename1 = temp_file.name


        ## Opening Template; Best-Library
        with open('template/templates_Protocols/Template_Protocol_BEST-Library_OT2.py','r') as template_file:
            template_content2 = template_file.read()
        
        ## Modifying Template; Best-Library
        modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content2 = modified_content2.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        # Write the modified content to temporary Python script files
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
            temp_file.write(modified_content2)
            temp_filename2 = temp_file.name


        ## Opening Template; Best Purification
        with open('template/templates_Protocols/Template_Protocol_BEST-Purification_OT2.py','r') as template_file:
            template_content3 = template_file.read()
        
        ## Modifying Template; Best Purification
        modified_content3 = template_content3.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content3 = modified_content3.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        # Write the modified content to temporary Python script files
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
            temp_file.write(modified_content3)
            temp_filename3 = temp_file.name
        
        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, mode="w") as zipf:
            # Add temporary files to the ZIP archive
            zipf.write(temp_filename1, arcname='finished_protocol1.py')
            zipf.write(temp_filename2, arcname='finished_protocol2.py')
            zipf.write(temp_filename3, arcname='finished_protocol3.py')

        # Move to the beginning of the ZIP data stream
        zip_data.seek(0)

        # Return the ZIP file as an attachment
        return send_file(zip_data,as_attachment=True,download_name='opentrons_scripts.zip',mimetype='application/zip')
        

    #### qPCR ####
    elif csv_user_input['Protocol'][0] == "qPCR":
        with open('template/templates_Protocols/Template_Protocol_qPCR_OT2.py','r') as template_file:
            template_content = template_file.read()
        
        modified_content = template_content.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content = modified_content.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        # Write the modified content to temporary Python script files
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
            temp_file.write(modified_content)
            temp_filename1 = temp_file.name
        
        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, mode="w") as zipf:
            # Add temporary files to the ZIP archive
            zipf.write(temp_filename1, arcname='finished_protocol1.py')
            
                # Move to the beginning of the ZIP data stream
        zip_data.seek(0)



    #### Index PCR; PCR ####
    elif csv_user_input['Protocol'][0] == "IndexPCR":
        
        ##Opening Template Protocol (Index PCR; PCR)
        with open('template/templates_Protocols/Template_Protocol_IndexPCR_OT2.py','r') as template_file:
            template_content1 = template_file.read()
        
        ## Modifying Template (Index PCR; PCR)
        modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content1 = modified_content1.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        # Write the modified content to temporary Python script files
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
            temp_file.write(modified_content1)
            temp_filename1 = temp_file.name


        ##Opening Template Protocol (Index PCR; Purification)
        with open('template/templates_Protocols/Template_Protocol_IndexPCR_Purfication_OT2.py','r') as template_file:
            template_content2 = template_file.read()
        
        ## Modifying Template (Index PCR; Purification)
        modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content2 = modified_content2.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        # Write the modified content to temporary Python script files
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
            temp_file.write(modified_content2)
            temp_filename2 = temp_file.name

        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, mode="w") as zipf:
            # Add temporary files to the ZIP archive
            zipf.write(temp_filename1, arcname='finished_protocol1.py')
            zipf.write(temp_filename2, arcname='finished_protocol2.py')
            
        # Move to the beginning of the ZIP data stream
        zip_data.seek(0)

        # Return the ZIP file as an attachment
        return send_file(zip_data,as_attachment=True,download_name='opentrons_scripts.zip',mimetype='application/zip')
    
    


    





    

























## Finished protocols
@app.route("/finished_protocol1/<path:naming>")
def finished_protocol1(naming):
    if naming != "":
        script_filename = f'template/client/pythonscripts/{naming}.py'
        return (send_from_directory(app.config["Client_Scripts"],script_filename, as_attachment=True))
    else: 
        return

@app.route("/finished_protocol2/<path:naming>")
def finished_protocol2(naming):
    if naming != "":
        script_filename = f'template/client/pythonscripts/{naming}.py'
        return (send_from_directory(app.config["Client_Scripts"],script_filename, as_attachment=True))
    else:
        return

@app.route("/finished_protocol3/<path:naming>")
def finished_protocol3(naming):
    if naming != "":
        script_filename = f'template/client/pythonscripts/{naming}.py'
        return send_from_directory(app.config["Client_Scripts"],script_filename, as_attachment=True)
    else:
        return




## csv / script download
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
    