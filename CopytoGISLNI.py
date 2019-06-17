import arcpy
import logging
import sys
import traceback

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
    arcpy.TruncateTable_management('Database Connections\\GISLNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY')
    log.info('Appending to GISLNI')
    arcpy.Append_management('E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb\\Flags_Table_Temp', 'Database Connections\\GISLNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY', 'NO_TEST')
    log.info('GISLNI Table Updated')

    log.info('Truncating DataBridge')
    arcpy.TruncateTable_management('Database Connections\\DataBridge_GIS_LNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY')
    log.info('Appending to DataBridge')
    arcpy.Append_management('E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb\\Flags_Table_Temp', 'Database Connections\\DataBridge_GIS_LNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY', 'NO_TEST')
    log.info('DataBridge Table Updated')
except:
    msgs = arcpy.GetMessages(2)
    print(msgs)
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    log.error(pymsg)
