import arcpy
import sys
import traceback
import datetime
from datetime import timedelta


try:
    today = datetime.datetime.today()
    oneWeekAgo = today - timedelta(days=7)

    PR_FLAG_SUMMARY = 'Database Connections\\LIGISDB.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY'

    Zoning_Overlays= 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_Overlays'

    PWD_PARCELS_DataBridge = 'Database Connections\\DataBridge.sde\\GIS_WATER.PWD_PARCELS'

    Council_Districts_2016 = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Council_Districts_2016'
    Council_Districts_Local = 'Districts'

    zoningFC = 'ZoningO_'+ today.strftime("%d%b%Y")
    zoningLayer = 'ZoningLayer' 
    zoningCurrent = 'ZoningCurrent'

    PR_FLAG_Temp = 'PR_FLAG_Temp'
    PWD_Parcels_Local = 'PWD_Parcels_'+ today.strftime("%d%b%Y")
    Council_Districts_Local = 'Districts_'+ today.strftime("%d%b%Y")

    localWorkspace = 'E:\Plan_Review_Flags\Workspace.gdb'
    inMemory = 'in_memory'

    arcpy.env.workspace = localWorkspace
    arcpy.env.overwriteOutput = True
    locallySaved = arcpy.ListFeatureClasses()

    #Delete local files that are more than a week old

    deleteFiles = [fc for fc in locallySaved if datetime.datetime.strptime(fc.split('_')[-1], "%d%b%Y") < oneWeekAgo]
    print('Checking for local versions of files')
    for fc in deleteFiles:
        print('Deleting ' + fc)
        arcpy.Delete_management(fc)
    localFiles = [[zoningFC, Zoning_Overlays], [PWD_Parcels_Local, PWD_PARCELS_DataBridge], [Council_Districts_Local, Council_Districts_2016]]

    #If there are no local files less than a week old, copy a new one
    for localF in localFiles:
        localName = localF[0].split('_')[0]
        if not any(fc.startswith(localName) for fc in locallySaved):
            print('Copying ' + localName)
            arcpy.FeatureClassToFeatureClass_conversion(localF[1], localWorkspace, localF[0])
        else:
            listIndex = None
            for fc in locallySaved:
                if fc.startswith(localName):
                    listIndex = locallySaved.index(fc)
                    break
            print('Changing variable for ' + localName + ' to exisiting local copy')
            localF[0] = locallySaved[listIndex]
    zoningFC = localFiles[0][0]
    PWD_Parcels_Local = localFiles[1][0]
    Council_Districts_Local = localFiles[2][0]

    del localFiles
    
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
        #if overlayCount == 0: #######################  <-----------
        arcpy.env.workspace = localWorkspace
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
            #if districtCount == 0: ####################################### <----------------------------
            arcpy.env.workspace = inMemory
            print('Processing Tract ' + tract[0] + "\n" + str(
                (float(districtCount) / float(districtTotal)) * 100.0) + '% Complete')
            districtCount += 1
            print("DISTRICT = '" + tract[0] + "'")
            arcpy.MakeFeatureLayer_management(localWorkspace + '\\' + Council_Districts_Local, currentTract, "DISTRICT = '" + tract[0] + "'")
            arcpy.Clip_analysis(zoningCurrent, currentTract, tempZone)
            if int(arcpy.GetCount_management(tempZone).getOutput(0)) >= 1:
                print('Examing Overlay')
                arcpy.Clip_analysis(localWorkspace + '\\' + PWD_Parcels_Local, currentTract, tempParcels)
                IntersectOutput = 'G:\\Scripts\\li-queries\\PR_FLAGS\\Workspace.gdb\\' + zoningFC + '_Int'
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
    arcpy.env.workspace = inMemory
    arcpy.TableToTable_conversion(PR_FLAG_SUMMARY, inMemory, PR_FLAG_Temp)
    zoneCursor = arcpy.da.UpdateCursor(PR_FLAG_Temp, ['PWD_PARCEL_ID', 'OVERLAY_ZONING'])
    print('Starting Cursor')
    for parcel in zoneCursor:
        if parcel[0] in parcelDict:
            parcel[1] = '|'.join(parcelDict.get(parcel[0]))
            zoneCursor.updateRow(parcel)
    del zoneCursor
    arcpy.TruncateTable_management(PR_FLAG_SUMMARY)
    arcpy.Append_management(PR_FLAG_Temp, PR_FLAG_SUMMARY, 'NO_TEST')
    arcpy.Delete_management(PR_FLAG_Temp)
    print('Script Complete')
    
except arcpy.ExecuteError:
    # log.critical('The script failed in Step 7' )
    msgs = arcpy.GetMessages(2)
    print(msgs)
    # log.error(msgs)
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    print(pymsg)
    arcpy.AddError(pymsg)
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    arcpy.AddError(pymsg)
    sys.exit(1)