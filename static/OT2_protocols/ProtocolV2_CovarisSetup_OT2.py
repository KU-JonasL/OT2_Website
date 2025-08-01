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


#### User Input Parameters ###
def add_parameters(parameters):

    ## CSV file load
    #SampleNumber;WellPosition;EXBarcode;SampleID;DNAconc;DNAul;Waterul;Adaptor;Notes
    parameters.add_csv_file(
        variable_name = "DNAnormalisingwells",
        display_name = "DNA Normalisation File",
        description = "csv file with normalisation information"
    )

    ## First Tip Available 200 uL
    parameters.add_str(
        variable_name = "First_Tip10",
        display_name = "First tip available, P10 tips",
        default = "A1",
        choices = [{"display_name": "A1", "value": "A1"},
            {"display_name": "A2", "value": "A2"},
            {"display_name": "A3", "value": "A3"},
            {"display_name": "A4", "value": "A4"},
            {"display_name": "A5", "value": "A5"},
            {"display_name": "A6", "value": "A6"},
            {"display_name": "A7", "value": "A7"},
            {"display_name": "A8", "value": "A8"},
            {"display_name": "A9", "value": "A9"},
            {"display_name": "A10", "value": "A10"},
            {"display_name": "A11", "value": "A11"},
            {"display_name": "A12", "value": "A12"},
            {"display_name": "B1", "value": "B1"},
            {"display_name": "B2", "value": "B2"},
            {"display_name": "B3", "value": "B3"},
            {"display_name": "B4", "value": "B4"},
            {"display_name": "B5", "value": "B5"},
            {"display_name": "B6", "value": "B6"},
            {"display_name": "B7", "value": "B7"},
            {"display_name": "B8", "value": "B8"},
            {"display_name": "B9", "value": "B9"},
            {"display_name": "B10", "value": "B10"},
            {"display_name": "B11", "value": "B11"},
            {"display_name": "B12", "value": "B12"},
            {"display_name": "C1", "value": "C1"},
            {"display_name": "C2", "value": "C2"},
            {"display_name": "C3", "value": "C3"},
            {"display_name": "C4", "value": "C4"},
            {"display_name": "C5", "value": "C5"},
            {"display_name": "C6", "value": "C6"},
            {"display_name": "C7", "value": "C7"},
            {"display_name": "C8", "value": "C8"},
            {"display_name": "C9", "value": "C9"},
            {"display_name": "C10", "value": "C10"},
            {"display_name": "C11", "value": "C11"},
            {"display_name": "C12", "value": "C12"},
            {"display_name": "D1", "value": "D1"},
            {"display_name": "D2", "value": "D2"},
            {"display_name": "D3", "value": "D3"},
            {"display_name": "D4", "value": "D4"},
            {"display_name": "D5", "value": "D5"},
            {"display_name": "D6", "value": "D6"},
            {"display_name": "D7", "value": "D7"},
            {"display_name": "D8", "value": "D8"},
            {"display_name": "D9", "value": "D9"},
            {"display_name": "D10", "value": "D10"},
            {"display_name": "D11", "value": "D11"},
            {"display_name": "D12", "value": "D12"},
            {"display_name": "E1", "value": "E1"},
            {"display_name": "E2", "value": "E2"},
            {"display_name": "E3", "value": "E3"},
            {"display_name": "E4", "value": "E4"},
            {"display_name": "E5", "value": "E5"},
            {"display_name": "E6", "value": "E6"},
            {"display_name": "E7", "value": "E7"},
            {"display_name": "E8", "value": "E8"},
            {"display_name": "E9", "value": "E9"},
            {"display_name": "E10", "value": "E10"},
            {"display_name": "E11", "value": "E11"},
            {"display_name": "E12", "value": "E12"},
            {"display_name": "F1", "value": "F1"},
            {"display_name": "F2", "value": "F2"},
            {"display_name": "F3", "value": "F3"},
            {"display_name": "F4", "value": "F4"},
            {"display_name": "F5", "value": "F5"},
            {"display_name": "F6", "value": "F6"},
            {"display_name": "F7", "value": "F7"},
            {"display_name": "F8", "value": "F8"},
            {"display_name": "F9", "value": "F9"},
            {"display_name": "F10", "value": "F10"},
            {"display_name": "F11", "value": "F11"},
            {"display_name": "F12", "value": "F12"},
            {"display_name": "G1", "value": "G1"},
            {"display_name": "G2", "value": "G2"},
            {"display_name": "G3", "value": "G3"},
            {"display_name": "G4", "value": "G4"},
            {"display_name": "G5", "value": "G5"},
            {"display_name": "G6", "value": "G6"},
            {"display_name": "G7", "value": "G7"},
            {"display_name": "G8", "value": "G8"},
            {"display_name": "G9", "value": "G9"},
            {"display_name": "G10", "value": "G10"},
            {"display_name": "G11", "value": "G11"},
            {"display_name": "G12", "value": "G12"},
            {"display_name": "H1", "value": "H1"},
            {"display_name": "H2", "value": "H2"},
            {"display_name": "H3", "value": "H3"},
            {"display_name": "H4", "value": "H4"},
            {"display_name": "H5", "value": "H5"},
            {"display_name": "H6", "value": "H6"},
            {"display_name": "H7", "value": "H7"},
            {"display_name": "H8", "value": "H8"},
            {"display_name": "H9", "value": "H9"},
            {"display_name": "H10", "value": "H10"},
            {"display_name": "H11", "value": "H11"},
            {"display_name": "H12", "value": "H12"}]
    )

    ## First Tip Available 10 uL
    parameters.add_str(
        variable_name = "First_Tip50",
        display_name = "First tip available, P50 tips",
        default = "A1",
        choices = [{"display_name": "A1", "value": "A1"},
            {"display_name": "A2", "value": "A2"},
            {"display_name": "A3", "value": "A3"},
            {"display_name": "A4", "value": "A4"},
            {"display_name": "A5", "value": "A5"},
            {"display_name": "A6", "value": "A6"},
            {"display_name": "A7", "value": "A7"},
            {"display_name": "A8", "value": "A8"},
            {"display_name": "A9", "value": "A9"},
            {"display_name": "A10", "value": "A10"},
            {"display_name": "A11", "value": "A11"},
            {"display_name": "A12", "value": "A12"},
            {"display_name": "B1", "value": "B1"},
            {"display_name": "B2", "value": "B2"},
            {"display_name": "B3", "value": "B3"},
            {"display_name": "B4", "value": "B4"},
            {"display_name": "B5", "value": "B5"},
            {"display_name": "B6", "value": "B6"},
            {"display_name": "B7", "value": "B7"},
            {"display_name": "B8", "value": "B8"},
            {"display_name": "B9", "value": "B9"},
            {"display_name": "B10", "value": "B10"},
            {"display_name": "B11", "value": "B11"},
            {"display_name": "B12", "value": "B12"},
            {"display_name": "C1", "value": "C1"},
            {"display_name": "C2", "value": "C2"},
            {"display_name": "C3", "value": "C3"},
            {"display_name": "C4", "value": "C4"},
            {"display_name": "C5", "value": "C5"},
            {"display_name": "C6", "value": "C6"},
            {"display_name": "C7", "value": "C7"},
            {"display_name": "C8", "value": "C8"},
            {"display_name": "C9", "value": "C9"},
            {"display_name": "C10", "value": "C10"},
            {"display_name": "C11", "value": "C11"},
            {"display_name": "C12", "value": "C12"},
            {"display_name": "D1", "value": "D1"},
            {"display_name": "D2", "value": "D2"},
            {"display_name": "D3", "value": "D3"},
            {"display_name": "D4", "value": "D4"},
            {"display_name": "D5", "value": "D5"},
            {"display_name": "D6", "value": "D6"},
            {"display_name": "D7", "value": "D7"},
            {"display_name": "D8", "value": "D8"},
            {"display_name": "D9", "value": "D9"},
            {"display_name": "D10", "value": "D10"},
            {"display_name": "D11", "value": "D11"},
            {"display_name": "D12", "value": "D12"},
            {"display_name": "E1", "value": "E1"},
            {"display_name": "E2", "value": "E2"},
            {"display_name": "E3", "value": "E3"},
            {"display_name": "E4", "value": "E4"},
            {"display_name": "E5", "value": "E5"},
            {"display_name": "E6", "value": "E6"},
            {"display_name": "E7", "value": "E7"},
            {"display_name": "E8", "value": "E8"},
            {"display_name": "E9", "value": "E9"},
            {"display_name": "E10", "value": "E10"},
            {"display_name": "E11", "value": "E11"},
            {"display_name": "E12", "value": "E12"},
            {"display_name": "F1", "value": "F1"},
            {"display_name": "F2", "value": "F2"},
            {"display_name": "F3", "value": "F3"},
            {"display_name": "F4", "value": "F4"},
            {"display_name": "F5", "value": "F5"},
            {"display_name": "F6", "value": "F6"},
            {"display_name": "F7", "value": "F7"},
            {"display_name": "F8", "value": "F8"},
            {"display_name": "F9", "value": "F9"},
            {"display_name": "F10", "value": "F10"},
            {"display_name": "F11", "value": "F11"},
            {"display_name": "F12", "value": "F12"},
            {"display_name": "G1", "value": "G1"},
            {"display_name": "G2", "value": "G2"},
            {"display_name": "G3", "value": "G3"},
            {"display_name": "G4", "value": "G4"},
            {"display_name": "G5", "value": "G5"},
            {"display_name": "G6", "value": "G6"},
            {"display_name": "G7", "value": "G7"},
            {"display_name": "G8", "value": "G8"},
            {"display_name": "G9", "value": "G9"},
            {"display_name": "G10", "value": "G10"},
            {"display_name": "G11", "value": "G11"},
            {"display_name": "G12", "value": "G12"},
            {"display_name": "H1", "value": "H1"},
            {"display_name": "H2", "value": "H2"},
            {"display_name": "H3", "value": "H3"},
            {"display_name": "H4", "value": "H4"},
            {"display_name": "H5", "value": "H5"},
            {"display_name": "H6", "value": "H6"},
            {"display_name": "H7", "value": "H7"},
            {"display_name": "H8", "value": "H8"},
            {"display_name": "H9", "value": "H9"},
            {"display_name": "H10", "value": "H10"},
            {"display_name": "H11", "value": "H11"},
            {"display_name": "H12", "value": "H12"}]
    )

    ## Input Format
    parameters.add_str(
        variable_name = "input_plate_type",
        display_name = "Well plate type",
        choices = [{"display_name": "PCR Strips (Aluminumblock)", "value": "opentrons_96_aluminumblock_generic_pcr_strip_200ul"},
        {"display_name": "LVL XSX 200 tubes (LVL plate)", "value": "LVLXSX200_wellplate_200ul"},
        {"display_name": "PCR Plate", "value": "biorad_96_wellplate_200ul_pcr"}],
        default="biorad_96_wellplate_200ul_pcr",
    )

##################################

#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Automated Covaris Setup',
    'apiLevel': '2.22',
    'robotType': 'OT-2',    
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': "Covaris automated plate prepper with user CSV input. Protocol generated at https://alberdilab-opentronsscripts.onrender.com"}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### Loading Protocol Runtime Parameters ####
    parsed_data = protocol.params.DNAnormalisingwells.parse_as_csv()
    user_data = pd.DataFrame(parsed_data[1:], columns = parsed_data[0])


    #### LABWARE SETUP ####
    ## Input Plate - defaults to PCR wellplate
    Input_plate = protocol.load_labware(protocol.params.input_plate_type)
    
    ## Covaris Plate - custom labware
    Covaris_plate = protocol.load_labware('96afatubetpxplate_96_wellplate_200ul', 3) 
        
    ## Water position - if needed you can pause and exchange water as needed.
    Rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',1)
    H2O_1 = Rack.wells_by_name()["A1"]
    H2O_2 = Rack.wells_by_name()["A2"]

    ## Load liquid
    dH2O = protocol.define_liquid(name = "Sterile, Demineralised Water", description = "Water for Normalisation", display_color = "#336CFF")
    H2O_1.load_liquid(liquid = dH2O, volume = 2000)
    H2O_2.load_liquid(liquid = dH2O, volume = 2000)
    
    ## Tip racks (2x 10 µL, 2x 200 µl)
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',4)
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',7)
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',6)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    p10 = protocol.load_instrument('p10_single', mount='left', tip_racks=[tiprack_10_1,tiprack_10_2])
    p50 = protocol.load_instrument('p50_single', mount='right', tip_racks=[tiprack_200_1,tiprack_200_2])

    ## Setting start tips (based on user input)
    p10.starting_tip = tiprack_10_1.well(protocol.params.First_Tip10)
    p50.starting_tip = tiprack_200_1.well(protocol.params.First_Tip50)


    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Covaris Setup Begun")
    protocol.set_rail_lights(True)

   
    ## Set up counters for upcoming loop
    H2O = H2O_1
    H2O_available = 2000
    

    ## Loop for transfering samples and H2O. The samples are "cherrypicked" samples from the the user input.
    for i in range(len(user_data)):

        ## Find Sample volume and water volume for transfer.
        #SampleNumber;WellPosition;EXBarcode;SampleID;DNAconc;DNAul;Waterul;Adaptor;Notes
        WellPosition = user_data['WellPosition'][i]
        Sample_Input = user_data['DNAul'][i]
        H2O_Input = user_data['Waterul'][i]
        Total_Input = (Sample_Input+H2O_Input)

        ## If more than 1950 uL has been removed, second tube is used
        if H2O_available < 50:
            H2O = H2O_2
            H2O_available = 2000
        H2O_available = H2O_available - H2O_Input


        #### If the sample input volume is equal or greater to 5 µL, and the water input is lower than 5 µL: ####
        if Sample_Input >= 5 and H2O_Input < 5:

            ## Adding water first if water input volume is greater than 0. ##
            if H2O_Input > 0: # If command prohibits picking up tips and disposing them without a transfer.
                p10.transfer(volume = H2O_Input, source = H2O.bottom(z = 2.0), dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'always', trash = True) #Transfer pick up new tip

            ## Adding sample (to the water).
            p50.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[WellPosition], dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'Always', Trash = True, mix_after=(3,15), rate = 0.8)


        #### If the sample input volume is equal or greater to 5 µL, and the water input is also equal or greater than 5 µL: ####
        elif Sample_Input >= 5 and H2O_Input >= 5:

            ## Aspirating H2O then sample, and dispense them together into the covaris plate. Both volume are aspirated together to save time.
            p50.pick_up_tip()
            p50.aspirate(volume = H2O_Input, location = H2O.bottom(z = 2.0)) # First pickup
            p50.touch_tip(location = H2O) # Touching the side of the well to remove excess water.
            p50.aspirate(volume = Sample_Input, location = Input_plate.wells_by_name()[WellPosition]) # Second pickup of DNA
            p50.dispense(volume = Total_Input, location = Covaris_plate.wells_by_name()[WellPosition]) # 30 µL dispense to empty completely
            p50.mix(repetitions = 3, volume = 15, location = Covaris_plate.wells_by_name()[WellPosition], rate = 0.8)

            ## Transferring diluted samples to covaris plate
            p50.drop_tip()


        #### If sample input volume is less than 5 µL. (Water input volume is always above 5 µL here) ####
        elif Sample_Input < 5:
            ## Adding sample to the Covaris plate.
            p10.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[WellPosition], dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'always', trash = True) #µL

            ## Dispensing H2O into the Covaris plate.
            p50.transfer(volume = H2O_Input, source = H2O.bottom(z = 2.0), dest = Covaris_plate.wells_by_name()[WellPosition], new_tip = 'Always', trash = True, mix_after = (3,15), rate = 0.8) #µL



    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
