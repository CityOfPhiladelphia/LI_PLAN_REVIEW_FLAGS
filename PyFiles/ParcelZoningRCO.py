"""
Plan Review Flags - Part 4 of 5

This script populates the Zoning RCO value for every property value.
This process must be run immediately after Parts 1-3 as it relies on the same local source data to remain in sync
"""
import datetime
import logging
import sys
import traceback
from datetime import timedelta

import arcpy
from sde_connections import DataBridge

# Step 1: Configure log file
try:
    print('Step 1: Configuring log file...')
    log_file_path = 'E:\LI_PLAN_REVIEW_FLAGS\Logs\PermitReviewFlags.log'
    log = logging.getLogger('PR Flags Part 4 - Zoning RCOs')
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
    log.info('PR Flags Part 4 Begun')
    today = datetime.datetime.today()
    oneWeekAgo = today - timedelta(days=7)

    Zoning_RCOs = DataBridge.sde_path+'\\GIS_PLANNING.Zoning_RCO'

    PWD_PARCELS_DataBridge = DataBridge.sde_path+'\\GIS_WATER.PWD_PARCELS'

    Council_Districts_2016 = DataBridge.sde_path+'\\GIS_PLANNING.Council_Districts_2016'

    zoningFC = 'ZoningRCO_'
    zoningLayer = 'ZoningLayer'
    zoningCurrent = 'ZoningCurrent'

    PR_FLAG_Temp = 'Flags_Table_Temp'
    PWD_Parcels_Working = 'PWDParcels_Working'
    Council_Districts_Local = 'Districts_'
    PPR_Assets = DataBridge.sde_path + '\\GIS_PPR.PPR_Assets'
    PPR_Assets_Temp_Pre_Dissolve = 'in_memory\\PPR_Assets_Temp_Pre_Dissolve'
    PPR_Assets_Temp = 'in_memory\\PPR_Assets_Temp'
    Park_IDs_Local = 'ParkNameIDs_' 

    localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
    inMemory = 'in_memory'

    arcpy.env.workspace = localWorkspace
    arcpy.env.overwriteOutput = True
    locallySaved = arcpy.ListFeatureClasses()

    ############################
    #Copy RCO Layer Local
    if arcpy.Exists(zoningFC):
        arcpy.Delete_management(zoningFC)
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_RCOs, localWorkspace, zoningFC)

    #Append all ROC Names to a list.  Each RCO will be iterated through and added to the dictionary
    print(zoningFC)
    print([f.name for f in arcpy.ListFields(zoningFC)])

    rcoOIDCursor = arcpy.da.SearchCursor(zoningFC, 'ORGANIZATION_NAME')
    rcoIDS = list(set([row[0] for row in rcoOIDCursor]))
    del rcoOIDCursor

    #Create lookup dictionary for RCO Objectid names:
    from li_dbs_Lazy import DataBridge
    lookupSQL = "select LNI_ID, ORGANIZATION_NAME from GIS_PLANNING.ZONING_RCO"
    lookupCursor = DataBridge.DataBridge.cursor()
    lookupCursor.execute(lookupSQL)
    lookupDict = {row[1]:row[0] for row in lookupCursor.fetchall()}
    lookupCursor.close()
    del lookupCursor

    #Create a layer based off of each overlay type saved from previous list
    overlayTotal = len(rcoIDS)
    overlayCount = 0
    arcpy.MakeFeatureLayer_management(zoningFC, zoningLayer)
    parcelDict = {}
    for overlayType in rcoIDS:
        arcpy.env.workspace = localWorkspace
        overlayCount += 1
        print('Starting ' + str(overlayType) + ', ' + str(overlayCount)+ ' of ' + str(overlayTotal))
        arcpy.SelectLayerByAttribute_management(zoningLayer, 'NEW_SELECTION', "ORGANIZATION_NAME = '" + str(overlayType if "'" not in overlayType else overlayType.replace("'", "|| CHR(39) ||")) + "'")
        arcpy.MakeFeatureLayer_management(zoningLayer, zoningCurrent)
        IntersectOutput = localWorkspace + '\\' + 'Int_' + zoningFC
        arcpy.Intersect_analysis([PWD_Parcels_Working] + [zoningCurrent], IntersectOutput, 'ALL')
        '''
        # To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
        arcpy.AddField_management(IntersectOutput, 'Thinness', 'FLOAT')
        print('Calculating Area')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
        print('Calculating Permimeter')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
        print('Calculating Thiness')
        arcpy.CalculateField_management(IntersectOutput, 'Thinness',
                                        "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')
        fieldList = ['PARCELID', 'GROSS_AREA', 'POLY_AREA',
                     'Thinness', 'CODE']
        '''
        fieldList = ['PARCELID', 'GROSS_AREA', 'ORGANIZATION_NAME']
        IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fieldList)
        countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
        count = 0
        print('Found ' + str(countin) + ' records in intersect table')
        breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
        for row in IntersectCursor:
            count += 1
            if count in breaks:
                print('Parsing RCO FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
            # if (row[2] / float(row[1])) > 0.01:  #To implment 3% coverage and thinness minimum: row[3] > 0.3 and (row[2] / float(row[1])) > 0.03:
            if row[fieldList.index('PARCELID')] in parcelDict:
                tempList = parcelDict.get(row[0])
                parcelDict[row[fieldList.index('PARCELID')]] = list(set([lookupDict[row[fieldList.index('ORGANIZATION_NAME')]]] + tempList))
            else:
                parcelDict[row[fieldList.index('PARCELID')]] = [lookupDict[row[fieldList.index('ORGANIZATION_NAME')]]]
        arcpy.Delete_management(IntersectOutput)
        arcpy.Delete_management(zoningCurrent)
        arcpy.SelectLayerByAttribute_management(zoningLayer, 'CLEAR_SELECTION')
    del rcoIDS
    zoneCursor = arcpy.da.UpdateCursor(PR_FLAG_Temp, ['PWD_PARCEL_ID', 'ZONING_RCO'])
    print('Starting Cursor')
    for parcel in zoneCursor:
        if parcel[0] in parcelDict:
            parcel[1] = '|'.join([str(oid) for oid in parcelDict.get(parcel[0])])
            zoneCursor.updateRow(parcel)
    del zoneCursor
    log.info('PR Flags Part 4 Complete')

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    log.error(pymsg)
    print(pymsg)

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
    sys.exit(1)
