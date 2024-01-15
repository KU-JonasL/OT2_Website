from flask import Flask, render_template, request, redirect, send_file, send_from_directory, abort, url_for
import requests
from waitress import serve
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import os
import io
import tempfile
import zipfile


def get_opentrons_script(protocol, user, samplenumber, inputformat, outputformat, userdata):

    ## Creating a dictionary from User Inputs
    csv_user_input =pd.DataFrame({'Protocol':[protocol],
    'User':[user],
    'SampleNumber':[samplenumber],
    'InputFormat':[inputformat],
    'OutputFormat':[outputformat]})

    ## Prepare the inputs types for transfer
    csv_input_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_input.values])
    csv_input_raw_str = f"{', '.join(csv_user_input.columns)}\n{csv_input_values}"
    csv_input_raw_str = csv_input_raw_str.replace("nan", "").replace("(", "").replace(")", "")


    ## Read data from User_Data if available
    csv_user_data = pd.DataFrame(userdata[1:], columns = userdata[0])

    ## Prepare the data types for transfer
    csv_data_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_data.values])
    csv_data_raw_str = f"{', '.join(csv_user_data.columns)}\n{csv_data_values}"
    csv_data_raw_str = csv_data_raw_str.replace("nan", "").replace("(", "").replace(")", "")
    

    
    #temp_dir = tempfile.mkdtemp()
    #os.chmod(temp_dir, 0o777)
    #zip_data = os.path.join(temp_dir, "temp_folder.zip")
    zip_data = io.BytesIO()

    with zipfile.ZipFile(zip_data, mode="w") as zipf:
    ###### Read the content of the TEMPLATE.py and loading it in a modified protocol ######

        #### DNA Extraction
        if csv_user_input['Protocol'] == "Extraction":
            ## Opening and Modifying Template Extraction

            template_content = open(f'static/OT2_protocols/Template_Protocol_DREX-NucleicAcidExtraction_OT2.py','r').read()
            modified_content = template_content.replace("1# User Input here", f"'''\n{csv_input_raw_str}\n'''")
            modified_content = modified_content.replace("1# User Data here", f"'''\n{csv_data_raw_str}'''")

            ## Investigation 
            test_file = open("requirements.txt",'r').read()
            
            # Write the modified content to temporary Python script files
            zipf.writepy('finished_protocol1.py', modified_content.encode())
            zipf.writepy('Test_sop.txt', test_file.encode())
            


        
        #### Library Building
        elif csv_user_input['Protocol'] == "Library":
            
            ## Opening and Modifying Template; Covaris
            template_content1 =  open('static/OT2_protocols/Template_Protocol_CovarisSetup_OT2.py','r').read()
            modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content1 = modified_content1.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

            ## Opening and Modifying Template; Best-Library
            template_content2 = open('static/OT2_protocols/Template_Protocol_BEST-Library_OT2.py','r').read()
            modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content2 = modified_content2.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

            ## Opening and Modifying Template; Best Purification
            template_content3 =  open('static/OT2_protocols/Template_Protocol_BEST-Purification_OT2.py','r').read()
            modified_content3 = template_content3.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content3 = modified_content3.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

            # Write the modified content to temporary Python script files
            zipf.writepy('finished_protocol1.py', modified_content1.encode())
            zipf.writepy('finished_protocol2.py', modified_content2.encode())
            zipf.writepy('finished_protocol3.py', modified_content3.encode())
                

        #### qPCR ####
        elif csv_user_input['Protocol'] == "qPCR":
            template_content = open('static/OT2_protocols/Template_Protocol_qPCR_OT2.py','r').read()
            modified_content = template_content.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content = modified_content.replace("1# User Data here", f"'''{csv_data_raw_str}'''")
            
            # Write the modified content to temporary Python script files
            zipf.writepy('finished_protocol1.py', modified_content.encode())


        #### Index PCR; PCR ####
        elif csv_user_input['Protocol'] == "IndexPCR":
            
            ##Opening and Modifying Template Protocol (Index PCR; PCR)
            template_content1 = open('static/OT2_protocols/Template_Protocol_IndexPCR_OT2.py','r').read()
            modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content1 = modified_content1.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

            ##Opening and Modifying Template Protocol (Index PCR; Purification)
            template_content2 = open('static/OT2_protocols/Template_Protocol_IndexPCR_Purfication_OT2.py','r').read()
            modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
            modified_content2 = modified_content2.replace("1# User Data here", f"'''{csv_data_raw_str}'''")


            # Write the modified content to temporary Python script files
            zipf.writepy('finished_protocol1.py', modified_content1.encode())
            zipf.writepy('finished_protocol2.py', modified_content2.encode())

        
        #else: 
            #return abort(404) 
      
            
    # Move to the beginning of the ZIP data stream
    zip_data.seek(0)

    #if not bool(zip_data):
    #    return abort(404)

    # Return the ZIP file as an attachment
    return send_file(zip_data,as_attachment=False,download_name='opentrons_scripts.zip',mimetype='application/zip', max_age=1800)
    