####################################
###       Index PCR setup        ###
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
Sample_Number=int(user_input['Sample Number'][0])
Col_Number = int(ceil(Sample_Number/8))

## Inputformat & Outputformat = No here
Input_Format = user_input['Input_Format'][0]
#Output_Format = user_input['Output_Format'][0]


## Reading csv data
csv_data_temp = StringIO(csv_userdata)
user_data = pd.read_csv(csv_data_temp)



#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Index PCR Setup',
    'apiLevel': '2.13',
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': f"{naming}'s transfer for Index PCR: Master Mix, Primers Mix, and Sample-library material. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### LABWARE SETUP ####
    ## Index PCR plate
    Temp_Module_PCR = protocol.load_module('temperature module',6)
    iPCR_Plate = Temp_Module_PCR.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul') ## PCR plate


    ## Primer plate (each well contain both forward and reverse primers)
    Temp_Module_Primer = protocol.load_module('temperature module',7)
    Primer_plate = Temp_Module_Primer.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')


    ## Selecting input format
    if Input_Format == "PCRstrip":
        Sample_Plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul',10) # Output plate
    elif Input_Format == "LVLSXS200":
        Sample_Plate = protocol.load_labware('LVLXSX200_wellplate_200ul',10) # Output plate
    else:
        Sample_Plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',10) # Output plate


    ## Master Mix
    MasterMix = protocol.load_labware('thermoscientificnunc_96_wellplate_1300ul', 4).wells_by_name()["A1"] ## MasterMix to be prepared in advance


    ## Tip racks
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',3) ## Primer transfer
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',2) ## Sample Transfer
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5) ## MasterMix


    #### PIPETTE SETUP ####
    ## Loading pipettes
    m20 = protocol.load_instrument('p20_multi_gen2', mount = 'right', tip_racks = [tiprack_10_1,tiprack_10_2])
    m200 = protocol.load_instrument('p300_multi_gen2', mount = 'left',tip_racks = [tiprack_200_1])

    m200.starting_tip = tiprack_200_1




    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Index PCR setup begun")
    protocol.set_rail_lights(True)


    ## Activating Tempeature modules
    #Temp_Module_PCR.set_temperature(celsius = 10)
    #Temp_Module_Primer.set_temperature(celsius = 10)


    #### Transfer MasterMix to the PCR plate ####
    protocol.comment("STATUS: Transfer MasterMix to PCR plate.")

    m200.pick_up_tip()
    for i in range(Col_Number):
        Col = i*8
        m200.transfer(volume = 38, source = MasterMix.bottom(z = 3.4), dest = iPCR_Plate.wells()[Col].bottom(z = 1.2), mix_before = (2,30), rate = 0.6, blow_out = False, blowout_location = 'source well', new_tip = 'never')
        ## Deep well plates we have less deep bottoms.
    m200.drop_tip()


    #### Primer Transfer ####
    protocol.comment("STATUS: Transfering Index PCR primer.")
    for i in range(Col_Number):
        Col = i*8
        m20.transfer(volume = 2, source = Primer_plate.wells()[Col], dest = iPCR_Plate.wells()[Col].bottom(z = 1.2), mix_after = (2,5), rate = 0.6, new_tip = 'Always', trash = True)


    #### Transfer diluted sample-library to index PCR strips - obs for
    protocol.comment("STATUS: Transfering Diluted Samples to Index PCR strips")
    for i in range (Col_Number):
        Col = i*8
        m20.transfer(volume = 10, source = Sample_Plate.wells()[Col].bottom(z = 1.2), dest = iPCR_Plate.wells()[Col].bottom(z = 1.2), mix_before = (2,5), mix_after = (2,10), rate = 0.6, new_tip = 'Always', trash = True)


    ## Protocol complete
    protocol.pause("STATUS: Index PCR Setup Finished")
    Temp_Module_PCR.deactivate()
    Temp_Module_Primer.deactivate()
    protocol.set_rail_lights(False)
