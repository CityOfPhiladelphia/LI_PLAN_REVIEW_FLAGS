"""
Plan Review Flags - Part 3 of 5

This script populates the Zoning Overlay District value for every property value.
This process must be run immediately after Parts 1 and 2 as it relies on the same local source data to remain in sync
"""
import datetime
import logging
import sys
import traceback
from datetime import timedelta

import arcpy
from sde_connections import DataBridge
from sde_connections import GISLNI

# Step 1: Configure log file
try:
    print('Step 1: Configuring log file...')
    log_file_path = 'E:\LI_PLAN_REVIEW_FLAGS\Logs\PermitReviewFlags.log'
    log = logging.getLogger('PR Flags Part 3 - Zoning Overlays')
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
    log.info('PR Flags Part 3 Begun')
    today = datetime.datetime.today()
    oneWeekAgo = today - timedelta(days=7)

    Zoning_Overlays = DataBridge.sde_path+'\\GIS_PLANNING.Zoning_Overlays'
    GIS_LNI_PR_PCPC_DORMismatchReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_DORMismatchReview'
    PPR_Assets = DataBridge.sde_path + '\\GIS_PPR.PPR_Assets'
    PWD_PARCELS_DataBridge = DataBridge.sde_path+'\\GIS_WATER.PWD_PARCELS'

    Council_Districts_2016 = DataBridge.sde_path+'\\GIS_PLANNING.Council_Districts_2016'
    Council_Districts_Local = 'Districts_'

    zoningFC = 'ZoningOverlays_'
    zoningLayer = 'ZoningLayer'
    zoningCurrent = 'ZoningCurrent'

    PR_FLAG_Temp = 'Flags_Table_Temp'
    PPR_Assets_Temp_Pre_Dissolve = 'in_memory\\PPR_Assets_Temp_Pre_Dissolve'
    PPR_Assets_Temp = 'in_memory\\PPR_Assets_Temp'
    Park_IDs_Local = 'ParkNameIDs_'
    PWD_Parcels_Working = 'PWDParcels_Working'

    localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
    inMemory = 'in_memory'

    arcpy.env.workspace = localWorkspace
    arcpy.env.overwriteOutput = True

    #Append DOR Mismatch Review Layer to Overlays.  This is a temporary function until the DOR/Zoning data issue is cleaned up
    arcpy.Append_management(GIS_LNI_PR_PCPC_DORMismatchReview, zoningFC, 'NO_TEST')

    #Append first word from all overlay types to list.  Script will iterate through these values below to match to appropriate parcel.  This is being done to ease use of memory
    print(zoningFC)
    print([f.name for f in arcpy.ListFields(zoningFC)])
    specOverlayCursor = arcpy.da.SearchCursor(zoningFC, 'OVERLAY_NAME')
    overlayTypes = []
    for row in specOverlayCursor:
        if row[0].split(' ')[0] not in overlayTypes:
            overlayTypes.append(row[0].split(' ')[0])
    del specOverlayCursor

    #Create a layer based off of each overlay type saved from previous list
    overlayTotal = len(overlayTypes)
    overlayCount = 0
    arcpy.MakeFeatureLayer_management(zoningFC, zoningLayer)
    parcelDict = {}
    for overlayType in overlayTypes:
        overlayCount += 1
        print('Starting '+ overlayType +' overlay ' + str(overlayCount)+ ' of ' + str(overlayTotal))
        arcpy.SelectLayerByAttribute_management(zoningLayer, 'NEW_SELECTION', "OVERLAY_NAME LIKE '" + overlayType + "%'")
        arcpy.MakeFeatureLayer_management(zoningLayer, zoningCurrent)


        currentTract = 'CurrentDistrict'
        tempParcels = 'TempParcels'
        tempZone = 'TempZone'
        districtCount = 0
        districtTotal = int(arcpy.GetCount_management(Council_Districts_Local).getOutput(0))
        arcpy.CalculateField_management(Council_Districts_Local, 'DISTRICT', '!DISTRICT!.strip(' ')', 'PYTHON_9.3')
        districtTileCursor = arcpy.da.SearchCursor(Council_Districts_Local, 'DISTRICT')

        for tract in districtTileCursor:
            print('Processing District ' + tract[0] + "\n" + str(
                (float(districtCount) / float(districtTotal)) * 100.0) + '% Complete')
            districtCount += 1
            arcpy.MakeFeatureLayer_management(localWorkspace + '\\' + Council_Districts_Local, currentTract, "DISTRICT = '" + tract[0] + "'")
            if arcpy.Exists(tempZone):
                arcpy.Delete_management(tempZone)
            arcpy.Clip_analysis(zoningCurrent, currentTract, tempZone)
            if int(arcpy.GetCount_management(tempZone).getOutput(0)) >= 1:
                print('Extracting Overlay')
                if arcpy.Exists(tempParcels):
                    arcpy.Delete_management(tempParcels)
                arcpy.Clip_analysis(localWorkspace + '\\' + PWD_Parcels_Working, currentTract, tempParcels)
                IntersectOutput = localWorkspace + '\\' + zoningFC + '_Int'
                print('Running Intersect')
                arcpy.Intersect_analysis([tempParcels] + [tempZone], IntersectOutput, 'ALL')

                # To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
                arcpy.AddField_management(IntersectOutput, 'Thinness', 'FLOAT')
                # NOTE Thiness calculation was removed by request, this is designed remove small overlaps in zoning from adjacent parcels
                arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
                """
                arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
                arcpy.CalculateField_management(IntersectOutput, 'ThinessRatio',
                                                "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')
    
                """
                fieldList = ['PARCELID', 'GROSS_AREA', 'POLY_AREA', 'Thinness', 'OVERLAY_NAME', 'ADDRESS']
                IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fieldList)
                countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
                count = 0
                print('Found ' + str(countin) + ' records in intersect table')
                breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
                for row in IntersectCursor:
                    count += 1
                    if count in breaks:
                        print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
                    # null values in the poly_area field will break the script and they don't belong in the parcelDict anyway
                    if row[fieldList.index('POLY_AREA')] is None:
                        print('ParcelID ' + str(row[fieldList.index('PARCELID')]) + ' has a null POLY_AREA value.')
                        log.info('ParcelID ' + str(row[fieldList.index('PARCELID')]) + ' has a null POLY_AREA value.')
                        continue
                    elif (float(row[fieldList.index('POLY_AREA')]) / float(row[fieldList.index('GROSS_AREA')])) > 0.01:  #To implment 3% coverage and thinness minimum: row[3] > 0.3 and (row[2] / float(row[1])) > 0.03:
                        if row[fieldList.index('PARCELID')] in parcelDict and row[fieldList.index('PARCELID')] is not None:
                            print('should not be here 2')
                            tempList = parcelDict[row[fieldList.index('PARCELID')]]
                            parcelDict[row[fieldList.index('PARCELID')]] = list(set([row[fieldList.index('OVERLAY_NAME')]] + tempList))
                        else:
                            print('Should not be here 1.5')
                            parcelDict[row[fieldList.index('PARCELID')]] = [row[fieldList.index('OVERLAY_NAME')]]
                arcpy.Delete_management(IntersectOutput)
                arcpy.Delete_management(currentTract)
                arcpy.Delete_management(tempZone)
                arcpy.Delete_management(tempParcels)
            else:
                print('No overlay in District')
        del districtTileCursor
        arcpy.Delete_management(zoningCurrent)
        arcpy.SelectLayerByAttribute_management(zoningLayer, 'CLEAR_SELECTION')
    del overlayTypes
    zoneCursor = arcpy.da.UpdateCursor(PR_FLAG_Temp, ['PWD_PARCEL_ID', 'OVERLAY_ZONING'])
    print('Starting Cursor')
    for parcel in zoneCursor:
        if parcel[0] in parcelDict:
            print(parcel[0])
            parcel[1] = '|'.join(parcelDict.get(parcel[0]))
            zoneCursor.updateRow(parcel)
    del zoneCursor
    log.info('PR Flags Part 3 Complete')
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    log.info(pymsg)
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