#################################
### Covaris plate preparation ###
#################################

## Author Jonas Greve Lauritsen
## Automatic preparation of covaris plates based on csv input

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

    

##################################



#### Function to convert copied csv data into a 2D list. ####
def csv_list_converter_covaris(csv_raw):
    import csv
    csv_data = csv_raw.splitlines()[1:]
    csv_reader = csv.DictReader(csv_data)
    Excel = [['Well','Sample_Input_Vol','H2O_Input_Vol']]
    for csv_row in csv_reader:
        Info = [csv_row['#'], float(csv_row['DNA volume (ul) for Covaris']), float(csv_row['Water volume (ul) for Covaris'])]
        Excel.append(Info)
    return(Excel)


#### Function to convert a well number to a well identifier. ####
def Number_to_Well_Converter(Number):
    WellIndex = ['Null','A1','B1','C1','D1','E1','F1','G1','H1',
    'A2','B2','C2','D2','E2','F2','G2','H2',
    'A3','B3','C3','D3','E3','F3','G3','H3',
    'A4','B4','C4','D4','E4','F4','G4','H4',
    'A5','B5','C5','D5','E5','F5','G5','H5',
    'A6','B6','C6','D6','E6','F6','G6','H6',
    'A7','B7','C7','D7','E7','F7','G7','H7',
    'A8','B8','C8','D8','E8','F8','G8','H8',
    'A9','B9','C9','D9','E9','F9','G9','H9',
    'A10','B10','C10','D10','E10','F10','G10','H10',
    'A11','B11','C11','D11','E11','F11','G11','H11',
    'A12','B12','C12','D12','E12','F12','G12','H12']
    Well = WellIndex[Number]
    return(Well)


#### Function to reposition the sample well to the covaris plate. ####
def Covaris_Plate_Well_Repositioner(Sample_Well,Covaris_Well):
    WellName = ['A1','B1','C1','D1','E1','F1','G1','H1',
    'A2','B2','C2','D2','E2','F2','G2','H2',
    'A3','B3','C3','D3','E3','F3','G3','H3',
    'A4','B4','C4','D4','E4','F4','G4','H4',
    'A5','B5','C5','D5','E5','F5','G5','H5',
    'A6','B6','C6','D6','E6','F6','G6','H6',
    'A7','B7','C7','D7','E7','F7','G7','H7',
    'A8','B8','C8','D8','E8','F8','G8','H8',
    'A9','B9','C9','D9','E9','F9','G9','H9',
    'A10','B10','C10','D10','E10','F10','G10','H10',
    'A11','B11','C11','D11','E11','F11','G11','H11',
    'A12','B12','C12','D12','E12','F12','G12','H12']
    Wellindex = WellName.index(Sample_Well) + WellName.index(Covaris_Well)
    return(Wellindex)



#### Meta Data ####
metadata = {
    'protocolName': 'Protocol Automated Covaris Setup',
    'apiLevel': '2.13',
    'author': 'Jonas Lauritsen <jonas.lauritsen@sund.ku.dk>',
    'description': 'Covaris automated plate prepper with user CSV input. The user inputs csv data containing 1) well position, 2) sample input volume, and 3) H2O input volume. The columns need to be named "Well", "Sample_Input_Vol", & "H2O_Input_Vol" for it to be read correctly'}


#### Protocol Script ####
def run(protocol: protocol_api.ProtocolContext):

    #### LABWARE SETUP ####
    ## Input Plate
    if Input_Format == 'PCRstrip':
        Input_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', 2) ## PCR tubes/strips
    if Input_Format == 'Plate':
        Input_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr', 2) ## Plate
    if Input_Format == 'LVL': 
        Input_plate = protocol.load_labware('lvl_96_wellplate_200ul', 2) ## LVL SXS 200 tubes (200 µL tubes)
    
    
    ## Covaris Plate
    Covaris_plate = protocol.load_labware('96afatubetpxplate_96_wellplate_200ul', 3) #Custom labware (To add it use App -> 'More' -> 'Labware').


    ## Water position - if needed you can pause and exchange water as needed.
    Rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap',1)
    H2O_1 = Rack.wells_by_name()["A1"]
    H2O_2 = Rack.wells_by_name()["A2"] ## Personally hate this: Would prefer either to switch to new tube or to refill to avoid wasting plastic as 2 mL H20 would fit 80+ samples if there is a need of 23 µL per sample.
    #Rack = Rack_5ml = protocol.load_labware('opentrons_15_tuberack_5000ul',8)
    # H20 = Rack_5ml['A5']
    

    ## Tip racks (2x 10 µL, 2x 200 µl)
    tiprack_10_1 = protocol.load_labware('opentrons_96_filtertiprack_10ul',4)
    tiprack_10_2 = protocol.load_labware('opentrons_96_filtertiprack_10ul',7)
    tiprack_200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul',5)
    tiprack_200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul',6)


    #### PIPETTE SETUP ####
    ## Loading pipettes
    p20 = protocol.load_instrument('p10_single', mount='left', tip_racks=[tiprack_10_1,tiprack_10_2])
    p50 = protocol.load_instrument('p50_single', mount='right', tip_racks=[tiprack_200_1,tiprack_200_2])


    ## Setting start tips (based on user input)
    #p20.starting_tip = tiprack_10_1.well(First_Tip10)
    #p50.starting_tip = tiprack_200_1.well(First_Tip50)



    ############################### Lab Work Protocol ###############################
    ## The instructions for the robot to execute.
    protocol.comment("STATUS: Covaris Setup Begun")
    protocol.set_rail_lights(True)


    ## Converts User input (csv data) into a 2D list used in the Covaris work ##
    Excel = csv_list_converter_covaris(csv_raw)
    Excel = Excel[1:] ## Removes headers - Header indices are: [0] Well, [1] Sample_Input_Vol, & [2] H2O_Input_Vol.
    
    
    ## Set up counter
    Counter = 0

    ## Loop for transfering samples and H2O. The samples are "cherrypicked" samples from the the user input.
    for i in range(len(Excel)):


        if Counter < 71:
            H2O = H2O_1
        if Counter >= 71:
            H2O = H2O_2

        ## Counting the progress
        Counter = Counter + 1


        ## Variable definitions for the pipetting functions and positions.
        Well_pos = Number_to_Well_Converter(int(Excel[i][0])) ## Sample well (converted from numbet to name) from UserInput
        Covaris_Well_pos = Covaris_Plate_Well_Repositioner(Sample_Well = Well_pos, Covaris_Well = First_Covaris_Well) ## Covaris well repositioned based on sample well and first avaible covaris well.
        Sample_Input = csv_raw[i][1] # Variable setup for sample input (script readability)
        H2O_Input = [i][2] # Variable setup for H2O input (script readability)


        ## If the sample input volume is equal or greater to 5 µL, and the water input is lower than 5 µL:
        if Sample_Input >= 5 and H2O_Input < 5:

            ## Adding water first if water input volume is greater than 0.
            if H2O_Input > 0: # If command is here to prohibit picking up tips and disposing them without a transfer.
                p20.transfer(volume = H2O_Input, source = H2O, dest = Covaris_plate.wells()[Covaris_Well_pos], new_tip = 'always', trash = True) #Transfer pick up new tip

            ## Adding sample (to the water).
            p50.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[Well_pos], dest = Covaris_plate.wells()[Covaris_Well_pos], new_tip = 'Always', Trash = True, mix_after=(3,15), rate = 0.8)


        ## If the sample input volume is equal or greater to 5 µL, and the water input is also equal or greater than 5 µL:
        if Sample_Input >= 5 and H2O_Input >= 5:

            ## Aspirating H2O then sample, and dispense them together into the covaris plate. Both volume are aspirated together to save time.
            p50.pick_up_tip()
            p50.aspirate(volume = H2O_Input, location = H2O) # First pickup
            p50.touch_tip(location = H2O) # Touching the side of the well to remove excess water.
            p50.aspirate(volume = Sample_Input, location = Input_plate.wells_by_name()[Well_pos]) # Second pickup
            p50.dispense(volume = 30, location = Covaris_plate.wells()[Covaris_Well_pos]) # 30 µL dispense to empty completely
            p50.mix(repetitions = 3, volume = 15, location = Covaris_plate.wells()[Covaris_Well_pos], rate = 0.8)

            ## Transferring diluted samples to covaris plate
            p50.drop_tip()


        ## If sample input volume is less than 5 µL. (Water input volume is always above 5 µL here)
        if Sample_Input < 5:
            ## Adding sample to the Covaris plate.
            p20.transfer(volume = Sample_Input, source = Input_plate.wells_by_name()[Well_pos], dest = Covaris_plate.wells()[Covaris_Well_pos], new_tip = 'always', trash = True) #µL

            ## Dispensing H2O  into the Covaris plate.
            p50.transfer(volume = H2O_Input, source = H2O, dest = Covaris_plate.wells()[Covaris_Well_pos], new_tip = 'Always', trash = True, mix_after = (3,15), rate = 0.8) #µL


    protocol.set_rail_lights(False)
    protocol.comment("STATUS: Protocol Completed.")
