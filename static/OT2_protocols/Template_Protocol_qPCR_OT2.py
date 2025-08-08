####################################
###     PCR setup - for qPCR     ###
####################################

## Author Jonas Greve Lauritsen

##################################


#### Package loading ####
from opentrons import protocol_api
import pandas as pd
from math import *
from io import StringIO

## User Input
csv_userinput = 1# User Input here

csv_userdata = 1# User Data here


## Reading User Input
csv_input_temp = StringIO(csv_userinput)
user_input = pd.read_csv(csv_input_temp)

## Extracting naming
naming = user_input['Naming'][0]

## Sample number = No here, csv data take priority
Sample_Number=user_input['SampleNumber'][0]
Col_Number = int(ceil(Sample_Number/8))

## Inputformat & Outputformat Output placements not incorporated
Input_Format = user_input['InputFormat'][0]
Output_Format = user_input['OutputFormat'][0]


#### Meta Data ####
metadata = {
    'protocolName': 'Protocol qPCR Setup',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Automated transfer for Master Mix + DNA Libraries for qPCR. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### LABWARE SETUP ####
    ## Samples and sample format (Dilutions done prior)
    Temp_Module_Sample = protocol.load_module('temperature module', 7)
    if Input_Format == "PCRstrip":
        Sample_plate = Temp_Module_Sample.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul') ## Generic PCR strip should approximate our types. Low volumes could be problematic.
        Sample_Height = 1.0

    elif Input_Format == "LVLSXS200":
        Sample_plate = Temp_Module_Sample.load_labware("LVLXSX200_wellplate_200ul")

    else:
        Sample_plate = Temp_Module_Sample.load_labware('biorad_96_wellplate_200ul_pcr') ## Biorad plate is the closest to our plate type.
        Sample_Height = 1.0

    ## qPCR PCR plate
    Temp_Module_qPCR = protocol.load_module('temperature module', 6)
    if Output_Format == "PCRplate":
        qPCR_strips = Temp_Module_qPCR.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul') ## OBS Generic plate here no qPCR strip is uesd here
    
    else: ## Default to qPCR stripsCurrently no qPCR plate is used.
        qPCR_strips = Temp_Module_qPCR.load_labware('bioplastics_96_aluminumblock_100ul') ## qPCR strips are shorter than the PCR tubes we use. Do we have this?
        

    ## Master Mix
    MasterMix = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', 4) ## MasterMix to be prepared in advance and placed in this column.


    ## Load Liquid/ Well Labeling
    ## Samples
    Sample_Liquid = protocol.define_liquid(name = "Sample",description = "Library Sample",display_color = "#00FF37")
    Sample_plate.load_liquid(wells = Sample_plate.wells(), volume = 20, liquid = Sample_Liquid)

    ## MasterMix
    MasterMix_Liquid = protocol.define_liquid(name = "Sample",description = "Library Sample",display_color = "#D000FF")
    MasterMix.load_liquid(wells = MasterMix.wells(), volume = (Col_Number*23*1.1), liquid = MasterMix_Liquid)


    ## Tip racks
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul', 3) ## Sample Transfer
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 5) ## MasterMix (1 column of tips)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    m20 = protocol.load_instrument('p20_multi_gen2', mount = 'right', tip_racks = [tiprack_10_1])
    m200 = protocol.load_instrument('p300_multi_gen2', mount = 'left',tip_racks = [tiprack_200_1])


    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: qPCR setup begun")
    protocol.set_rail_lights(True)


    ## Activating Tempeature module
    Temp_Module_qPCR.set_temperature(celsius = 10)
    Temp_Module_Sample.set_temperature(celsius = 10)


    #### Transfer MasterMix to the PCR plate ####
    protocol.comment("STATUS: Transfer MasterMix to PCR plate.")
    m200.pick_up_tip()
    for i in range(Col_Number):
        Col = i*8
        
        ## Sets the mastermix column (assuming 200 µL maximum), and transfers the remaning over to next column.
        if i == 0: 
            MMpos = "A1"
        if i == 8: 
            MMpos = "A4"
            m200.transfer(volume = 30, source = MasterMix.wells_by_name()["A1"], dest =MasterMix.wells_by_name()[MMpos], rate = 0.8, new_tip = 'never')
        
        m200.transfer(volume = 23, source = MasterMix.wells_by_name()[MMpos], dest = qPCR_strips.wells()[Col].bottom(1.3), mix_before = (2,20), rate = 0.6, blow_out = False, blowout_location = 'source well', new_tip = 'never')
        ## Deep well plates we have less deep bottoms.
        ## Remember the qPCR tubes are shorter.
    m200.drop_tip()


    #### Transfer diluted sample-library to qPCR plate - each sample format has its own Sample_Height for the sample aspiration
    protocol.comment("STATUS: Transfering Diluted Samples to qPCR strips.")
    for i in range(Col_Number):
        Col = i*8
        m20.transfer(volume = 2, source = Sample_plate.wells()[Col].bottom(z = Sample_Height), dest = qPCR_strips.wells()[Col].bottom(z = 1.3), mix_before = (2,5), mix_after = (1,10), rate = 0.6, new_tip = 'always', trash = True)


    ## Protocol complete
    protocol.pause("STATUS: qPCR Setup Finished")
    Temp_Module_qPCR.deactivate()
    Temp_Module_Sample.deactivate()
    protocol.set_rail_lights(False)
