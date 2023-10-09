from time import strftime
import pandas as pd
import sqlalchemy
import datetime
import os

def td_to_dt(td):
    time = [str(td.components.hours), str(td.components.minutes), str(td.components.seconds)]
    return datetime.datetime.strptime(':'.join(time), '%H:%M:%S').time()

def combine_date_time_24bug(date, time):
    combined = []
    for x in range(len(date)):
        if time[x] == datetime.time(hour=0, minute=0):
            temp_combination = str(datetime.datetime.combine(date[x] + datetime.timedelta(days=1), time[x]).strftime('%Y-%m-%d %H:%M'))
        else:
            temp_combination = str(datetime.datetime.combine(date[x], time[x]).strftime('%Y-%m-%d %H:%M'))
        combined.append(temp_combination)
    return combined

def combine_date_time(date, time):
    combined = []
    for x in range(len(date)):
        combined.append(str(datetime.datetime.combine(date[x], time[x]).strftime('%Y-%m-%d %H:%M')))
    return combined

def convert_date_time(dates, times):
    dates_dt = []
    for day in dates:
        dates_dt.append(pd.Timestamp.to_pydatetime(day))
    return combine_date_time_24bug(dates_dt, times)

def get_chart(chart_type, start_date, end_date):

    #connecting to sqlalchemy
    database_username = os.getenv("DB_USERNAME")
    database_password = os.getenv("DB_PASSWORD")
    database_ip = os.getenv("DB_IP")
    database_name = os.getenv("DB_NAME")
    #port = os.getenv("DB_PORT")
    database_connection = sqlalchemy.create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.
                                                   format(database_username, database_password, 
                                                          database_ip, database_name))
    connection = database_connection.connect() 

    # -----------------------------------
    # System Wide Demand
    # -----------------------------------
    if chart_type == "system-wide-demand":
        if (start_date and end_date):
            end_date = pd.Timestamp(end_date)
            start_date = pd.Timestamp(start_date)
            query = """SELECT * FROM GRID_ANALYTICS.SWD WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        else:
            query = """SELECT * FROM GRID_ANALYTICS.SWD ORDER BY OperatingDay DESC LIMIT 1"""
            df = pd.read_sql_query(query, connection)
            end_date = df.iloc[-1].get('OperatingDay')
            # DEFAULT VIEW: two weeks
            start_date = end_date - pd.Timedelta(days=14)
            query = """SELECT * FROM GRID_ANALYTICS.SWD WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        df = pd.read_sql_query(query, connection)
        
        ch_data_mw = df["Demand"].tolist()
        ch_data = [entry / 1000 for entry in ch_data_mw]
        
        df["HourEnding"] = df["HourEnding"].apply(td_to_dt)
        ch_times = df['HourEnding'].tolist()
        ch_days = df['OperatingDay'].tolist()

        ch_labels = combine_date_time(ch_days, ch_times)
        return ch_data, ch_labels

    # -----------------------------------
    # Fuel Type Generation
    # TODO Decimate
    # -----------------------------------
    if chart_type == "fuel-type-generation":
        if (start_date and end_date):
            end_date = pd.Timestamp(end_date)
            start_date = pd.Timestamp(start_date)
            query = """SELECT * FROM GRID_ANALYTICS.GBFT WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        else:
            query = """SELECT * FROM GRID_ANALYTICS.GBFT ORDER BY OperatingDay DESC LIMIT 1"""
            df = pd.read_sql_query(query, connection)
            end_date = df.iloc[-1].get('OperatingDay')
            # DEFAULT VIEW: one week
            start_date = end_date - pd.Timedelta(days=7)
            query = """SELECT * FROM GRID_ANALYTICS.GBFT WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        df = pd.read_sql_query(query, connection)        
        df = df.sort_values(by=['OperatingDay', 'HourEnding'])

        ch_data = {
            "Biomass": df["Biomass"].tolist(),
            "Coal": df["Coal"].tolist(),
            "Gas": df["Gas"].tolist(),
            "Gas-CC": df["Gas-CC"].tolist(),
            "Hydro": df["Hydro"].tolist(),
            "Nuclear": df["Nuclear"].tolist(),
            "Other": df["Other"].tolist(),
            "Solar": df["Solar"].tolist(),
            "Wind": df["Wind"].tolist()
        }

        df["HourEnding"] = df["HourEnding"].apply(td_to_dt)
        ch_times = df['HourEnding'].tolist()
        ch_days = df['OperatingDay'].tolist()
        
        ch_labels = combine_date_time_24bug(ch_days, ch_times)
        return ch_data, ch_labels

    # -----------------------------------
    # System Frequency
    # TODO hour selector
    # -----------------------------------
    if chart_type == "system-frequency":
        if (start_date and end_date):
            end_date = pd.Timestamp(end_date)
            start_date = pd.Timestamp(start_date)
            query = """SELECT * FROM GRID_ANALYTICS.RTSC WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        else:
            query = """SELECT * FROM GRID_ANALYTICS.RTSC ORDER BY OperatingDay DESC LIMIT 1"""
            df = pd.read_sql_query(query, connection)
            end_date = df.iloc[-1].get('OperatingDay')
            # DEFAULT VIEW: one day
            start_date = end_date - pd.Timedelta(days=1)
            query = """SELECT * FROM GRID_ANALYTICS.RTSC WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        df = pd.read_sql_query(query, connection)

        ch_data = df["CurrentFrequency"].tolist()

        df["HourEnding"] = df["HourEnding"].apply(td_to_dt)
        ch_times = df['HourEnding'].tolist()
        ch_days = df['OperatingDay'].tolist()
        
        ch_labels = combine_date_time(ch_days, ch_times)
        return ch_data, ch_labels
    
    # -----------------------------------
    # Wind and PV
    # -----------------------------------
    if chart_type == "wind-and-pv":
        if (start_date and end_date):
            end_date = pd.Timestamp(end_date)
            start_date = pd.Timestamp(start_date)
            query = """SELECT * FROM GRID_ANALYTICS.SPP WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        else:
            query = """SELECT * FROM GRID_ANALYTICS.SPP ORDER BY OperatingDay DESC LIMIT 1"""
            df = pd.read_sql_query(query, connection)
            end_date = df.iloc[-1].get('OperatingDay')
            # DEFAULT VIEW: one week
            start_date = end_date - pd.Timedelta(days=7)
            query = """SELECT * FROM GRID_ANALYTICS.SPP WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        df = pd.read_sql_query(query, connection)

        pv_data = df['SystemWide'].tolist()
        # PV Times are the same as Wind Times so disregard one or the other

        if (start_date and end_date):
            end_date = pd.Timestamp(end_date)
            start_date = pd.Timestamp(start_date)
            query = """SELECT * FROM GRID_ANALYTICS.WPP WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        else:
            query = """SELECT * FROM GRID_ANALYTICS.WPP ORDER BY OperatingDay DESC LIMIT 1"""
            df = pd.read_sql_query(query, connection)
            end_date = df.iloc[-1].get('OperatingDay')
            # DEFAULT VIEW: one week
            start_date = end_date - pd.Timedelta(days=7)
            query = """SELECT * FROM GRID_ANALYTICS.WPP WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        df = pd.read_sql_query(query, connection)
        
        wind_data = df['SystemWide'].tolist()


        df["HourEnding"] = df["HourEnding"].apply(td_to_dt)
        wind_times = df['HourEnding'].tolist()
        wind_days = df['OperatingDay'].tolist()

        wind_labels = combine_date_time(wind_days, wind_times)
        return [wind_data, pv_data], wind_labels

    # -----------------------------------
    # Electricity Prices
    # -----------------------------------
    if chart_type == "electricity-prices":
        if (start_date and end_date):
            end_date = pd.Timestamp(end_date)
            start_date = pd.Timestamp(start_date)
            query = """SELECT * FROM GRID_ANALYTICS.SMPP_LZ WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        else:
            query = """SELECT * FROM GRID_ANALYTICS.SMPP_LZ ORDER BY OperatingDay DESC LIMIT 1"""
            df = pd.read_sql_query(query, connection)
            end_date = df.iloc[-1].get('OperatingDay')
            # DEFAULT VIEW: one day
            start_date = end_date - pd.Timedelta(days=1)
            query = """SELECT * FROM GRID_ANALYTICS.SMPP_LZ WHERE OperatingDay BETWEEN '""" + start_date.strftime("%Y-%m-%d") + """' AND '""" + end_date.strftime("%Y-%m-%d") +"""'"""
        df = pd.read_sql_query(query, connection)
 
        df = df.sort_values(by=['SettlementPointName', 'OperatingDay', 'HourEnding'])

        df = df.pivot(index=['OperatingDay','HourEnding'], columns=['SettlementPointName'], values=['SettlementPointPrice'])
        df.reset_index(inplace=True)

        ch_data = {
            "LZ_AEN": df["SettlementPointPrice"]["LZ_AEN"].tolist(),
            "LZ_CPS": df["SettlementPointPrice"]["LZ_CPS"].tolist(),
            "LZ_HOUSTON": df["SettlementPointPrice"]["LZ_HOUSTON"].tolist(),
            "LZ_LCRA": df["SettlementPointPrice"]["LZ_LCRA"].tolist(),
            "LZ_NORTH": df["SettlementPointPrice"]["LZ_NORTH"].tolist(),
            "LZ_RAYBN": df["SettlementPointPrice"]["LZ_RAYBN"].tolist(),
            "LZ_SOUTH": df["SettlementPointPrice"]["LZ_SOUTH"].tolist(),
            "LZ_WEST": df["SettlementPointPrice"]["LZ_WEST"].tolist()
        }

        df["HourEnding"] = df["HourEnding"].apply(td_to_dt)
        ch_times = df['HourEnding'].tolist()
        ch_days = df['OperatingDay'].tolist()
        
        ch_labels = combine_date_time(ch_days, ch_times)
        return ch_data, ch_labels

    return pd.read_sql_table(chart_type, connection)