import pandas as pd 
from io import StringIO

#read_file = pd.read_excel("template\Template_CSV_LibraryInput.xlsx")
#df = pd.DataFrame(read_file)


#df['DNA volume (ul) for Covaris'] = df['DNA volume (ul) for Covaris'].fillna(0)
#df['Water volume (ul) for Covaris'] = df['Water volume (ul) for Covaris'].fillna(0)
#df['Adaptor concentration (nM)'] = df['Adaptor concentration (nM)'].fillna(0)

#print(df)

#print(df['Water volume (ul) for Covaris'])

#for i in range(0,96):
#    print(df['Well Position'][i])

#userinput = "user_data/User_Input.csv"
#df = pd.DataFrame(pd.read_csv(f'{userinput}', header=0)) 
#print(df)
#Info = df['User'][0]
#print(Info)



#csv_userinput = '''User, Protocol, Input, email
#Jonas, Library, LVL, jonas.lauritsen@sund.ku.dk'''

#data=StringIO(csv_userinput)

#df = pd.read_csv(data,header=0)
#print(df)
#print("Hellow")
#print(df['User'][0])


import pandas as pd

protocol = "Extraction"
user = "Jonas"
samplesnumber = 96
inputformat = "LVLSXS200"
outputformat = "LVLSXS200"
userdata = "user_data/User_Data.csv"

    
csv_user_input ={'Protocol':[protocol],
    'User':[user],
    'SampleNumber':[samplesnumber],
    'InputFormat':[inputformat],
    'OutputFormat':[outputformat]}

df = pd.DataFrame(csv_user_input)
print(df)
