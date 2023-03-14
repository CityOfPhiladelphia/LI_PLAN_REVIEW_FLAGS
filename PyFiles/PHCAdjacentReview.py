"""
Plan Review Flags - Part 5 of 5

This script populates the PHC Adjacent Review value for every property value.
This process must be run immediately after all other parts because it updates the final table directly
"""
import datetime
import logging
import sys
import traceback
from datetime import timedelta

import arcpy
from sde_connections import GISLNI, DataBridge_GIS_LNI, DataBridge

# Step 1: Configure log file
try:
    print('Step 1: Configuring log file...')
    log_file_path = 'E:\LI_PLAN_REVIEW_FLAGS\Logs\PermitReviewFlags.log'
    log = logging.getLogger('PR Flags Part 5 - PHC Adjacent Review')
    log.setLevel(logging.INFO)
    hdlr = logging.FileHandler(log_file_path)
    hdlr.setLevel(logging.INFO)
    hdlrFormatter = logging.Formatter('%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%m/%d/%Y  %I:%M:%S %p')
    hdlr.setFormatter(hdlrFormatter)
    log.addHandler(hdlr)
    print('SUCCESS at Step 1')
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    arcpy.AddError(pymsg)
    sys.exit(1)

try:
    log.info('PR Flags Part 5 Begun')
    today = datetime.datetime.today()
    oneWeekAgo = today - timedelta(days=7)

    localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
    inMemory = 'in_memory'

    arcpy.env.workspace = localWorkspace
    arcpy.env.overwriteOutput = True

    GIS_LNI_PR_PHC_HistoricalResReview = GISLNI.sde_path + '\\GIS_LNI.PR_PHC'
    PWD_Parcels = DataBridge.sde_path + '\\GIS_WATER.PWD_PARCELS'
    Parcels_Near_PHC_Sites = 'Parcels_Near_PHC_Sites'
    PR_FLAG_SUMMARY_GISLNI = GISLNI.sde_path + '\\GIS_LNI.LI_PR_FLAG_SUMMARY'
    PR_FLAG_SUMMARY_DataBridge_GISLNI = DataBridge_GIS_LNI.sde_path + '\\GIS_LNI.LI_PR_FLAG_SUMMARY'

    print('Starting the spatial join process.')
    log.info('Starting the spatial join process.')
    arcpy.analysis.SpatialJoin(PWD_Parcels, GIS_LNI_PR_PHC_HistoricalResReview, Parcels_Near_PHC_Sites, "JOIN_ONE_TO_ONE", "KEEP_COMMON", match_option="WITHIN_A_DISTANCE", search_radius="5 Feet")
    print('Successfully joined parcels to PHC sites.')
    log.info('Successfully joined parcels to PHC sites.')

    # create a list for obvious PHC Adjacent Flags and potential PHC Adjacent Flags
    Might_Need_A_Flag_List = []
    Definitely_Needs_A_Flag_List = []
    with arcpy.da.SearchCursor(Parcels_Near_PHC_Sites, ['PARCELID', 'Join_Count']) as cursor:
        for row in cursor:
            if row[1] == 1:
                Might_Need_A_Flag_List.append(row[0])
            else:
                Definitely_Needs_A_Flag_List.append(row[0])
    del cursor

    print('Starting the flag assignment process.')
    log.info('Starting the flag assignment process.')
    with arcpy.da.UpdateCursor(PR_FLAG_SUMMARY_GISLNI, ['PWD_PARCEL_ID','PHCADJACENT_FLAG','PHCADJACENT_REVIEW_TYPE','PHC_FLAG']) as flagsUpdateCursor:
        for row in flagsUpdateCursor:
            if row[0] in Definitely_Needs_A_Flag_List:
                row[1] = 1
                row[2] = 'PHC Adjacent'
            else:
                if row[0] in Might_Need_A_Flag_List and row[3] == 1:
                    row[1] = 0
                    row[2] = None
                elif row[0] in Might_Need_A_Flag_List and row[3] == 0:
                    row[1] = 1
                    row[2] = 'PHC Adjacent'
                else:
                    row[1] = 0
                    row[2] = None
            flagsUpdateCursor.updateRow(row)
    del flagsUpdateCursor
    print('Finished the flag assignment process.')
    log.info('Finished the flag assignment process.')

    # truncate the databridge table and append the gislni table values to it
    log.info('Truncating DataBridge')
    arcpy.TruncateTable_management(PR_FLAG_SUMMARY_DataBridge_GISLNI)
    log.info('Appending to DataBridge')
    arcpy.Append_management(PR_FLAG_SUMMARY_GISLNI, PR_FLAG_SUMMARY_DataBridge_GISLNI, 'NO_TEST')
    log.info('DataBridge Table Updated')
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    print(pymsg)
    log.error(pymsg)

    import smtplib
    from email.mime.text import MIMEText
    from phila_mail import server
    sender = 'LIGISTeam@phila.gov'
    recipientslist = ['DANI.INTERRANTE@PHILA.GOV', 'daniel.whaland@phila.gov', 'bailey.glover@phila.gov', 'LIGISTeam@phila.gov']
    commaspace = ', '
    msg = MIMEText('AUTOMATIC EMAIL \n Plan Review Flags Update Failed during update: \n' + pymsg)
    msg['To'] = commaspace.join(recipientslist)
    msg['From'] = sender
    msg['X-Priority'] = '2'
    msg['Subject'] = 'Plan Review Flags Table Update Failure'
    server.server.sendmail(sender, recipientslist, msg.as_string())
    server.server.quit()
    sys.exit(1)
