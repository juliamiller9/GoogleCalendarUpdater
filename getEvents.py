from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

#name of file to be read
filename = "CyclotronSched.html"

#use BeautifulSoup package to put parser onto file
with open(filename) as fp:
    soup = BeautifulSoup(fp, "html.parser")

#find all span elements to create array of text in file
data = np.array(soup.find_all("span"))

#iterate through array, stripping whitespace from each value
for index, value in enumerate(data):
    data[index] = np.char.strip(value)
    
data_length = data.size

#remove header text and column indices
data = data[8::] 

#resize the data into rows and columns
data = np.reshape(data, ((int((data_length-8)/6)),6))

#create a dataframe using data with appropriate column headers
df = pd.DataFrame(data, columns=["ID", "Time", "Desc.", "Location", "MD", "Notes"])

#remove rows with lunch and repeated column headers
df = df[df["ID"] != "null"]
df = df[df["ID"] != "App_DtTm"]

#drop the ID column to protect patient info
df = df.drop(["ID"], axis =1)

#drop unnecessary columns
df = df.drop(["MD"], axis =1)
df = df.drop(["Location"], axis =1)

#reset indices after dropping rows
df = df.reset_index().drop(["index"], axis=1)

#create a new column in the dataframe indicating event type (IMNT, conformal, VISM, or TBI)
types = ["" for x in range(len(df.index))]
for index, row in df.iterrows():
    if row["Desc."] == "Neutrons TC":
        if row["Notes"].find("IMNT") == -1:
            types[index] = "Conformal"
        elif row["Notes"].find("VSIM") == 1:
            types[index] = "VSIM"
        else:
            types[index] = "IMNT"
    elif row["Desc."] == "Verify Sim":
        types[index] = "VSIM"
    elif row["Desc."] == "Sim No Charge":
        types[index] = "TBI"
    else:
        types[index] == "Unknown"

df["Type"] = types

#drop unnecessary columns
df = df.drop(["Notes"], axis =1)
df = df.drop(["Desc."], axis =1)

df["Time"] = pd.to_datetime(df["Time"])

print(df)