
import os
import glob
import pandas as pd
import sqlalchemy
import datetime as dt
import shutil

def get_chart(chart_type, start_date, end_date):
    # demo data
    chart_type = "RTSL"

    #connecting to sqlalchemy
    database_username = "admin"
    database_password = "dvqLt7v635tuf9Bf"
    database_ip = "txgridanalytics-database.c3xnwzdtzngd.us-east-2.rds.amazonaws.com"
    database_name = "GRID_ANALYTICS"
    #port = "3306"
    database_connection = sqlalchemy.create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.
                                                   format(database_username, database_password, 
                                                          database_ip, database_name))
    connection = database_connection.connect() 

    df = pd.read_sql_table(chart_type, connection)
    return df


# def updateTable(table, source):
    
#     for file in glob.glob("*.csv"):
#         df = pd.read_csv(file)

#         df.rename(columns = {list(df)[0]:'OperatingDay', list(df)[1]:'HourEnding'}, inplace=True)   # Assumes that the first two columns in a df are Date and Time

#         df["OperatingDay"] = pd.to_datetime(df["OperatingDay"]).dt.date
#         df["HourEnding"] = df["HourEnding"] + ":00"
#         df.to_sql(con=connection, name=table, if_exists='append', index=False)
#         print(file)

#     os.chdir("..")
#     try:
#         shutil.rmtree(table)
#         print('Done')
#     except:
#         print("Unhandled Deletion Exception")

#     cursor.close()
#     db.close()
