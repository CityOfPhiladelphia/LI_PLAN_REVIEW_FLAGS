"""
Plan Review Flags - Part 2 of 5

This script populates the Zoning Base District value for every property value.
This process must be run immediately after Part 1 as it relies on the same local source data to remain in sync
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
    log = logging.getLogger('PR Flags Part 2 - Base Zoning')
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
    log.info('PR Flags Part 2 Begun')
    today = datetime.datetime.today()
    oneWeekAgo = today - timedelta(days=7)

    PPR_Assets = DataBridge.sde_path + '\\GIS_PPR.PPR_Assets'
    Zoning_BaseDistricts = DataBridge.sde_path+'\\GIS_PLANNING.Zoning_BaseDistricts'
    Zoning_Overlays= DataBridge.sde_path+'\\GIS_PLANNING.Zoning_Overlays'

    PWD_PARCELS_DataBridge = DataBridge.sde_path+'\\GIS_WATER.PWD_PARCELS'

    Council_Districts_2016 = DataBridge.sde_path+'\\GIS_PLANNING.Council_Districts_2016'

    zoningFC = 'ZonBaseDistricts_'

    PR_FLAG_Temp = 'Flags_Table_Temp'
    PPR_Assets_Temp_Pre_Dissolve = 'in_memory\\PPR_Assets_Temp_Pre_Dissolve'
    PPR_Assets_Temp = 'in_memory\\PPR_Assets_Temp'
    Park_IDs_Local = 'ParkNameIDs_' 
    PWD_Parcels_Working = 'PWDParcels_Working'
    Council_Districts_Local = 'Districts_'

    localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'

    inMemory = 'in_memory'

    arcpy.env.workspace = localWorkspace
    arcpy.env.overwriteOutput = True


    #Iterate through Council District Polygons
    currentTract = 'CurrentDistrict'
    tempParcels = 'TempParcels'
    tempZone = 'TempZone'
    districtCount = 0
    districtTotal = int(arcpy.GetCount_management(Council_Districts_Local).getOutput(0))
    arcpy.CalculateField_management(Council_Districts_Local, 'DISTRICT', '!DISTRICT!.strip(' ')', 'PYTHON_9.3')
    districtTileCursor = arcpy.da.SearchCursor(Council_Districts_Local, 'DISTRICT')
    parcelDict = {}
    for tract in districtTileCursor:
        memory = inMemory
        districtCount += 1
        print('Processing District ' + tract[0] + "\n" + str((float(districtCount) / float(districtTotal)) * 100.0) + '% Complete')
        arcpy.MakeFeatureLayer_management(localWorkspace + '\\' + Council_Districts_Local, currentTract, "DISTRICT = '" + tract[0] + "'")
        if arcpy.Exists(tempZone):
            arcpy.Delete_management(tempZone)
        arcpy.Clip_analysis(localWorkspace + '\\' + zoningFC, currentTract, tempZone)
        if arcpy.Exists(tempParcels):
            arcpy.Delete_management(tempParcels)
        arcpy.Clip_analysis(localWorkspace + '\\' + PWD_Parcels_Working, currentTract, tempParcels)
        IntersectOutput = localWorkspace + '\\' + zoningFC + '_Int'
        print('Running Intersect')
        arcpy.Intersect_analysis([tempParcels] + [tempZone], IntersectOutput, 'ALL')

        # To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
        arcpy.AddField_management(IntersectOutput, 'Thinness', 'FLOAT')
        print('Calculating Area')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
        """ #NOTE Thiness calculation was removed by request
        print('Calculating Permimeter')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
        print('Calculating Thiness')
        arcpy.CalculateField_management(IntersectOutput, 'Thinness',
                                        "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')
        """


        inFL = ['PARCELID', 'GROSS_AREA', 'POLY_AREA',
                     'Thinness', 'CODE', 'ADDRESS']
        IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, inFL)
        countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
        count = 0
        print('Found ' + str(countin) + ' records in intersect table')
        breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
        for row in IntersectCursor:
            try:
                count += 1
                if count in breaks:
                    print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
                if (row[2] / float(row[1])) > 0.01:  #To implment 3% coverage and thinness minimum: and row[3] > 0.3 and (row[2] / float(row[1])) > 0.03:
                    if row[inFL.index('PARCELID')] in parcelDict:
                        tempList = parcelDict.get(row[inFL.index('PARCELID')])
                        tempCode = tempList[0]
                        newTempList = [list(set([row[inFL.index('CODE')]] + tempCode)),row[inFL.index('ADDRESS')] ]
                        parcelDict[row[inFL.index('PARCELID')]] = newTempList
                    else:
                        parcelDict[row[inFL.index('PARCELID')]] = [[row[inFL.index('CODE')]], row[inFL.index('ADDRESS')]]
            except:
                continue
        arcpy.Delete_management(IntersectOutput)
        arcpy.Delete_management(currentTract)
        arcpy.Delete_management(tempZone)
        arcpy.Delete_management(tempParcels)
    del districtTileCursor

    # Add base zoning for existing parking
    countin = int(arcpy.GetCount_management(PR_FLAG_Temp).getOutput(0))
    count = 0
    print('Found ' + str(countin) + ' records in local flags table')
    breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
    zoneCursor1 = arcpy.da.UpdateCursor(PR_FLAG_Temp, ['PWD_PARCEL_ID', 'BASE_ZONING'])
    for parcel in zoneCursor1:
        count += 1
        if count in breaks:
            print('Adding Zoning to Exisiting FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
        if parcel[0] in parcelDict:
            parcel[1] = '|'.join(parcelDict[parcel[0]][0])
            del parcelDict[parcel[0]]
            zoneCursor1.updateRow(parcel)
    del zoneCursor1

    # Add remaining parcels to table
    print('Copying new parcels to table')
    countin = int(len(parcelDict))
    count = 0
    breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
    remainingParcels = 'Parcels_Without_Flags'
    if arcpy.Exists(remainingParcels):
        arcpy.Delete_management(remainingParcels)
    arcpy.CreateTable_management(localWorkspace, remainingParcels, PR_FLAG_Temp)
    flagFields = ['PAC_FLAG', 'PCPC_FLAG', 'PHC_FLAG', 'PWD_FLAG', 'CORNER_PROPERTY', 'FLOODPLAIN', 'STEEP_SLOPE']
    zoneCursor2 = arcpy.da.InsertCursor(remainingParcels, ['PWD_PARCEL_ID', 'BASE_ZONING', 'ADDRESS'] + flagFields)
    for k,v in parcelDict.items():
        count += 1
        if count in breaks:
            print('Adding Addresses to table ' + str(int(round(count * 100.0 / countin))) + '% complete...')
        zoneCursor2.insertRow([str(k), '|'.join(v[0]), v[-1]] + [0] * len(flagFields))
    arcpy.Append_management(remainingParcels, PR_FLAG_Temp, 'NO_TEST')
    arcpy.Delete_management(remainingParcels)
    log.info('PR Flags Part 2 Complete')
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
