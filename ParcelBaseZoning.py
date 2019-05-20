import arcpy
import sys
import traceback
import datetime
from datetime import timedelta


#try:
today = datetime.datetime.today()
oneWeekAgo = today - timedelta(days=7)

PR_FLAG_SUMMARY = 'Database Connections\\GISLNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY_TEST' #TODO Test

Zoning_BaseDistricts = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_BaseDistricts'
Zoning_Overlays= 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_Overlays'

PWD_PARCELS_DataBridge = 'Database Connections\\DataBridge.sde\\GIS_WATER.PWD_PARCELS'

Council_Districts_2016 = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Council_Districts_2016'
Council_Districts_Local = 'Districts'

zoningFC = 'ZoningB_'+ today.strftime("%d%b%Y")

PR_FLAG_Temp = 'Flags_Table_Temp'
PWD_Parcels_Local = 'PWD_Parcels_'+ today.strftime("%d%b%Y")
Council_Districts_Local = 'Districts_'+ today.strftime("%d%b%Y")

localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
inMemory = 'in_memory'

arcpy.env.workspace = localWorkspace
arcpy.env.overwriteOutput = True
locallySaved = arcpy.ListFeatureClasses()
print locallySaved

#Delete local files that are more than a week old
if locallySaved is not None:
    deleteFiles = [fc for fc in locallySaved if (fc.endswith(str(datetime.datetime.now().year)) or fc.endswith(str(int(datetime.datetime.now().year)-1))) and datetime.datetime.strptime(fc.split('_')[-1], "%d%b%Y") < oneWeekAgo]
    print('Checking for local versions of files')
    for fc in deleteFiles:
        print('Deleting ' + fc)
        arcpy.Delete_management(fc)
    locallySaved = []
localFiles = [[zoningFC, Zoning_BaseDistricts], [PWD_Parcels_Local, PWD_PARCELS_DataBridge], [Council_Districts_Local, Council_Districts_2016]]

#If there are no local files less than a week old, copy a new one
print locallySaved
for localF in localFiles:
    localName = localF[0].split('_')[0]
    if locallySaved is None or not any(fc.startswith(localName) for fc in locallySaved):
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


currentTract = 'CurrentDistrict'
tempParcels = 'TempParcels'
tempZone = 'TempZone'
districtCount = 0
districtTotal = int(arcpy.GetCount_management(Council_Districts_Local).getOutput(0))
arcpy.CalculateField_management(Council_Districts_Local, 'DISTRICT', '!DISTRICT!.strip(' ')', 'PYTHON_9.3')
districtTileCursor = arcpy.da.SearchCursor(Council_Districts_Local, 'DISTRICT')
parcelDict = {}
for tract in districtTileCursor:
    #if districtCount == 0:################################################
    arcpy.env.workspace = inMemory
    districtCount += 1
    print('Processing Tract ' + tract[0] + "\n" + str((float(districtCount) / float(districtTotal)) * 100.0) + '% Complete')
    print("DISTRICT = '" + tract[0] + "'")
    #arcpy.FeatureClassToFeatureClass_conversion(Council_Districts_Local, inMemory, currentTract, "DISTRICT = '" + tract[0] + "'")
    arcpy.MakeFeatureLayer_management(localWorkspace + '\\' + Council_Districts_Local, currentTract, "DISTRICT = '" + tract[0] + "'")
    arcpy.Clip_analysis(localWorkspace + '\\' + zoningFC, currentTract, tempZone)
    arcpy.Clip_analysis(localWorkspace + '\\' + PWD_Parcels_Local, currentTract, tempParcels)
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


    fieldList = ['PARCELID', 'GROSS_AREA', 'POLY_AREA',
                 'Thinness', 'CODE']
    IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fieldList)
    countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
    count = 0
    print('Found ' + str(countin) + ' records in intersect table')
    breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
    for row in IntersectCursor:
        count += 1
        if count in breaks:
            print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
        if (row[2] / float(row[1])) > 0.01:  #To implment 3% coverage and thinness minimum: and row[3] > 0.3 and (row[2] / float(row[1])) > 0.03:
            if row[0] in parcelDict:
                tempList = parcelDict.get(row[0])
                parcelDict[row[0]] = list(set([row[4]] + tempList))
            else:
                parcelDict[row[0]] = [row[4]]
    arcpy.Delete_management(IntersectOutput)
    arcpy.Delete_management(currentTract)
    arcpy.Delete_management(tempZone)
    arcpy.Delete_management(tempParcels)
del districtTileCursor

arcpy.env.workspace = localWorkspace
arcpy.TableToTable_conversion(PR_FLAG_SUMMARY, localWorkspace, PR_FLAG_Temp)
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
        parcel[1] = '|'.join(parcelDict.get(parcel[0]))
        del parcelDict[parcel[0]]
        zoneCursor1.updateRow(parcel)
del zoneCursor1


remainingParcels = 'Parcels_Without_Flags'
arcpy.CreateTable_management(localWorkspace, remainingParcels, PR_FLAG_Temp)
zoneCursor2 = arcpy.da.InsertCursor(remainingParcels, ['PWD_PARCEL_ID', 'BASE_ZONING'])
for k,v in parcelDict.iteritems():
    zoneCursor2.insertRow([k, '|'.join(v)])
arcpy.Append_management(remainingParcels, PR_FLAG_Temp, 'NO_TEST')

#arcpy.TruncateTable_management(PR_FLAG_SUMMARY)
#arcpy.Append_management(PR_FLAG_Temp, PR_FLAG_SUMMARY, 'NO_TEST')

#arcpy.Delete_management(PR_FLAG_Temp)
"""
except arcpy.ExecuteError:
    # log.critical('The script failed in Step 7' )
    msgs = arcpy.GetMessages(2)
    print(msgs)
    print('Step 18 Failed')# log.error(msgs)
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
"""