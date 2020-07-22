"""
Plan Review Flags - Part 5 of 5

This script populates the Zoning RCO value for every property value.
This process must be run immediately after Parts 1-4 as pushes the now up to date data back to DataBridge and GISLNI
"""
import logging
import sys
import traceback

import arcpy
from sde_connections import DataBridge_GIS_LNI, GISLNI

# Step 1: Configure log file
try:
    print('Step 1: Configuring log file...')
    log_file_path = 'E:\LI_PLAN_REVIEW_FLAGS\Logs\PermitReviewFlags.log'
    log = logging.getLogger('PR Flags Part 5 - Copying to Enterprise')
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
    log.info('Truncating GISLNI')
    arcpy.TruncateTable_management(GISLNI.sde_path+'\\GIS_LNI.LI_PR_FLAG_SUMMARY')
    log.info('Appending to GISLNI')
    arcpy.Append_management('E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb\\Flags_Table_Temp', GISLNI.sde_path+'\\GIS_LNI.LI_PR_FLAG_SUMMARY', 'NO_TEST')
    log.info('GISLNI Table Updated')

    log.info('Truncating DataBridge')
    arcpy.TruncateTable_management(DataBridge_GIS_LNI.sde_path+'\\GIS_LNI.LI_PR_FLAG_SUMMARY')
    log.info('Appending to DataBridge')
    arcpy.Append_management('E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb\\Flags_Table_Temp', DataBridge_GIS_LNI.sde_path+'\\GIS_LNI.LI_PR_FLAG_SUMMARY', 'NO_TEST')
    log.info('DataBridge Table Updated')
except:
    msgs = arcpy.GetMessages(2)
    print(msgs)
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])

    import smtplib
    from email.mime.text import MIMEText
    from phila_mail import server
    sender = 'LIGISTeam@phila.gov'
    recipientslist = ['DANI.INTERRANTE@PHILA.GOV', 'SHANNON.HOLM@PHILA.GOV', 'Philip.Ribbens@Phila.gov', 'LIGISTeam@phila.gov', 'Jessica.bradley@phila.gov']
    commaspace = ', '
    msg = MIMEText('AUTOMATIC EMAIL \n Plan Review Flags Update Failed during update: \n' + pymsg)
    msg['To'] = commaspace.join(recipientslist)
    msg['From'] = sender
    msg['X-Priority'] = '2'
    msg['Subject'] = 'Plan Review Flags Table Update Failure'
    server.server.sendmail(sender, recipientslist, msg.as_string())
    server.server.quit()
    log.error(pymsg)
