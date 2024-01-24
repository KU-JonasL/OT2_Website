########## Not finished



##############################
### Index PCR Purification ###
##############################

## Author Jonas Greve Lauritsen
## Automatic preparation of covaris plates based on csv input

############################


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
Sample_Number=int(user_input['SampleNumber'][0])
Col_Number = int(ceil(Sample_Number/8))

## Inputformat & Outputformat = No here
Input_Format = user_input['InputFormat'][0]
Output_Format = user_input['OutputFormat'][0]



#### Meta Data ####
metadata = {
    'protocolName': 'Purification of Library Build',
    'apiLevel': '2.12',
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Automated purification of library builds. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
    #### LABWARE SETUP ####
    ## Placement of smart and dumb labware
    magnet_module = protocol.load_module('magnetic_module',9)

    ## Work plates
    if Input_Format == "PCRstrip":
        Sample_Plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul',10) # Input plate
    else:
        Sample_Plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',10) # Input plate

    if Output_Format == "PCRstrip":
        Purified_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul',10) # Output plate
    elif Output_Format == "LVLSXS200":
        Purified_plate = protocol.load_labware('LVLXSX200_wellplate_200ul',10) # Output plate
    else:
        Purified_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',10) # Output plate


    ## Purification materials
    Reservoir = protocol.load_labware('deepwellreservoir_12channel_21000ul',1) # Custom labware definition for the 22 mL reservoir
    Beads = Reservoir['A1']
    Ethanol1 = Reservoir['A3']
    Ethanol2 = Reservoir['A4']
    Ebt = Reservoir['A6']
    Waste1 = Reservoir['A12'] # Beads supernatant waste
    Waste2 = Reservoir['A11'] # 1st ethanol wash waste
    Waste3 = Reservoir['A10'] # 2nd ethanol wash waste


    ## Tip racks (2x 10 µL, 2x 200 µl)
    
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',7)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_3 = protocol.load_labware('opentrons_96_filtertiprack_200ul',2)
    tiprack_200_4 = protocol.load_labware('opentrons_96_filtertiprack_200ul',3)
    tiprack_200_5 = protocol.load_labware('opentrons_96_filtertiprack_200ul',8)
    tiprack_200_6 = protocol.load_labware('opentrons_96_filtertiprack_200ul',9)
    tiprack_200_7 = protocol.load_labware('opentrons_96_filtertiprack_10ul',6)

    #### PIPETTE SETUP ####
    ## Loading pipettes
    m200 = protocol.load_instrument('p300_multi_gen2', mount='left', tip_racks=([tiprack_200_1,tiprack_200_2,tiprack_200_3,tiprack_200_4,tiprack_200_5,tiprack_200_6,tiprack_200_7]))

    
    #### Lab Work Protocol ####
    ## Addition of Magnetic beads
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.transfer(volume = 75, source = Beads, dest = Sample_Plate.wells_by_index()[Column], new_tip = 'always', mix_before = (5,100), mix_after = (6,90), blow_out = True, blowout_location = Sample_Plate[Column])
    
    ## 5 minutes incubation at room temperature
    protocol.delay(minutes = 5) 

    ## Engaging magnetic module. 5 mins wait (to be tested)
    magnet_module.engage()
    protocol.delay(minutes = 5)

    ## Discarding supernatant - to be tested: pipette position.
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.transfer(volume = 140, source = Sample_Plate.wells_by_index()[Column], dest = Waste1, new_tip = 'always')

    ## Ethanol washing
    for k in range(2): # Double wash 
        
        ## Setting tiprack
        if k == 0:
            EtOHTip = tiprack_200_3
            Ethanol = Ethanol1
            Waste = Waste2
        if k == 1:
            EtOHTip = tiprack_200_4
            Ethanol = Ethanol1
            Waste = Waste3

        ## Adding Ethanol 
        for i in range(Col_Number): 
            Column = i*8 #Gives the index for the first well in the column
            m200.pick_up_tip(EtOHTip.wells_by_index()[Column])
            m200.transfer(volume = 200, source = Ethanol, dest = Sample_Plate.wells_by_index()[Column], new_tip = 'never')
            m200.return_tip

        ## Removing Ethanol - reusing the tips from above
        for i in range (Col_Number):
            Column = i*8 # Gives the index for the first well in the column
            m200.pick_up_tip(EtOHTip.wells_by_index()[Column])
            m200.transfer(volume = 220, source = Sample_Plate.wells_by_index()[Column], dest = Waste, new_tip = 'never')
            if k == 1: # Extra aspiration to remove residual ethanol
                m200.transfer(volume = 50, source = Sample_Plate.wells_by_index()[Column], dest = Waste, new_tip = 'never')
            m200.return_tip



    ## Drying beads (5 mins) 
    protocol.delay(minutes = 5)

    ## Disengaging magnet
    magnet_module.disengage()

    ## Adding EBT buffer
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = 40, source = Ebt, dest = Sample_Plate.wells_by_index()[Column], new_tip = 'always',mix_after = (3,35), blow_out=True, blowout_location = Sample_Plate.wells_by_index()[Column])


    ## Incubation of library plate
    protocol.pause('Seal library plate and spin it down shortly. Incubate the library plate for 5 min at 55 C*. Press RESUME, when library plate has been replaced (without seal) in the magnet module.')
    
    ## Engaging Magnet. 5 mins wait
    magnet_module.engage()
    protocol.delay(minutes = 5)

    ## Transferring purified library to a new plate (purified plate)
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = 40, source = Sample_Plate.wells_by_index()[Column], dest = Purified_plate.wells_by_index()[Column], new_tip = 'always', rate = 0.5)

    ## Deactivating magnet module
    magnet_module.deactivate()

    protocol.comment("STATUS: Protocol Completed.")
