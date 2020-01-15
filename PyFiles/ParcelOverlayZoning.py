import datetime
import logging
import sys
import traceback
from datetime import timedelta

import arcpy
from Update_Local_GDB.Update_Feature_Class import Update
from sde_connections import DataBridge

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
    PPR_Assets = DataBridge.sde_path + '\\GIS_PPR.PPR_Assets'
    PWD_PARCELS_DataBridge = DataBridge.sde_path+'\\GIS_WATER.PWD_PARCELS'

    Council_Districts_2016 = DataBridge.sde_path+'\\GIS_PLANNING.Council_Districts_2016'
    Council_Districts_Local = 'Districts'

    zoningFC = 'ZoningOverlays_'+ today.strftime("%d%b%Y")
    zoningLayer = 'ZoningLayer'
    zoningCurrent = 'ZoningCurrent'

    PR_FLAG_Temp = 'Flags_Table_Temp'
    PPR_Assets_Temp_Pre_Dissolve = 'in_memory\\PPR_Assets_Temp_Pre_Dissolve'
    PPR_Assets_Temp = 'in_memory\\PPR_Assets_Temp'
    Park_IDs_Local = 'ParkNameIDs_' + today.strftime("%d%b%Y")
    PWD_Parcels_Local = 'PWDParcels_'+ today.strftime("%d%b%Y")
    Council_Districts_Local = 'Districts_'+ today.strftime("%d%b%Y")

    localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
    inMemory = 'in_memory'

    arcpy.env.workspace = localWorkspace
    arcpy.env.overwriteOutput = True

    #Update Local Copies of DataBridge Files
    localTables = arcpy.ListFeatureClasses('PWD_*')
    for t in localTables:
        arcpy.Delete_management(t)
    zoningFC = Update(zoningFC, Zoning_Overlays, 7, localWorkspace).rebuild()
    Council_Districts_Local = Update(Council_Districts_Local, Council_Districts_2016, 7, localWorkspace).rebuild()
    PWD_Parcels_Local = Update(PWD_Parcels_Local, PWD_PARCELS_DataBridge, 7, localWorkspace).rebuild()


    #Merge Parks with Parcels

    # Determine if PPR Assets has been updated in the last week, if so execute
    previousTables = sorted(
        [[f] + f.split('_') for f in arcpy.ListTables() if f.split('_')[0] == Park_IDs_Local.split('_')[0]],
        key=lambda r: r[-1], reverse=True)
    print(previousTables)
    if len(previousTables) > 1:
        print('Multiple tables detected')
        for t in previousTables[1:]:
            print(t)
            arcpy.Delete_management(t[0])

    if previousTables[0][2] != PWD_Parcels_Local.split('_')[1]:
        print('Updating Parks Table')
        previousTable = previousTables[0][0]
        print(previousTable)
        del previousTables
        print('Copying Parks Local')
        arcpy.FeatureClassToFeatureClass_conversion(PPR_Assets, inMemory, 'PPR_Assets_Temp_Pre_Dissolve')
        print('Dissolving Parks Polygons')
        arcpy.Dissolve_management(PPR_Assets_Temp_Pre_Dissolve, PPR_Assets_Temp, ['CHILD_OF'])
        print('Deleting undissolved layer')
        arcpy.Delete_management(PPR_Assets_Temp_Pre_Dissolve)
        print('Adding and calculating geometry')
        arcpy.AddGeometryAttributes_management(PPR_Assets_Temp, 'AREA', Area_Unit='SQUARE_FEET_US')
        arcpy.AddField_management(PPR_Assets_Temp, 'PARCEL_AREA', 'LONG')
        #arcpy.CalculateField_management(PPR_Assets_Temp, 'PARCEL_AREA', '!POLY_AREA!', 'PYTHON')
        arcpy.CalculateField_management(PPR_Assets_Temp, 'PARCEL_AREA', '!POLY_AREA!', 'PYTHON3')

        # Pull all currently posted park names and compare to previous
        cursor1 = arcpy.da.SearchCursor(PPR_Assets_Temp, ['CHILD_OF'])
        currentParks = [row[0] for row in cursor1]
        del cursor1
        print(previousTable)
        print([f.name for f in arcpy.ListFields(previousTable)])
        cursor2 = arcpy.da.SearchCursor(previousTable, ['CHILD_OF', 'LI_TEMP_ID'])
        parkDict = {row[0]: row[1] for row in cursor2}
        del cursor2
        # The IDs are negative so we're looking for the next LOWEST value to add
        minID = min([id for id in parkDict.values()])
        for p in currentParks:
            if p not in parkDict:
                minID -= 1
                parkDict[p] = minID

        # Create a new table schema and populate it
        arcpy.CreateTable_management(localWorkspace, Park_IDs_Local, previousTable)
        cursor3 = arcpy.da.InsertCursor(Park_IDs_Local, ['CHILD_OF', 'LI_TEMP_ID'])
        print([f.name for f in arcpy.ListFields(Park_IDs_Local)])
        for k, v in parkDict.items():
            cursor3.insertRow([k, v])
        arcpy.Delete_management(previousTable)
        del cursor3

        # Join Park IDs to Temp Parks Layer
        arcpy.JoinField_management(PPR_Assets_Temp, 'CHILD_OF', Park_IDs_Local, 'CHILD_OF', ['LI_TEMP_ID'])

        # Map Fields for Append
        fms = arcpy.FieldMappings()
        fm_ID = arcpy.FieldMap()
        fm_ID.addInputField(PPR_Assets_Temp, 'LI_TEMP_ID')
        fm_ID_Out = fm_ID.outputField
        fm_ID_Out.name = 'PARCELID'
        fm_ID.outputField = fm_ID_Out
        fm_Area = arcpy.FieldMap()
        fm_Area.addInputField(PPR_Assets_Temp, 'PARCEL_AREA')
        fm_Area_Out = fm_Area.outputField
        fm_Area_Out.name = 'GROSS_AREA'
        fm_Area.outputField = fm_Area_Out
        fms.addFieldMap(fm_ID)
        fms.addFieldMap(fm_Area)
        arcpy.FeatureClassToFeatureClass_conversion(PWD_PARCELS_DataBridge, localWorkspace, PWD_Parcels_Local)
        arcpy.Append_management(PPR_Assets_Temp, PWD_Parcels_Local, schema_type='NO_TEST', field_mapping=fms)


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
            arcpy.Clip_analysis(zoningCurrent, currentTract, tempZone)
            if int(arcpy.GetCount_management(tempZone).getOutput(0)) >= 1:
                print('Extracting Overlay')
                arcpy.Clip_analysis(localWorkspace + '\\' + PWD_Parcels_Local, currentTract, tempParcels)
                IntersectOutput = localWorkspace + '\\' + zoningFC + '_Int'
                print('Running Intersect')
                arcpy.Intersect_analysis([tempParcels] + [tempZone], IntersectOutput, 'ALL')
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
                fieldList = ['PARCELID', 'GROSS_AREA', 'OVERLAY_NAME']
                IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fieldList)
                countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
                count = 0
                print('Found ' + str(countin) + ' records in intersect table')
                breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
                for row in IntersectCursor:
                    count += 1
                    if count in breaks:
                        print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
                    #if (row[2] / float(row[1])) > 0.01:  #To implment 3% coverage and thinness minimum: row[3] > 0.3 and (row[2] / float(row[1])) > 0.03:
                    if row[fieldList.index('PARCELID')] in parcelDict:
                        tempList = parcelDict.get(row[0])
                        parcelDict[row[fieldList.index('PARCELID')]] = list(set([row[fieldList.index('OVERLAY_NAME')]] + tempList))
                    else:
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