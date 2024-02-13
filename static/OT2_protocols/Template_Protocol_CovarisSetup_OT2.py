#################################
### Covaris plate preparation ###
#################################

## Author Jonas Greve Lauritsen
## Automatic preparation of covaris plates based on csv input

##################################

#### Package loading ####
from opentrons import protocol_api
import pandas as pd
from math import *
from io import StringIO

## User Input & Data
csv_userinput = 1# User Input here

csv_userdata = 1# User Data here

## Reading User Input
csv_input_temp = StringIO(csv_userinput)
user_input = pd.read_csv(csv_input_temp)

## Extracting naming
naming = user_input['Naming'][0]

## Inputformat
Input_Format = user_input['InputFormat'][0]

## Reading csv data
csv_data_temp = StringIO(csv_userdata)
user_data = pd.read_csv(csv_data_temp)

    

##################################

#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Automated Covaris Setup',
    'apiLevel': '2.16',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Covaris automated plate prepper with user CSV input. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### LABWARE SETUP ####
    ## Input Plate - defaults to PCR wellplate
    if Input_Format == 'PCRstrip':
        Input_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', 2) ## PCR tubes/strips
    elif Input_Format == 'LVLSXS200': 
        Input_plate = protocol.load_labware('LVLXSX200_wellplate_200ul', 2) ## LVL SXS 200 tubes (200 µL tubes)
    else:
        Input_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 2) ## Plate

    
    ## Covaris Plate - custom labware
    Covaris_plate = protocol.load_labware('96afatubetpxplate_96_wellplate_200ul', 3) 
    

    ## Water position - if needed you can pause and exchange water as needed.
    Rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',1)
    H2O_1 = Rack.wells_by_name()["A1"]
    H2O_2 = Rack.wells_by_name()["A2"] 
    

    ## Tip racks (2x 10 µL, 2x 200 µl)
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',4)
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',7)
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',6)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    p20 = protocol.load_instrument('p10_single', mount='left', tip_racks=[tiprack_10_1,tiprack_10_2])
    p50 = protocol.load_instrument('p50_single', mount='right', tip_racks=[tiprack_200_1,tiprack_200_2])



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Covaris Setup Begun")
    protocol.set_rail_lights(True)

   
    ## Set up counter
    Counter = 0

    ## Loop for transfering samples and H2O. The samples are "cherrypicked" samples from the the user input.
    for i in range(len(user_data)):

        ## If more than 72 samples are present, a second is needed
        if Counter < 72:
            H2O = H2O_1
        if Counter >= 72:
            H2O = H2O_2

        ## Counting the progress
        Counter = Counter + 1


        ## Find Sample volume and water volume for transfer.
        WellPosition = user_data['Well Position'][i]
        Sample_Input = user_data['DNA ul'][i]
        H2O_Input = user_data['Water ul'][i]



        ## If the sample input volume is equal or greater to 5 µL, and the water input is lower than 5 µL:
        if Sample_Input >= 5 and H2O_Input < 5:

            ## Adding water first if water input volume is greater than 0.
            if H2O_Input > 0: # If command is here to prohibit picking up tips and disposing them without a transfer.
                p20.transfer(volume = H2O_Input, source = H2O.bottom(z = 2.0), dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'always', trash = True) #Transfer pick up new tip

            ## Adding sample (to the water).
            p50.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[WellPosition], dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'Always', Trash = True, mix_after=(3,15), rate = 0.8)


        ## If the sample input volume is equal or greater to 5 µL, and the water input is also equal or greater than 5 µL:
        elif Sample_Input >= 5 and H2O_Input >= 5:

            ## Aspirating H2O then sample, and dispense them together into the covaris plate. Both volume are aspirated together to save time.
            p50.pick_up_tip()
            p50.aspirate(volume = H2O_Input, location = H2O.bottom(z = 2.0)) # First pickup
            p50.touch_tip(location = H2O) # Touching the side of the well to remove excess water.
            p50.aspirate(volume = Sample_Input, location = Input_plate.wells_by_name()[WellPosition]) # Second pickup
            p50.dispense(volume = Sample_Input, location = Covaris_plate.wells_by_name()[WellPosition]) # 30 µL dispense to empty completely
            p50.mix(repetitions = 3, volume = 15, location = Covaris_plate.wells_by_name()[WellPosition], rate = 0.8)

            ## Transferring diluted samples to covaris plate
            p50.drop_tip()


        ## If sample input volume is less than 5 µL. (Water input volume is always above 5 µL here)
        elif Sample_Input < 5:
            ## Adding sample to the Covaris plate.
            p20.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[WellPosition], dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'always', trash = True) #µL

            ## Dispensing H2O into the Covaris plate.
            p50.transfer(volume = H2O_Input, source = H2O.bottom(z = 2.0), dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'Always', trash = True, mix_after = (3,15), rate = 0.8) #µL


    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
