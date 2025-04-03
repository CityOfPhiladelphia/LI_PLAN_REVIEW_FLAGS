import os
from li_dbs import DataBridge_SQLALCHEMY
import pandas as pd
from sqlalchemy import text
from li_utils import li_utils
import traceback
import sys

try:
    query_folder = r'D:\LI_PLAN_REVIEW_FLAGS\queries'

    engine = DataBridge_SQLALCHEMY.engine

    conn = engine.connect()

    # Set statement_timeout once for the entire connection
    conn.execute(text("SET statement_timeout = '1500s'"))

    # Function to read SQL query from file
    def read_sql_query(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    # Function to execute a query and return a dataframe
    def execute_query_to_df(conn, query):
        # cur = conn.cursor()
        # conn.execute("SET statement_timeout = 1200000;")
        return pd.read_sql(query, conn)

    # Main function to process queries in "queries" folder
    def process_queries(queries_folder):

        # Create a dictionary to store dataframes keyed by query file name
        query_dfs = {}

        # Loop through all SQL files in the 'queries' folder
        for query_file in os.listdir(query_folder):
            if query_file.endswith('.sql'):  # Ensure it's a SQL file
                query_path = os.path.join(query_folder, query_file)

                # Read the query from the file
                query = read_sql_query(query_path)

                # Execute the query and store the result in a dataframe
                try:
                    df = execute_query_to_df(conn, query)
                    query_dfs[query_file.replace('.sql', '_df')] = df  # Save the dataframe with the query file name as key. Replace '.sql' with '_df'
                except Exception as e:
                    print(f"Error executing query {query_file}: {e}")

        conn.close()

        return query_dfs

    query_dfs = process_queries(query_folder)

    # Now `query_dfs` contains a dictionary of dataframes with query file names as keys
    for query_file, df in query_dfs.items():
        print(f"Data for query: {query_file}")
        print(df.head())  # Preview first few rows of the dataframe

    # Add flag fields to parcel data
    # 0 = field name of field to be added, 1 = data type of field to be added, 2 = name of boolean flag field in li_pr_flag_summary
    parcel_field_dict = {
        'pac_flag': 'Int16',
        'pac_review_type': 'object',
        'pcpc_flag': 'Int16',
        'pcpc_review_type': 'object',
        'phc_flag': 'Int16',
        'phc_review_type': 'object',
        'pwd_flag': 'Int16',
        'pwd_review_type': 'object',
        'corner_property': 'Int16',
        'base_zoning': 'object',
        'overlay_zoning': 'object',
        'li_inspection_district': 'object',
        'floodplain': 'Int16',
        'steep_slope': 'Int16',
        'zoning_rco': 'object',
        'phcadjacent_flag': 'Int16',
        'phcadjacent_review_type': 'object'
    }

    # Add the columns from the dictionary to the parcel dataframe
    for field, field_type in parcel_field_dict.items():
        query_dfs['pwd_parcels_df'][field] = pd.Series([None] * len(df), dtype=field_type)

    # 1. merge parcels with corner properties, then drop the unnecessary columns
    print('Starting to merge dataframes.')
    merged_df = pd.merge(query_dfs['pwd_parcels_df'],query_dfs['corner_properties_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['corner_property'] = merged_df['_merge'].apply(lambda x: 1 if x == 'both' else 0)
    merged_df = merged_df.drop(columns=['parcel_id','_merge'])

    # 2. merge parcels with floodplains
    merged_df = merged_df.merge(query_dfs['floodplain_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['floodplain'] = merged_df['_merge'].apply(lambda x: 1 if x == 'both' else 0)
    merged_df = merged_df.drop(columns=['_merge','parcel_id'])

    # 3. merge parcels with li districts
    merged_df = merged_df.merge(query_dfs['li_districts_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['li_inspection_district'] = merged_df.apply(lambda row: row['district'] if row['_merge'] == 'both' else None, axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id','district'])

    # 4. merge parcels with phc_flags
    merged_df = merged_df.merge(query_dfs['phc_flag_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['phc_flag'] = merged_df.apply(lambda row: 1 if row['_merge'] == 'both' else 0, axis=1)
    merged_df['phc_review_type'] = merged_df.apply(lambda row: 'Historic Designation' if row['_merge'] == 'both' else None, axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id'])

    # 5. merge parcels with phcadjacent_flags df
    merged_df = merged_df.merge(query_dfs['phcadjacent_flag_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['phcadjacent_flag'] = merged_df.apply(lambda row: 1 if row['_merge'] == 'both' else 0, axis=1)
    merged_df['phcadjacent_review_type'] = merged_df.apply(lambda row: 'PHC Adjacent' if row['_merge'] == 'both' else None, axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id'])

    # 6. merge parcels with pwd green infrastructure df
    merged_df = merged_df.merge(query_dfs['pwd_flag_green_infrastructure_review_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['pwd_flag'] = merged_df.apply(lambda row: 1 if row['_merge'] == 'both' else 0, axis=1)
    merged_df['pwd_review_type'] = merged_df.apply(lambda row: 'Green Infrastructure' if row['_merge'] == 'both' else None, axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id'])

    # merge parcels with green roof df
    merged_df = merged_df.merge(query_dfs['pwd_flag_green_roof_review_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['pwd_flag'] = merged_df.apply(lambda row: 1 if row['_merge'] == 'both' or row['pwd_flag'] == 1 else 0, axis=1)
    merged_df['pwd_review_type'] = merged_df.apply(lambda row: 'GREEN ROOF' if row['_merge'] == 'both' and row['pwd_review_type'] is None else row['pwd_review_type'], axis=1)
    merged_df['pwd_review_type'] = merged_df.apply(lambda row: 'Green Infrastructure|GREEN ROOF' if row['_merge'] == 'both' and row['pwd_review_type'] == 'Green Infrastructure' else row['pwd_review_type'], axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id'])

    # 7. merge parcels with steep slopes df
    merged_df = merged_df.merge(query_dfs['steep_slopes_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['steep_slope'] = merged_df.apply(lambda row: 1 if row['_merge'] == 'both' else 0, axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id'])

    # 8. merge parcels with rco df
    merged_df = merged_df.merge(query_dfs['zoning_rco_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['zoning_rco'] = merged_df.apply(lambda row: row['rco_name'] if row['_merge'] == 'both' else row['zoning_rco'], axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id','rco_name'])

    # 9. merge parcels with zoning basedistricts
    merged_df = merged_df.merge(query_dfs['zoning_base_districts_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['base_zoning'] = merged_df.apply(lambda row: row['base_zoning_district'] if row['_merge'] == 'both' else None, axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id','base_zoning_district'])

    # 9. merge parcels with zoning overlays df
    merged_df = merged_df.merge(query_dfs['zoning_overlays_df'], how = 'left', left_on = 'pwd_parcel_id', right_on = 'parcel_id',  indicator = True)
    merged_df['overlay_zoning'] = merged_df.apply(lambda row: row['zoning_overlay_district'] if row['_merge'] == 'both' else None, axis=1)
    merged_df = merged_df.drop(columns=['_merge','parcel_id','zoning_overlay_district'])

    # populate pac_flag and pac_review_type "Building ID Signage Review"
    merged_df['pac_flag'], merged_df['pac_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Building ID Signage Review' if pd.isna(row['pac_review_type']) else str(row['pac_review_type']) + '|Building ID Signage Review')
        if
            row['base_zoning'] is not None
            and
            ('ICMX' in row['base_zoning']
            or 'I1' in row['base_zoning']
            or 'IRMX' in row['base_zoning']
            or 'CMX4' in row['base_zoning']
            or 'CMX5' in row['base_zoning']
            or 'SPCIV' in row['base_zoning'])
        else (row['pac_flag'],row['pac_review_type']), axis=1
    )
    )

    # populate pac_flag AND pac_review_type "Parkway Buffer"
    merged_df['pac_flag'], merged_df['pac_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Parkway Buffer' if pd.isna(row['pac_review_type']) else str(row['pac_review_type']) + '|Parkway Buffer')
        if
            row['overlay_zoning'] is not None
            and
            '/CTR Center City Overlay District - Parkway Buffer' in row['overlay_zoning']
        else (row['pac_flag'],row['pac_review_type']), axis=1
    )
    )

    # populate pac_flag and pac_review_type "Public Art"
    merged_df['pac_flag'], merged_df['pac_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Public Art' if pd.isna(row['pac_review_type']) else str(row['pac_review_type']) + '|Public Art')
        if
            row['base_zoning'] is not None
            and
            ('SPENT' in row['base_zoning'])
        else (row['pac_flag'],row['pac_review_type']), axis=1
    )
    )

    # populate pac_flag AND pac_review_type "Special Signage Control"
    merged_df['pac_flag'], merged_df['pac_review_type'] = zip(*merged_df.apply(
        lambda row: (1, 'Special Signage Control' if pd.isna(row['pac_review_type']) else str(row['pac_review_type']) + '|Special Signage Control')
        if (
            row['overlay_zoning'] is not None
            and
            (
                (
                '/CTR Center City Overlay District - Center City Commercial Area' in row['overlay_zoning']
                or '/CTR Center City Overlay District - Convention Center Area' in row['overlay_zoning']
                or '/CTR Center City Overlay District - Independence Hall Area' in row['overlay_zoning']
                or '/CTR Center City Overlay District - Rittenhouse Square' in row['overlay_zoning']
                or '/CTR Center City Overlay District - Vine Street Area' in row['overlay_zoning']
                or '/CTR Center City Overlay District - Washington Square' in row['overlay_zoning']
                # or '/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood' in row['overlay_zoning']
                # or '/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue' in row['overlay_zoning']
                # or '/NCA Neighborhood Commercial Area Overlay District - Main Street/Manayunk and Venice Island' in row['overlay_zoning']
                # or '/NCA Neighborhood Commercial Area Overlay District - Logan Triangle' in row['overlay_zoning']
                # or '/NCA Neighborhood Commercial Area Overlay District - Lower and Central Germantown' in row['overlay_zoning']
                # or '/NCA Neighborhood Commercial Area Overlay District - North Delaware Avenue' in row['overlay_zoning']
                # or '/NCA Neighborhood Commercial Area Overlay District - Spring Garden' in row['overlay_zoning']
                or 'Accessory Sign Controls - Special Controls for Cobbs Creek, Roosevelt Boulevard, and Department of Parks and Recreation Land' in row['overlay_zoning']
                or '/CTR Center City Overlay District - Society Hill Area' in row['overlay_zoning']
                or '/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue - Mount Airy and Germantown North Subarea' in row['overlay_zoning']
                )
            or
                (
                row['base_zoning'] is not None
                    and
                    '/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood' in row['overlay_zoning']
                     and
                     (
                         'CMX2' in row['base_zoning']
                         or 'CMX2.5' in row['base_zoning']
                         or 'CMX3' in row['base_zoning']
                     )
                )
            )
        )
        else (row['pac_flag'],row['pac_review_type']), axis=1
    )
    )

    # populate pcpc_flag AND pcpc_review_type "Center City Facade Review"
    merged_df['pcpc_flag'], merged_df['pcpc_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Center City Facade Review' if pd.isna(row['pcpc_review_type']) else str(row['pcpc_review_type']) + '|Center City Facade Review')
        if (
            row['overlay_zoning'] is not None
            and
            ('/CTR Center City Overlay District - Broad Street Area South' in row['overlay_zoning']
             or '/CTR Center City Overlay District - Chestnut and Walnut Street Area' in row['overlay_zoning']
             or '/CTR Center City Overlay District - Market Street Area East' in row['overlay_zoning']
             or '/CTR Center City Overlay District - Society Hill Area - Northeast' in row['overlay_zoning']
             or '/CTR Center City Overlay District - West Chestnut Street Area' in row['overlay_zoning'])
            )
        else (row['pcpc_flag'],row['pcpc_review_type']), axis=1
    )
    )

    # populate pcpc_flag AND pcpc_review_type "City Ave Site Review"
    merged_df['pcpc_flag'], merged_df['pcpc_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'City Ave Site Review' if pd.isna(row['pcpc_review_type']) else str(row['pcpc_review_type']) + '|City Ave Site Review')
        if (
            row['overlay_zoning'] is not None
            and
            ('/CAO City Avenue Overlay District - City Avenue Regional Center Area' in row['overlay_zoning']
             or '/CAO City Avenue Overlay District - City Avenue Village Center Area' in row['overlay_zoning'])
        )
        else (row['pcpc_flag'],row['pcpc_review_type']), axis=1
    )
    )

    # populate pcpc_flag AND pcpc_review_type "East Falls Subarea Facade Review"
    merged_df['pcpc_flag'], merged_df['pcpc_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'East Falls Subarea Facade Review' if pd.isna(row['pcpc_review_type']) else str(row['pcpc_review_type']) + '|East Falls Subarea Facade Review')
        if row['overlay_zoning'] is not None
            and '/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood' in row['overlay_zoning']
             and (row['base_zoning'] is not None
                  and
                     (
                         'CMX2' in row['base_zoning']
                         or 'CMX2.5' in row['base_zoning']
                         or 'CMX3' in row['base_zoning']
                     )
            )
        else (row['pcpc_flag'],row['pcpc_review_type']), axis=1
    )
    )

    # populate pcpc_flag AND pcpc_review_type "Germantown Avenue - Mount Airy and Germantown North Subarea"
    merged_df['pcpc_flag'], merged_df['pcpc_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Germantown Avenue - Mount Airy and Germantown North Subarea' if pd.isna(row['pcpc_review_type']) else str(row['pcpc_review_type']) + '|Germantown Avenue - Mount Airy and Germantown North Subarea')
        if row['overlay_zoning'] is not None
            and
            '/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue - Mount Airy and Germantown North Subarea' in row['overlay_zoning']
        else (row['pcpc_flag'],row['pcpc_review_type']), axis=1
    )
    )

    # populate pcpc_flag AND pcpc_review_type "Master Plan Review"
    merged_df['pcpc_flag'], merged_df['pcpc_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Master Plan Review' if pd.isna(row['pcpc_review_type']) else str(row['pcpc_review_type']) + '|Master Plan Review')
        if row['base_zoning'] is not None
            and
            (
                'RMX1' in row['base_zoning']
                 or 'RMX2' in row['base_zoning']
                 or 'SPENT' in row['base_zoning']
                 or 'SPINS' in row['base_zoning']
                 or 'SPSTA' in row['base_zoning']
            )
        else (row['pcpc_flag'],row['pcpc_review_type']), axis=1
    )
    )

    # populate pcpc_flag AND pcpc_review_type "Neighborhood Conservation Review"
    merged_df['pcpc_flag'], merged_df['pcpc_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Neighborhood Conservation Review' if pd.isna(row['pcpc_review_type']) else str(row['pcpc_review_type']) + '|Neighborhood Conservation Review')
        if row['overlay_zoning'] is not None
            and
            (
                '/NCO Neighborhood Conservation Overlay District - Strawberry Mansion' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Chestnut Hill Lower East' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Wissahickon with /RAN Exception' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Central Roxborough with /RAN Exception' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Overbrook Farms' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Queen Village' in row['overlay_zoning']
                or '/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough' in row['overlay_zoning']
            )
        else (row['pcpc_flag'],row['pcpc_review_type']), axis=1
    )
    )

    # populate pcpc_flag AND pcpc_review_type "Ridge Ave Façade Review"
    merged_df['pcpc_flag'], merged_df['pcpc_review_type'] = zip(*merged_df.apply(
        lambda row: (1,  'Ridge Ave Façade Review' if pd.isna(row['pcpc_review_type']) else str(row['pcpc_review_type']) + '|Ridge Ave Façade Review')
        if row['overlay_zoning'] is not None
            and
            '/RAN Ridge Avenue Neighborhoods Overlay District' in row['overlay_zoning']
        else (row['pcpc_flag'],row['pcpc_review_type']), axis=1
    )
    )

    # fill in all null cells with zeros for flag fields that have nulls
    print('Correcting df field types before truncate and append are performed.')
    merged_df['pac_flag'] = merged_df['pac_flag'].fillna(0)
    merged_df['pcpc_flag'] = merged_df['pcpc_flag'].fillna(0)

    # cast all flag fields to the correct data type to prep for sql append
    for col in merged_df.columns:
        if col.endswith('flag') or col in ('corner_property','floodplain','steep_slope'):
            # print(col)
            merged_df[col] = merged_df[col].astype('Int16')

    # cast the remaining incorrect field types to the appropriate type for sql append
    merged_df['objectid'] = merged_df['objectid'].astype('Int32')
    merged_df['phcadjacent_flag'] = merged_df['phcadjacent_flag'].astype('Int32')
    merged_df['parcel_area'] = merged_df['parcel_area'].astype('object')

    # drop any duplicates
    # Drop duplicates based on relevant columns or across all columns if truly identical
    merged_df = merged_df.drop_duplicates(subset=['objectid', 'pwd_parcel_id', 'address', 'parcel_area', 'pac_flag',
                                                    'pac_review_type', 'pcpc_flag', 'pcpc_review_type', 'phc_flag',
                                                    'phc_review_type', 'pwd_flag', 'pwd_review_type', 'corner_property',
                                                    'base_zoning', 'overlay_zoning', 'li_inspection_district',
                                                    'floodplain', 'steep_slope', 'zoning_rco', 'phcadjacent_flag',
                                                    'phcadjacent_review_type'], keep='first')

    # reconnect to DB and perform truncate/append
    engine = DataBridge_SQLALCHEMY.engine

    conn = engine.connect()

    databridge_len = pd.read_sql("select count(*) from li.li_pr_flag_summary", conn)

    db_count = databridge_len['count'].values[0]

    new_count = len(merged_df)

    # # truncate the table
    # print('Truncating DB table.')
    # conn.execute(text("truncate table li.li_pr_flag_summary"))
    #
    # #append the dataframe
    # print('Appending dataframe to DB table.')
    # merged_df.to_sql('li_pr_flag_summary', con=engine, if_exists='append', index=False)

    # conn.commit()
    # if there is greater than 5% difference in the number of records between the two datasets, do not truncate/append
    if 0.95 <= new_count / db_count <= 1.05:
        #truncate the table
        print('Truncating DB table.')
        conn.execute(text("truncate table li.li_pr_flag_summary"))
        # conn.commit()

        #append the dataframe
        print('Appending dataframe to DB table.')
        merged_df.to_sql('li_pr_flag_summary', con=engine, if_exists='append', index=False)
        conn.close()
    else:
        print('There is more than a 5 percent difference in the number of records in plan review flags. Did not truncate and append.')
        li_utils.send_email(subject = 'Too many changes in Plan Review Flags', body = 'The change threshold of 5 percent was exceeded. Did not truncate and append.', priority = 1)

except:
    print('THIS EXCEPTION')
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    email_body = "Plan Review Flags Failed.\n" + pymsg
    li_utils.send_email(subject='Plan Review Flags Failed', body=email_body)
    print('-------------------------------------------------------------------')