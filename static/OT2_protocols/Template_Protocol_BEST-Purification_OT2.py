#################################
### BEST Library Purification ###
#################################

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

## Outputformat
Output_Format = user_input['OutputFormat'][0]


## Reading csv data
csv_data_temp = StringIO(csv_userdata)
user_data = pd.read_csv(csv_data_temp)



#############################

#### Meta Data ####
metadata = {
    'protocolName': 'Protocol BEST Library Purification',
    'apiLevel': '2.13',
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "{naming} Automated purification of a BEST library build. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
    #### LABWARE SETUP ####
    ## Smart labware
    magnet_module = protocol.load_module('magnetic module',4)

    ## Work plates
    Library_plate = magnet_module.load_labware('biorad_96_wellplate_200ul_pcr') # Input plate
    
    ## Output plate decide from user input. Standard format is PCR plate
    if Output_Format == "PCRstrip":
        Purified_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul',10) # Output plate
    elif Output_Format == "LVLSXS200":
        Purified_plate = protocol.load_labware('LVLXSX200_wellplate_200ul',10) # Output plate
    else:
        Purified_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',10) # Output plate


    ## Purification reservoir and its content.
    Reservoir = protocol.load_labware('deepwellreservoir_12channel_21000ul',1) # Custom labware definition for the 22 mL reservoir
    Beads = Reservoir['A1']
    Ethanol1 = Reservoir['A3']
    Ethanol2 = Reservoir['A4']
    Ebt = Reservoir['A6']
    Waste1 = Reservoir['A12'] # Beads supernatant waste
    Waste2 = Reservoir['A11'] # 1st ethanol wash waste
    Waste3 = Reservoir['A10'] # 2nd ethanol wash waste


    ## Tip racks
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',6)
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',7)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_3 = protocol.load_labware('opentrons_96_filtertiprack_200ul',2)
    tiprack_200_4 = protocol.load_labware('opentrons_96_filtertiprack_200ul',3)
    tiprack_200_5 = protocol.load_labware('opentrons_96_filtertiprack_200ul',8)
    tiprack_200_6 = protocol.load_labware('opentrons_96_filtertiprack_200ul',9)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    m200 = protocol.load_instrument('p300_multi_gen2', mount='left', tip_racks=([tiprack_200_1,tiprack_200_2,tiprack_200_3,tiprack_200_4,tiprack_200_5,tiprack_200_6]))
    m20 = protocol.load_instrument('p20_multi_gen2', mount='right', tip_racks=([tiprack_10_1]))


    #### Beads drying time (seconds) ####
    ## Different drying times - Sat from the last removal of the first column. Total drying time is estimated to 4 mins 55 seconds (23s per pipetting cycle)
    BeadsTime = (295, 272, 249, 226, 203, 180, 157, 134, 111, 88, 65, 42)
    BeadsTime = BeadsTime[(Col_Number-1)] # Selecting the relevant drying time


    #### Selecting Reservoir Ethanol height ####
    Ethanol_Height = (31.7,28.9,26.0,23.2,20.3,17.5,14.6,11.8,8.9,6.1,3.2,0.7) 
    pos = 12-Col_Number
    Ethanol_Height = Ethanol_Height[pos:] # Removes highest, unused heights.

    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Purification of BEST Library Build Begun")
    protocol.set_rail_lights(True)
    magnet_module.disengage()


    ## Addition of Magnetic beads - slowed pipette included.
    protocol.comment("STATUS: Beads Transfer Begun")
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.pick_up_tip()
        m200.move_to(location = Beads.top())
        m200.move_to(location = Beads.bottom(), speed = 40)
        m200.mix(repetitions = 5, volume = 75, location = Beads)
        m200.aspirate(volume = 75, location = Beads, rate = 0.5)
        protocol.delay(5)

        m200.move_to(location = Beads.top(), speed = 10)
        m200.dispense(volume = 75, location = Library_plate.wells()[Column])
        m200.mix(repetitions = 6, volume = 90, location = Library_plate.wells()[Column])
        m200.dispense(volume = 100, location = Library_plate.wells()[Column], rate = 0.8) # Controlled 'blowout'
        protocol.delay(5)
        m200.move_to(location = Library_plate.wells()[Column].top(), speed = 40)
        m200.return_tip()

    ## 5 minutes incubation at room temperature
    protocol.comment("STATUS: Beginning Beads Incubation")
    protocol.delay(minutes = 5)

    ## Engaging magnetic module. 5 mins wait for beads attraction
    magnet_module.engage(height_from_base = 14)
    protocol.delay(minutes = 5)

    ## Discarding supernatant - to be tested: pipette positioning.
    protocol.comment("STATUS: Discarding Supernatant")
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.pick_up_tip()
        m200.transfer(volume = 150, source = Library_plate.wells()[Column].bottom(z = 0.3), dest = Waste1.top(), new_tip = 'never', rate=0.5) #
        m200.air_gap(40,20)
        m200.return_tip()

    ## Double ethanol washing
    protocol.comment("STATUS: Ethanol Wash Begun")
    for k in range(2): # Double wash
        ## Setting up the wash variables
        if k == 0:
            Ethanol_Tips = tiprack_200_3
            Ethanol = Ethanol1
            Waste = Waste2
            protocol.comment("STATUS: First Wash Begun")
        if k == 1:
            Ethanol_Tips = tiprack_200_4
            Ethanol = Ethanol2
            Waste = Waste3
            protocol.comment("STATUS: Second Wash Begun")

        ## Adding Ethanol.
        m200.pick_up_tip(Ethanol_Tips.wells_by_name()['A1']) # Using 1 set of tips for all rows
        for i in range(Col_Number):
            Column = i*8 # Gives the index for the first well in the column
            #m200.pick_up_tip(Ethanol_Tips.wells()[Column])
            m200.mix(repetitions = 2, volume = 200, location = Ethanol.bottom(z = Ethanol_Height[i]))
            m200.aspirate(volume = 170, location = Ethanol.bottom(z = Ethanol_Height[i]),rate = 0.7) 
            m200.dispense(volume = 190, location = Library_plate.wells()[Column].top(z = 1.2), rate = 1) # Dispenses ethanol from 1.2 mm above the top of the well.
        m200.blow_out(location = Waste) # Blow out to remove potential droplets before returning.
        m200.return_tip()

        ## Removing Ethanol - reusing the tips from above
        for i in range(Col_Number):
            Column = i*8 # Gives the index for the first well in the column
            m200.pick_up_tip(Ethanol_Tips.wells()[Column])
            m200.aspirate(volume = 200, location = Library_plate.wells()[Column].bottom(z = 0.35), rate = 0.2) #
            m200.move_to(location = Library_plate.wells()[Column].top(z=2), speed =100)
            m200.dispense(volume = 250, location = Waste.top(), rate = 1)
            m200.air_gap(70, 20) #Take in excess/outside droplets to limit cross-contamination.
            m200.return_tip()

    ## Extra ethanol removal step to remove leftover ethanol before drying beads.
    for i in range(Col_Number):
        Column = i*8
        m20.pick_up_tip()
        m20.aspirate(volume = 10, location = Library_plate.wells()[Column].bottom(z = -0), rate = 0.6)
        m20.return_tip()
        # z = 0 is at the bottom of the labware - here we use a well plate that is slightly deeper than the specified labaware, but be extra careful if changed.


    ## Drying beads (5 mins)
    protocol.comment("STATUS: Drying Beads - time autoadjusted based on number of columns")
    protocol.delay(seconds = BeadsTime) #Times to be verified given m20 step.

    #protocol.pause("Check ethanol level") # Used for testing residual ethnol levels

    ## Disengaging magnet
    magnet_module.disengage()

    ## Adding EBT buffer.
    protocol.comment("STATUS: EBT Buffer Transfer begun")
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.pick_up_tip()
        m200.transfer(volume = 40, source = Ebt, dest = Library_plate.wells()[Column], rate = 1, trash = False , new_tip = 'never', mix_after = (5,20))
        #m200.aspirate(volume = 40, location = Ebt, rate = 1)
        #m200.dispense(volume = 40, location = Library_plate.wells()[Column], rate = 1)
        #m200.mix(repetitions = 5, volume = 30, location = Library_plate.wells()[Column])
        m200.dispense(volume = 40, location = Library_plate.wells()[Column], rate = 0.7)
        protocol.delay(5)
        m200.move_to(location = Library_plate.wells()[Column].top(), speed = 100)
        m200.return_tip()


    ## Incubation of library plate
    protocol.pause('ACTION: Seal library plate and spin it down shortly. Incubate the library plate for 10 min at 37*C. Press RESUME, when library plate has been returned (without seal) to the magnet module.')

    ## Engaging Magnet. 5 mins wait for beads withdrawal
    magnet_module.engage(height_from_base = 14)
    protocol.delay(minutes = 5)

    ## Transferring purified library to a new plate (purified plate). Transfer is sat higher to remove all.
    protocol.comment("STATUS: Transfer of Purified Library")
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = 50, source = Library_plate.wells()[Column].bottom(z = 0.2), dest = Purified_plate.wells()[Column], new_tip = 'always', trash = False, rate = 1)


    ## Deactivating magnet module
    magnet_module.disengage()


    ## Protocol finished
    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
