import os
import glob
import pandas as pd
import sqlalchemy
import datetime as dt
from DownloadSA import DownloadSA
from UnzipFiles import Unzip
import shutil
from dotenv import load_dotenv

import os
from dotenv import load_dotenv

# updateTable(table, source)
#   Input:  Table = Name of the table to update
#           Source = ERCOT URL
#
#   Output: None
#
#   Uses DownloadSA and UnzipFiles functions to download zips, unzip, and upload csv's to DB
#   Downloads to directory '/tmp/<table>' but deletes '/<table>' directory at end   


def updateTable(table, source):
    # import enviornment variables
    load_dotenv(dotenv_path="../.env")

    #connecting to sqlalchemy
    database_username = os.getenv("DB_USERNAME")
    database_password = os.getenv("DB_PASSWORD")
    database_ip = os.getenv("DB_IP")
    database_name = os.getenv("DB_NAME")
    #port = "3306"
    database_connection = sqlalchemy.create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.
                                                   format(database_username, database_password, 
                                                          database_ip, database_name))
    connection = database_connection.connect() 

    #When implementing to Lambda, folder -> </tmp/ + KEY> 
    DownloadSA(source, 'tmp/' + table)
    Unzip('tmp/' + table)

    os.chdir("tmp/" + table)
    for file in glob.glob("*.csv"):
        df = pd.read_csv(file)

        if table == "SWL" or table == "RTSL":
            df.rename(columns = {list(df)[0]:'OperatingDay', list(df)[1]:'HourEnding'}, inplace=True)
            df["OperatingDay"] = pd.to_datetime(df["OperatingDay"]).dt.date
            df["HourEnding"] = df["HourEnding"] + ":00"

        if table == "WPP":
            df.rename(columns = {list(df)[0]:'Timestamp', list(df)[1]:'SystemWide', list(df)[2]:'LZSouthHouston', list(df)[3]:'LZWest', list(df)[4]:'LZNorth'}, inplace=True)
            df["OperatingDay"] = pd.to_datetime(df["Timestamp"]).dt.date
            df["HourEnding"] = pd.to_datetime(df["Timestamp"]).dt.time
            df = df.drop(['Timestamp'], axis=1)

        if table == "SPP":
            df.rename(columns = {list(df)[0]:'Timestamp', list(df)[1]:'SystemWide'}, inplace=True)
            df["OperatingDay"] = pd.to_datetime(df["Timestamp"]).dt.date
            df["HourEnding"] = pd.to_datetime(df["Timestamp"]).dt.time
            df = df.drop(['Timestamp'], axis=1)

        if table == "SEL":
            df.rename(columns = {list(df)[0]:'Timestamp'}, inplace=True)
            df["OperatingDay"] = pd.to_datetime(df["Timestamp"]).dt.date
            df["HourEnding"] = pd.to_datetime(df["Timestamp"]).dt.time
            df = df.drop(["Timestamp"], axis=1)

        df.to_sql(con=connection, name=table, if_exists='append', index=False)
        print(file)

    os.chdir("..")
    try:
        shutil.rmtree(table)
        print('Done')
    except:
        print("Unhandled Deletion Exception")
