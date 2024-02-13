#################################
### Nucleic Acids Extraction protocol ###
#################################

## Author Jonas Greve Lauritsen
## Automatic preparation of covaris plates based on csv input
## Protocol for the combined extraction of DNA and RNA. No nuclease step is active here.

############################


#### Package loading ####
from opentrons import protocol_api, types
import pandas as pd
from math import *
from io import StringIO


#### User Input & Data ####
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

## Inputformat & Outputformat
Output_Format = user_input['OutputFormat'][0]



#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Nucleic Acid Extraction',
    'apiLevel': '2.16',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "TREX Automated extraction of nucleic acids from samples.Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
    #### LABWARE SETUP ####
    ## Smart labware
    magnet_module = protocol.load_module('magnetic module',4)

    ## Input plate - OBS out deepwell plate is deeper.
    Extraction_plate = magnet_module.load_labware('thermoscientificnunc_96_wellplate_1300ul') ## Input plate with sample
    
    ## Selecting output format - default is a PCR wellplate
    if Output_Format == "PCRstrip":
        Elution_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul',10) # Output plate
    elif Output_Format == "LVLSXS200":
        Elution_plate = protocol.load_labware('LVLXSX200_wellplate_200ul',10) # Output plate
    else:
        Elution_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',10) # Output plate

    ## Deepwell reservoir & Liquid Inputs
    reservoir = protocol.load_labware('deepwellreservoir_12channel_21000ul',1)
    Beads = reservoir['A1']
    Ethanol1 = reservoir['A3']
    Ethanol2 = reservoir['A4']
    EBT = reservoir['A6']

    #### Waste ####
    Waste1 = reservoir['A12']    ## 1st Beads-supernatant waste
    Waste2 = reservoir['A11']    ## 2nd Beads-supernatant waste
    Waste3 = reservoir['A10']    ## 1st ethanol wash waste
    Waste4 = reservoir['A9']     ## 2nd ethanol wash waste


    #### Tip racks (8x 200 µl) ####
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',7) ## Beads and discard
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',2) ## Discard Ethanol 1 and remove
    tiprack_200_3 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5) ## Ethanol 1
    tiprack_200_4 = protocol.load_labware('opentrons_96_filtertiprack_200ul',3) ## Wash 1
    tiprack_200_5 = protocol.load_labware('opentrons_96_filtertiprack_200ul',6) ## Ethanol 2
    tiprack_200_6 = protocol.load_labware('opentrons_96_filtertiprack_200ul',8) ## Wash 2
    tiprack_200_7 = protocol.load_labware('opentrons_96_filtertiprack_200ul',9) ## Elution
    tiprack_200_8 = protocol.load_labware('opentrons_96_filtertiprack_200ul',11) ## Elution transfer


    #### PIPETTE SETUP ####
    m200 = protocol.load_instrument('p300_multi_gen2', mount='left', tip_racks=([tiprack_200_1,tiprack_200_2,tiprack_200_3,tiprack_200_4,tiprack_200_5,tiprack_200_6,tiprack_200_7,tiprack_200_8]))


    #### Reservoir Liquid Height ####
    Height = (31.5,28.8,25.9,23.1,20.2,17.4,14.5,11.7,8.8,6.0,3.1,0.8) ## Height above the reservoir to approximate liquid level.
    pos = 12-Col_Number
    Height = Height[pos:] ## Removes highest, unused heights.


    #### Function to resuspend-mix ####
    def Ethanol_Mix(Pipette, Vol, Loc, asp_height, dis_height, reps, Rate, Col):
        for i in range(reps):
            Pipette.aspirate(volume = Vol, location = Loc.wells()[Col].bottom(z = asp_height), rate = Rate)
            Pipette.dispense(volume = Vol, location = Loc.wells()[Col].bottom(z = dis_height), rate = Rate) ## Extra dispense to blow out



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Nucleic Acid Extraction Begun")
    protocol.set_rail_lights(True)
    magnet_module.disengage()



    #### Sample-bead binding ####
    ## Addition of Magnetic beads - slowed pipetting
    protocol.comment("STATUS: Beads Transfer Begun")
    for i in range(Col_Number):
        Column = i*8 ## Gives the index of the first well in the column
        m200.pick_up_tip()

        ## Beads Pick up
        m200.move_to(location = Beads.top())
        m200.move_to(location = Beads.bottom(z = Height[i]), speed = 50)
        m200.mix(repetitions = 5, volume = 125, location = Beads.bottom(z = Height[i]), rate = 1.0)
        m200.aspirate(volume = 200, location = Beads.bottom(z = Height[i]), rate = 0.5)
        protocol.delay(5)
        m200.move_to(location = Beads.top(), speed = 40)

        ## Beads Addition
        m200.dispense(volume = 200, location = Extraction_plate.wells()[Column].bottom(z = 4.0), rate = 0.8)
        m200.mix(repetitions = 5, volume = 180, location = Extraction_plate.wells()[Column].bottom(z = 6.0), rate = 1.2)
        protocol.delay(5)
        m200.move_to(location = Extraction_plate.wells()[Column].top(), speed = 50)

        m200.return_tip()

    ## Incuabtion of the extraction plate
    protocol.pause('ACTION: Seal the Extraction plate. Spin it down. Incubate the plate: 15 mins, 10 C, 1500 rpm. Spin it down. Press RESUME, when the extraction plate has been returned (without seal) to the magnet module.')



    #### Beads Cleanup ####
    ## Engaging Magnet. 2 mins wait for beads withdrawal
    protocol.comment("STATUS: Engaging the Magnet")
    magnet_module.engage(height_from_base = 12)
    protocol.delay(minutes = 2) ## Minimum of 60 seconds. Needs to be checked with actual DNA samples.

    ## Discarding the Supernatant
    for i in range(Col_Number):
        Column = i*8 ## Gives the index of the first well in the column
        m200.pick_up_tip()

        ## Remove bead-supernatant 1
        m200.aspirate(volume = 200, location = Extraction_plate.wells()[Column].bottom(z = 3.4), rate = 0.7)
        m200.dispense(volume = 200, location = Waste1.top(z = 1), rate = 0.5) ## Extra dispense to blow out
        protocol.delay(seconds = 10) ## Droplets falling
        m200.move_to(location = Waste1.top().move(types.Point(x = 0, y = -5, z = 2))) ## flicker motion??

        ## Remove bead-supernatant 2
        m200.aspirate(volume = 200, location = Extraction_plate.wells()[Column].bottom(z = 3.4), rate = 0.7)
        m200.dispense(volume = 200, location = Waste2.top(), rate = 0.6)
        protocol.delay(seconds = 5) ## Droplets falling.
        m200.air_gap(volume = 20)

        m200.return_tip()



    #### Ethanol washing ####
    ## Double ethanol washing
    protocol.comment("STATUS: Ethanol Wash Begun")
    for k in range(2): ## Double wash
        ## Setting up the wash variables
        if k == 0:
            Ethanol = Ethanol1
            Waste = Waste3
            protocol.comment("STATUS: First Wash Begun")
        if k == 1:
            Ethanol = Ethanol2
            Waste = Waste4
            protocol.comment("STATUS: Second Wash Begun")

        ## Disengaging magnet
        magnet_module.disengage()

        ## Adding Ethanol.
        for i in range(Col_Number):
            Column = i*8 ## Gives the index for the first well in the column
            m200.pick_up_tip()
            m200.aspirate(volume = 200, location = Ethanol.bottom(z = Height[i]), rate = 0.7)
            m200.dispense(volume = 200, location = Extraction_plate.wells()[Column].bottom(z = 5.5), rate = 0.8)
            Ethanol_Mix(Pipette = m200, Vol = 180, Loc = Extraction_plate, asp_height = 4.0, dis_height = 6.0, reps = 5, Rate = 1.3, Col = Column) ## Custom function for better mix and resuspention.
            m200.return_tip()

        ## Engaging Magnet
        magnet_module.engage(height_from_base = 12)
        protocol.delay(minutes = 2)

        ## Removing Ethanol
        for i in range(Col_Number):
            Column = i*8 ## Gives the index for the first well in the column
            m200.pick_up_tip()
            m200.aspirate(volume = 200, location = Extraction_plate.wells()[Column].bottom(z = 3.4), rate = 0.4)
            m200.dispense(volume = 200, location = Waste.top(), rate = 0.7)
            m200.air_gap(volume = 70) ## Takes in excess, outside droplets to limit cross-contamination.
            m200.return_tip()


    ## Drying beads (5 mins)
    protocol.comment("STATUS: Drying Beads - 5 Minutes")
    protocol.delay(minutes = 5)



    #### Elution ####
    ## Disengaging magnet
    magnet_module.disengage()

    ## Adding EBT buffer.
    protocol.comment("STATUS: EBT Buffer Transfer begun")
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = 50, source  = EBT, dest = Extraction_plate.wells()[Column].bottom(z = 3.4), rate = 1, new_tip = 'always', mix_after = (5,35), trash = False)

    ## Incubation of Extraction plate
    protocol.pause('ACTION: Seal the Extraction plate and spin it down shortly. Incubate the extraction plate: 5 mins, 25*C, 1500 rpm. Spin the plate down. Press RESUME, when the Extraction plate has been returned (without seal) to the magnet module.')

    ## Engaging Magnet. 3 mins wait for beads withdrawal
    magnet_module.engage(height_from_base = 12)
    protocol.delay(minutes = 3)

    ## Transferring extracted nucleic acids to a new plate (purified plate). Transfer is sat higher to remove all.
    protocol.comment("STATUS: Transfer of Eluted Extracted Samples")
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = 55, source = Extraction_plate.wells()[Column].bottom(z = 3.4), dest = Elution_plate.wells()[Column], new_tip = 'always', trash = False, rate = 0.3)


    #### Protocol finished ####
    magnet_module.disengage()
    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
