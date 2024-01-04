########## Not finished



##############################
### Index PCR Purification ###
##############################

## Author Jonas Greve Lauritsen
## Automatic preparation of covaris plates based on csv input

############################


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
    'protocolName': 'Purification of Library Build',
    'apiLevel': '2.12',
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': 'Automated purification of library builds'}

#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):
    #### LABWARE SETUP ####
    ## Placement of smart and dumb labware
    magnet_module = protocol.load_module('magnetic_module',9)

    ## Work plates
    Library_plate = magnet_module.load_labware('biorad_96_wellplate_200ul_pcr')
    Purified_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',11)

    ## Purification materials
    Beads = protocol.load_labware('nest_12_reservoir_15ml',6)['A1']
    Ethanol = protocol.load_labware('nest_12_reservoir_15ml',6)['A2']
    EBT = protocol.load_labware('nest_12_reservoir_15ml',6)['A3']

    ## Tip racks (2x 10 µL, 2x 200 µl)
    tiprack_200 = protocol.load_labware('opentrons_96_filtertiprack_200ul',(1,2,3,4)) #Maybe it has to divided into several seperat potential
    tiprack_200_7 = protocol.load_labware('opentrons_96_filtertiprack_200ul',7)
    tiprack_200_8 = protocol.load_labware('opentrons_96_filtertiprack_200ul',8)
    

    #### PIPETTE SETUP ####
    ## Loading pipettes
    m200 = protocol.load_instrument('p300_multi_gen2', mount='right', tip_racks=[tiprack_200,tiprack_200_7,tiprack_200_8])

    
    #### Lab Work Protocol ####
    ## Addition of Magnetic beads
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.transfer(volume = 75, source = Beads, dest = Library_plate.wells_by_index()[Column], new_tip = 'always', mix_before = (5,100), mix_after = (6,90), blow_out = True, blowout_location = Library_plate[Column])
    
    ## 5 minutes incubation at room temperature
    protocol.delay(minutes = 5) 

    ## Engaging magnetic module. 5 mins wait (to be tested)
    magnet_module.engage()
    protocol.delay(minutes = 5)

    ## Discarding supernatant - to be tested: pipette position.
    for i in range(Col_Number):
        Column = i*8 #Gives the index of the first well in the column
        m200.transfer(volume = 140, source = Library_plate.wells_by_index()[Column], dest = 'trash', new_tip = 'always')

    ## Ethanol washing
    for k in range(2): # Double wash 
        
        ## Setting tiprack
        if k == 0:
            EtOHTip = tiprack_200_7
        if k == 1:
            EtOHTip = tiprack_200_8

        ## Adding Ethanol 
        for i in range(Col_Number): 
            Column = i*8 #Gives the index for the first well in the column
            m200.pick_up_tip(EtOHTip.wells_by_index()[Column])
            m200.transfer(volume = 200, source = Ethanol, dest = Library_plate.wells_by_index()[Column], new_tip = 'never')
            m200.return_tip

        ## Removing Ethanol - reusing the tips from above
        for i in range (Col_Number):
            Column = i*8 # Gives the index for the first well in the column
            m200.pick_up_tip(EtOHTip.wells_by_index()[Column])
            m200.transfer(volume = 220, source = Library_plate.wells_by_index()[Column], dest = 'trash', new_tip = 'never')
            if k == 1: # Extra aspiration to remove residual ethanol
                m200.transfer(volume = 50, source = Library_plate.wells_by_index()[Column], dest = 'trash', new_tip = 'never')
            m200.return_tip

        

    ## Drying beads (5 mins) 
    protocol.delay(minutes = 5)

    ## Disengaging magnet
    magnet_module.disengage()

    ## Adding EBT buffer
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = 40, source = EBT, dest = Library_plate.wells_by_index()[Column], new_tip = 'always',mix_after = (3,35), blow_out=True, blowout_location = Library_plate.wells_by_index()[Column])

    ## Incubation of library plate
    protocol.pause('Seal library plate and spin it down shortly. Incubate the library plate for 5 min at 55 C*. Press RESUME, when library plate has been replaced (without seal) in the magnet module.')
    
    ## Engaging Magnet. 5 mins wait
    magnet_module.engage()
    protocol.delay(minutes = 5)

    ## Transferring purified library to a new plate (purified plate)
    for i in range(Col_Number):
        Column = i*8 #Gives the index for the first well in the column
        m200.transfer(volume = 40, source = Library_plate.wells_by_index()[Column], dest = Purified_plate.wells_by_index()[Column], new_tip = 'always', rate = 0.5)

    ## Deactivating magnet module
    magnet_module.deactivate()

    protocol.comment("STATUS: Protocol Completed.")
