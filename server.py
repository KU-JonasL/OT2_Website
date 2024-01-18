from flask import Flask, render_template, request, redirect, send_file, abort, url_for
import requests
from waitress import serve
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import os
import io
import tempfile
import zipfile

app = Flask(__name__,template_folder="template")


@app.route('/', methods = ["GET","POST"])
@app.route('/index.html', methods = ["GET","POST"])
def index():
    return render_template('/index.html')


@app.route('/OT2transfer.html', methods = ["GET","POST"])
def get_OT2transfer():
    
    if request.method == "POST":

        ## Arguments pasted in
        protocol = request.form.get('protocol')
        user = request.form.get('user')
        samplenumber = int(request.form.get('samples'))
        inputformat = request.form.get('inputformat')
        outputformat = request.form.get('outputformat')

        ## Naming
        today = datetime.today().strftime('%Y%m%d')
        naming = user+"_"+protocol+"_"+today 

        ## User Data redirect into a dataframe 
        userinput = pd.DataFrame({'Protocol':[protocol],'User':[user],'SampleNumber':[samplenumber],'InputFormat':[inputformat],'OutputFormat':[outputformat]})

        ## Looking for csv file contents.
        try:
            ## If there is a csv data file
            if bool(request.files['myFile']):
                
                ## Set uploaded file and secure name
                uploaded_file = request.files['myFile']  # Access the file using the key
                uploaded_file.filename = secure_filename(uploaded_file.filename)
                
                ## Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                    temp_file_path = temp_file.name
                    uploaded_file.save(temp_file_path)

                    ## Load and cleanup for the userdata
                    temp_userdata_csv = pd.read_csv(temp_file_path)
                    #userdata = [tuple(temp_userdata_csv.columns)] + [tuple(row) for row in temp_userdata_csv.values]

                    csv_data_values = "\n".join([f"({', '.join(map(str, row))})" for row in temp_userdata_csv.values])
                    csv_data_raw_str = f"{', '.join(temp_userdata_csv.columns)}\n{csv_data_values}"
                    userdata = csv_data_raw_str.replace("nan", "").replace("(", "").replace(")", "")
                    
                    ## Convert a semi-colon seperated file (',' for '.' [Digits] and ';' for ',' [cell/tab separator])
                    #if userdata.find("Sample Number; Well Position"):
                    #    userdata = userdata.replace(",",".")
                    #    userdata = userdata.replace(";",",")

                    ## Delete the temporary file
                    #os.unlink(temp_file_path)
                
                ## Create URL for zipfolder
                zip_scripts_url = url_for('get_opentrons_script', protocol=protocol, user=user, samplenumber=samplenumber, inputformat=inputformat, outputformat=outputformat, userdata=userdata, _external=True)
    

            ## If there is not a csv data file, and the protocol type is library - There need to be a user csv file for library building protocols 
            elif request.files['myFile'] == "" and protocol == "Library":
                return render_template("/csv-not-found.html")

            ## If there no user csv data file and the protocol is not for library building
            elif request.files['myFile'] == "" and protocol != "Library":
                userdata = "1"
                get_opentrons_script(protocol, user, samplenumber, inputformat, outputformat, userdata = userdata)
                zip_scripts_url = url_for('get_opentrons_script', protocol=protocol, user=user, samplenumber=samplenumber, inputformat=inputformat, outputformat=outputformat, userdata=userdata, _external=True)
    

            ## Render the OT2transfer html page 
            return render_template(
                "/OT2transfer.html",
                protocol = userinput['Protocol'],
                user = userinput['User'],
                samplenumber = userinput['SampleNumber'],
                inputformat = userinput['InputFormat'],
                outputformat = userinput['OutputFormat'],
                userdata = userdata,
                naming = naming,
                get_opentrons_script = zip_scripts_url,
                )

        except FileNotFoundError:
            return render_template("/index.html")
    else:
        return render_template("/index.html")



#/<path:user>/<path:protocol>/<path:samples>/<path:inputformat>/<path:outputformat>/<path:userdata>
@app.route("/get_OT2_scripts/<user>/<protocol>/<samplenumber>/<inputformat>/<outputformat>/<userdata>", methods = ["GET","POST"])
def get_opentrons_script(protocol, user, samplenumber, inputformat, outputformat, userdata):

    ## Creating a data frame of User Inputs
    csv_user_input =pd.DataFrame({'Protocol':[protocol],
    'User':[user],
    'SampleNumber':[samplenumber],
    'InputFormat':[inputformat],
    'OutputFormat':[outputformat]})

    ## Prepare the inputs types for transfer
    csv_input_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_input.values])
    csv_input_raw_str = f"{', '.join(csv_user_input.columns)}\n{csv_input_values}"
    csv_input_raw_str = csv_input_raw_str.replace("nan", "").replace("(", "").replace(")", "")


    ## Read and Prepare the user data for transfer
    #csv_user_data = pd.DataFrame(userdata[1:], columns = userdata[0])
    #csv_data_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_data.values])
    #csv_data_raw_str = f"{', '.join(csv_user_data.columns)}\n{csv_data_values}"
    #csv_data_raw_str = csv_data_raw_str.replace("nan", "").replace("(", "").replace(")", "").replace(";",",").replace(",",".")


    ## Naming generation for zipfile and zipfolde
    today = datetime.today().strftime('%Y%m%d')
    naming = user+"_"+protocol+"_"+today 

    ## Preparing zip folder generation
    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode="w") as zipf:
    
        #### Adds required custom labware definitions, as needed.
        ## 
        if inputformat or outputformat == "LVLSXS200":
            static_pdf_content = open('static\custom_labware\LVLXSX200_wellplate_200ul.json', 'rb').read()
            zipf.writestr('LVLXSX200_wellplate_200ul.json', static_pdf_content)

        ###### Read the content of the TEMPLATE.py and loading it in a modified OT2 protocol ######
        #### DNA Extraction
        if protocol == "Extraction":
            
            ## Opening and Modifying Template Extraction
            template_content = open(f'static/OT2_protocols/Template_Protocol_DREX-NucleicAcidExtraction_OT2.py','r').read()
            modified_content = template_content.replace("1# User Input here", f"'''\n{csv_input_raw_str}\n'''")
            modified_content = modified_content.replace("1# User Data here", f"'''\n{userdata}'''")

            # Write the modified content to temporary Python script files
            zipf.writestr(f'{naming}_Extraction.py', modified_content.encode())
            
            ## Add 21mL Deep well plate to zipfolder
            static_pdf_content = open('static\custom_labware\deepwellreservoir_12channel_21000ul.json', 'rb').read()
            zipf.writestr('static_pdf.pdf', static_pdf_content)

            ## Add SOP for extraction to zipfolder
            static_sop_content = open('static\SOPs\SOP_Template_V1.0.0.docx', 'rb').read()
            zipf.writestr('SOP_pdf.pdf', static_sop_content)


        
        #### Library Building
        elif protocol == "Library":
            
            ## Opening and Modifying Template Covaris fargmentation
            template_content1 =  open('static/OT2_protocols/Template_Protocol_CovarisSetup_OT2.py','r').read()
            modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content1 = modified_content1.replace("1# User Data here", f"'''{userdata}'''")

            ## Opening and Modifying Template Library-Building
            template_content2 = open('static/OT2_protocols/Template_Protocol_BEST-Library_OT2.py','r').read()
            modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content2 = modified_content2.replace("1# User Data here", f"'''{userdata}'''")

            ## Opening and Modifying Template Library-Purification
            template_content3 =  open('static/OT2_protocols/Template_Protocol_BEST-Purification_OT2.py','r').read()
            modified_content3 = template_content3.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content3 = modified_content3.replace("1# User Data here", f"'''{userdata}'''")

            # Write the modified content to temporary Python script files
            zipf.writestr(f'{naming}_fragmentation.py', modified_content1.encode())
            zipf.writestr(f'{naming}_library-building.py', modified_content2.encode())
            zipf.writestr(f'{naming}_library-purification.py', modified_content3.encode())

            
            ## Add 5mL eppendorf in OT2 15 rack to zipfolder
            static_pdf_content = open('static\custom_labware\opentronsrack_15_tuberack_5000ul.json', 'rb').read()
            zipf.writestr('static_pdf.pdf', static_pdf_content)
            ## Add Covaris plate to zipfolder
            static_pdf_content = open('static\custom_labware\Covaris_96afatubet_wellplate_200ul.json', 'rb').read()
            zipf.writestr('static_pdf.pdf', static_pdf_content)
            ## Add 21mL Deep well plate to zipfolder
            static_pdf_content = open('static\custom_labware\deepwellreservoir_12channel_21000ul.json', 'rb').read()
            zipf.writestr('static_pdf.pdf', static_pdf_content)

                

        #### qPCR ####
        elif protocol == "qPCR":
            ##Opening and Modifying Template Protocol qPCR
            template_content = open('static/OT2_protocols/Template_Protocol_qPCR_OT2.py','r').read()
            modified_content = template_content.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content = modified_content.replace("1# User Data here", f"'''{userdata}'''")
            
            # Write the modified content to temporary Python script files
            zipf.writestr(f'{naming}_qPCR.py', modified_content.encode())


        #### Index PCR ####
        elif protocol == "IndexPCR":
            
            ##Opening and Modifying Template Protocol Index PCR
            template_content1 = open('static/OT2_protocols/Template_Protocol_IndexPCR_OT2.py','r').read()
            modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content1 = modified_content1.replace("1# User Data here", f"'''{userdata}'''")

            ##Opening and Modifying Template Protocol Index PCR Purification
            template_content2 = open('static/OT2_protocols/Template_Protocol_IndexPCR_Purfication_OT2.py','r').read()
            modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content2 = modified_content2.replace("1# User Data here", f"'''{userdata}'''")

            # Write the modified content to temporary Python script files
            zipf.writestr(f'{naming}_IndexPCR.py', modified_content1.encode())
            zipf.writestr(f'{naming}_Index-Purification.py', modified_content2.encode())


        ## If there is no expected protocol selection
        else: 
            return abort(404) 



    # Move to the beginning of the ZIP data stream
    zip_data.seek(0)

    if not bool(zip_data):
        return abort(404)


    # Return the ZIP file as an attachment
    return send_file(zip_data,as_attachment=False,download_name=f'{naming}_opentrons_scripts.zip',mimetype='application/zip', max_age=1800)
   



## Script check
if __name__ == "__main__":
    serve(app, host = "0.0.0.0", port = 8000)
    