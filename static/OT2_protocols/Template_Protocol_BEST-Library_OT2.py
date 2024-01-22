##########################
### BEST Library build ###
##########################

## Author Jonas Greve Lauritsen
## Adaptation of the BEST library build.

##### User Data Input #####

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
#Sample_Number= int(user_input['Sample Number'][0])
#Col_Number = int(ceil(Sample_Number/8))

## Inputformat & Outputformat = No here
#Input_Format = user_input['Input_Format'][0]
#Output_Format = user_input['Output_Format'][0]


## Reading csv data
csv_data_temp = StringIO(csv_userdata)
user_data = pd.read_csv(csv_data_temp)



#### METADATA ####
metadata = {
    'protocolName': 'Protocol: BEST Library Build',
    'apiLevel': '2.13',
    'author': 'Jonas Greve Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': f"{naming}'s Automated (BEST) library build of DNA samples (csv-adjusting version). Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}


#### Protocol script ####
def run(protocol: protocol_api.ProtocolContext):


    #### LABWARE SETUP ####
    ## Smart labware; thermocycler and temperature modules.
    thermo_module = protocol.load_module('thermocyclerModuleV2')
    cold_module = protocol.load_module('temperature module', 9)


    ## Sample Plate (Placed in thermocycler).
    Sample_plate = thermo_module.load_labware('biorad_96_wellplate_200ul_pcr') ## Same plate as sat up for the purification.


    ## Tip racks (4x 10 µL)
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',4)
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',1)
    tiprack_10_3 = protocol.load_labware('opentrons_96_filtertiprack_10ul',2)
    tiprack_10_4 = protocol.load_labware('opentrons_96_filtertiprack_10ul',3)

    ## Mastermix Setup
    cold_plate = cold_module.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    End_Repair_Mix = cold_plate.wells_by_name()["A1"]
    Adaptors_10mM = cold_plate.wells_by_name()["A4"]
    Adaptors_20mM = cold_plate.wells_by_name()["C4"]
    Ligation_Mix = cold_plate.wells_by_name()["A7"]
    Nick_Fill_In_Mix = cold_plate.wells_by_name()["A10"]


    #### PIPETTE SETUP ####
    m20 = protocol.load_instrument('p20_multi_gen2', mount = 'right', tip_racks = [tiprack_10_1,tiprack_10_2,tiprack_10_3])
    p10 = protocol.load_instrument('p10_single', mount = 'left', tip_racks = [tiprack_10_4])


    
    #### User data setup ####
    ## Column setup
    Col_number = int(ceil(len(user_data)/8)) ## Scales number of columns in used based on csv data (rounding up for full columns used).
    col_name = ["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12"] ## Column is named by top well.


    ## Ligation height setup - to limit viscous solution on the outside of the tips.
    Ligation_height = [1.75, 1.6, 1.45, 1.30, 1.15, 1, 0.85, 0.70, 0.55, 0.4, 0.25, 0.10] ## List with volume height for 12 transfers and descending.
    pos = 12-Col_number
    Ligation_height = Ligation_height[pos:] ## Removes highest, unused heights.



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.

    ## Initial activation of Smart Labware. Activate temperature module early in setup to reduce time waste.
    protocol.set_rail_lights(True)
    protocol.comment("STATUS: Activating Modules")


    ## Activating smart modules
    cold_module.set_temperature(10) ## 10 C for the temperature module as it preserves the solutions while can be reached.
    thermo_module.open_lid()
    thermo_module.set_block_temperature(10) ## 10 C to preserve samples and be reached.
    thermo_module.set_lid_temperature(105)



    #### First step - End repair reaction ####
    protocol.comment("STATUS: End Repair Transfer Step Begun")

    ## Transfering End Repair Mix
    for i in range(Col_number):
        m20.transfer(volume = 5.85, source = End_Repair_Mix, dest = Sample_plate.wells_by_name()[col_name[i]], mix_before = (2,10), mix_after = (5,10), new_tip = 'always', trash = False)


    ## End Repair Incubation
    protocol.comment("STATUS: End Repair Incubation Begun")
    thermo_module.close_lid()
    profile = [
        {'temperature':20, 'hold_time_minutes':30},
        {'temperature':65, 'hold_time_minutes':30}]
    thermo_module.execute_profile(steps = profile, repetitions = 1, block_max_volume = 30)
    thermo_module.set_block_temperature(10) ## Reset to 10 C while working
    thermo_module.open_lid()



    #### Second step - Adaptors and Ligation ####
    protocol.comment("STATUS: Adaptor Transfer Step Begun")

    ## Transferring Adaptors. The adaptor concentration is chosen based on the csv input using conditional logic.
    for i in range(len(user_data)):
        p10.pick_up_tip()

        if user_data['Adaptor concentration (nM)'][i] == 10: ## 10 mM adaptor transfer
            p10.transfer(volume = 1.5, source = Adaptors_10mM, dest = Sample_plate.wells()[user_data[i][0]], mix_before = (2,4), mix_after = (1,10), new_tip = 'never')
        if user_data['Adaptor concentration (nM)'][i] == 20: ## 20 mM adaptor transfer
            p10.transfer(volume = 1.5, source = Adaptors_20mM, dest = Sample_plate.wells()[user_data[i][0]], mix_before = (2,4), mix_after = (1,10), new_tip = 'never')

        p10.return_tip()


    ## Transfering Ligation Mix
    protocol.comment("STATUS: Ligation Transfer Step Begun")

    ## Changing flowrate for aspiration & dispension, as PEG4000 is viscous and requires slowed pipetting.
    m20.flow_rate.aspirate = 3 ## µL/s 
    m20.flow_rate.dispense = 3 ## µL/s

    ## Ligation Pipetting
    for i in range(Col_number):
        ## Aspiration, mixing, and dispersion. Extra delays to allow viscous liquids to aspirate/dispense. Slow movements to limit adhesion.
        m20.pick_up_tip()

        m20.move_to(location = Ligation_Mix.top())
        m20.move_to(location = Ligation_Mix.bottom(z = Ligation_height[i]), speed = 3)
        m20.mix(repetitions = 2, volume = 6, location = Ligation_Mix.bottom(z = Ligation_height[i]))
        m20.aspirate(volume = 6, location = Ligation_Mix.bottom(z = Ligation_height[i]))
        protocol.delay(10)
        m20.move_to(location = Ligation_Mix.top(), speed = 3)

        m20.dispense(volume = 6, location = Sample_plate.wells_by_name()[col_name[i]])
        m20.mix(repetitions = 3, volume = 10, location = Sample_plate.wells_by_name()[col_name[i]])
        m20.dispense(volume = 3, location = Sample_plate.wells_by_name()[col_name[i]]) ## 'Controlled blowout'
        protocol.delay(5)
        m20.move_to(location = Sample_plate.wells_by_name()[col_name[i]].top(), speed = 3)

        m20.return_tip()

    ## Ligation Incubation
    protocol.comment("STATUS: Ligation Incubation Step Begun")
    thermo_module.close_lid()
    profile = [
        {'temperature':20, 'hold_time_minutes':30},
        {'temperature':65, 'hold_time_minutes':10}]
    thermo_module.execute_profile(steps = profile, repetitions = 1, block_max_volume = 37.5)
    thermo_module.set_block_temperature(10) ## Reset to 10 C while working
    thermo_module.open_lid()



    ### Third step - Fill-In Reaction ###

    ## Transfering Fill-In reaction mix
    protocol.comment("STATUS: Fill-In Step Begun")

    ## Changing flowrate for aspiration & dispension to default (7.6 µL/s for 20 µL multichannel pipettes).
    m20.flow_rate.aspirate = 7.6 ## µL/s
    m20.flow_rate.dispense = 7.6 ## µL/s

    ## Fill-in Reaction pipetting
    for i in range(Col_number):
        m20.transfer(volume = 7.5, source = Nick_Fill_In_Mix, dest = Sample_plate.wells_by_name()[col_name[i]], mix_before=(2,10), mix_after=(5,10), new_tip='always', trash = False)

    ## Fill-In Incubation
    protocol.comment("STATUS: Fill-In Incubation Step Begun")
    thermo_module.close_lid()
    profile = [
        {'temperature':65, 'hold_time_minutes':15},
        {'temperature':80, 'hold_time_minutes':15}]
    thermo_module.execute_profile(steps = profile, repetitions = 1, block_max_volume = 45)
    thermo_module.deactivate_lid() ## Turns off lid
    thermo_module.set_block_temperature(10) ## Reset to 10 C while working
    thermo_module.open_lid()


    ### Protocol finished ###
    protocol.set_rail_lights(False)
    protocol.pause("STATUS: Protocol Completed.")

    ## Shuts down modules
    thermo_module.deactivate()
    cold_module.deactivate()
