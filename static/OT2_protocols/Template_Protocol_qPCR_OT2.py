####################################
###     PCR setup - for qPCR     ###
####################################

## Author Jonas Greve Lauritsen

##################################


#### Package loading ####
from opentrons import protocol_api
from pandas import pd
from math import *


## User Input


csv_userinput = 1# User Input here

csv_userdata = 1# User Data here



user_input = pd.read_csv("csv_userinput",header=0)# User Input here
user = user_input['User'][0]
Sample_Number=user_input['Sample Number'][0]
Col_Number = int(ceil(Sample_Number/8))
Input_Format = user_input['Input_Format'][0]
Output_Format = user_input['Output_Format'][0]

if(bool("template\Template_CSV_LibraryInput.csv")==True): 
    csv_raw = pd.DataFrame(pd.read_file("template\Template_CSV_LibraryInput.csv"))# Your User Data here




#### Meta Data ####
metadata = {
    'protocolName': 'Protocol qPCR Setup',
    'apiLevel': '2.13',
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': 'Automated transfer for Master Mix + DNA Libraries for qPCR.'}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### LABWARE SETUP ####
    ## qPCR PCR plate
    Temp_Module_qPCR = protocol.load_module('temperature module', 6)
    qPCR_strips = Temp_Module_qPCR.load_labware('bioplastics_96_aluminumblock_100ul') ## qPCR strips - are shorter than the PCR tubes we use.


    ## Samples and sample format (Dilutions done prior)
    Temp_Module_Sample = protocol.load_module('temperature module', 7)
    if Input_Format == "Strip":
        Sample_Plate = Temp_Module_Sample.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul') ## Generic PCR strip should approximate our types. Low volumes could be problematic.
        Sample_Height = 1.0

    if Input_Format == "Plate":
        Sample_Plate = Temp_Module_Sample.load_labware('biorad_96_wellplate_200ul_pcr') ## Biorad plate is the closest to our plate type.
        Sample_Height = 1.0

    ## Master Mix
    MasterMix = protocol.load_labware('thermoscientificnunc_96_wellplate_1300ul', 4).wells_by_name()["A1"] ## MasterMix to be prepared in advance and placed in this column.


    ## Tip racks
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul', 3) ## Sample Transfer
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', 5) ## MasterMix (1 column of tips)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    m20 = protocol.load_instrument('p20_multi_gen2', mount = 'right', tip_racks = [tiprack_10_1])
    m200 = protocol.load_instrument('p300_multi_gen2', mount = 'left',tip_racks = [tiprack_200_1])

    m200.starting_tip = tiprack_200_1




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
        m200.transfer(volume = 23, source = MasterMix.bottom(z = 3.4), dest = qPCR_strips.wells()[Col].bottom(1.3), mix_before = (2,20), rate = 0.6, blow_out = False, blowout_location = 'source well', new_tip = 'never')
        ## Deep well plates we have less deep bottoms.
        ## Remember the qPCR tubes are shorter.
    m200.drop_tip()


    #### Transfer diluted sample-library to qPCR plate - each sample format has its own Sample_Height for the sample aspiration
    protocol.comment("STATUS: Transfering Diluted Samples to qPCR strips.")
    for i in range(Col_Number):
        Col = i*8
        m20.transfer(volume = 2, source = Sample_Plate.wells()[Col].bottom(z = Sample_Height), dest = qPCR_strips.wells()[Col].bottom(z = 1.3), mix_before = (2,5), mix_after = (1,10), rate = 0.6, new_tip = 'always', trash = True)


    ## Protocol complete
    protocol.pause("STATUS: qPCR Setup Finished")
    Temp_Module_qPCR.deactivate()
    Temp_Module_Sample.deactivate()
    protocol.set_rail_lights(False)
