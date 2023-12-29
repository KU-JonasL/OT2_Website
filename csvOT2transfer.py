##### Script to transfer csv data from one file into an OT2 python script (not this one) ####

## Loading packages
from dotenv import load_dotenv
from pprint import pprint
import requests
import os

import pandas as pd
import os
from datetime import datetime

load_dotenv()

def get_opentrons_script(protocol = "Extraction", user = "Antton", samplenumber = 96, inputformat = "LVLSXS200", outputformat = "LVLSXS200", userdata = 0):

    ## Creating a csv from User Inputs
    csv_user_input =pd.DataFrame({'Protocol':[protocol],
    'User':[user],
    'SampleNumber':[samplenumber],
    'InputFormat':[inputformat],
    'OutputFormat':[outputformat]})


    ##Naming of new template(s) selected (based on)
    protocolselect = csv_user_input['Protocol'][0]
    today = datetime.today().strftime('%Y%m%d')
    user = csv_user_input['User'][0]
    naming = user+"_"+protocolselect+"_"+today
    


    
    
    ## Prepare the inputs types for transfer
    csv_input_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_input.values])
    csv_input_raw_str = f"{', '.join(csv_user_input.columns)}\n{csv_input_values}"

    ## Cleaning up the inputs before merge
    csv_input_raw_str = csv_input_raw_str.replace("nan", "")
    csv_input_raw_str = csv_input_raw_str.replace("(", "")
    csv_input_raw_str = csv_input_raw_str.replace(")", "")


    ## Read data from User_Data.csv if available
    if userdata != 0:
        csv_user_data = pd.read_csv(userdata, header=0)

        ## Prepare the data types for transfer
        csv_data_values = "\n".join([f"({', '.join(map(str, row))})" for row in csv_user_data.values])
        csv_data_raw_str = f"{', '.join(csv_user_data.columns)}\n{csv_data_values}"

        ## Cleaning up the data before merge
        csv_data_raw_str = csv_data_raw_str.replace("nan", "")
        csv_data_raw_str = csv_data_raw_str.replace("(", "")
        csv_data_raw_str = csv_data_raw_str.replace(")", "")
    
    
    
    

    


    ## Setting up empty Protocols
    Protocol1 = ""
    Protocol2 = ""
    Protocol3 = ""



    ###### Read the content of the TEMPLATE.py and loading it in a modified protocol ######

    #### DNA Extraction
    if csv_user_input['Protocol'][0] == "Extraction":
        ## Opening Template Extraction
        with open(f'template/templates_Protocols/Template_Protocol_DREX-NucleicAcidExtraction_OT2.py','r') as template_file:
            template_content = template_file.read()
        
        ## Modifying Template 
        modified_content = template_content.replace("1# User Input here", f"'''\n{csv_input_raw_str}\n'''")
        modified_content = modified_content.replace("1# User Data here", f"'''\n{csv_data_raw_str}'''")

        ## Write the modified content back to {naming}.py
        with open(f'{naming}.py', 'w') as modified_file:
            Protocol1 = modified_file.write(modified_content)



    #### Library Building
    elif csv_user_input['Protocol'][0] == "Library":
        
        ## Opening Template; Covaris
        with open('template/templates_Protocols/Template_Protocol_CovarisSetup_OT2.py','r') as template_file:
            template_content1 = template_file.read()
        
        ## Modifying Template; Covaris
        modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content1 = modified_content1.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        ## Write the modified content back to {naming}.py; Covaris
        with open(f'{naming}_Covaris.py', 'w') as modified_file:
            Protocol1 = modified_file.write(modified_content1)



        ## Opening Template; Best-Library
        with open('template/templates_Protocols/Template_Protocol_BEST-Library_OT2.py','r') as template_file:
            template_content2 = template_file.read()
        
        ## Modifying Template; Best-Library
        modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content2 = modified_content2.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        ## Write the modified content back to {naming}.py; Covaris
        with open(f'{naming}_BESTLibrary.py', 'w') as modified_file:
            Protocol2 = modified_file.write(modified_content2)


        ## Opening Template; Best Purification
        with open('template/templates_Protocols/Template_Protocol_BEST-Purification_OT2.py','r') as template_file:
            template_content3 = template_file.read()
        
        ## Modifying Template; Best Purification
        modified_content3 = template_content3.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content3 = modified_content3.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        ## Write the modified content back to {naming}.py; Best Purification
        with open(f'{naming}_BESTPurification.py', 'w') as modified_file:
            Protocol3 = modified_file.write(modified_content3)


    #### qPCR ####
    elif csv_user_input['Protocol'][0] == "qPCR":
        with open('template\templates_Protocols\Template_Protocol_qPCR_OT2.py','r') as template_file:
            template_content = template_file.read()
        
        modified_content = template_content.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content = modified_content.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        ## Write the modified content back to {naming}.py
        with open(f'{naming}.py', 'w') as modified_file:
            Protocol1 = modified_file.write(modified_content)


    #### Index PCR; PCR ####
    elif csv_user_input['Protocol'][0] == "IndexPCR":
        
        ##Opening Template Protocol (Index PCR; PCR)
        with open('template/templates_Protocols/Template_Protocol_IndexPCR_OT2.py','r') as template_file:
            template_content1 = template_file.read()
        
        ## Modifying Template (Index PCR; PCR)
        modified_content1 = template_content1.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content1 = modified_content1.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        ## Write the modified content back to {naming}.py
        with open(f'{naming}_IndexPCR.py', 'w') as modified_file:
            Protocol1 = modified_file.write(modified_content1)


        ##Opening Template Protocol (Index PCR; Purification)
        with open('template/templates_Protocols/Template_Protocol_IndexPCR_Purfication_OT2.py','r') as template_file:
            template_content2 = template_file.read()
        
        ## Modifying Template (Index PCR; Purification)
        modified_content2 = template_content2.replace("1# User Input here", f"'''{csv_input_raw_str}'''")
        modified_content2 = modified_content2.replace("1# User Data here", f"'''{csv_data_raw_str}'''")

        ## Write the modified content back to {naming}.py
        with open(f'{naming}_IndexPurification.py', 'w') as modified_file:
            Protocol2 = modified_file.write(modified_content2)

    
    finished_protocols = [Protocol1,Protocol2,Protocol3]

    return finished_protocols

   



if __name__ == "__main__":
    print("*** Get Alberdi Opentrons Lab Script***")
    
    protocol = "Library"
    user = "Antton"
    samplesnumber = 96
    inputformat = "LVLSXS200"
    outputformat = "LVLSXS200"
    userdata = "user_data/User_Data.csv"

    finished_protocols = get_opentrons_script(protocol,user,samplesnumber, inputformat,outputformat,userdata)

    #print(naming)

    pprint(finished_protocols)




    