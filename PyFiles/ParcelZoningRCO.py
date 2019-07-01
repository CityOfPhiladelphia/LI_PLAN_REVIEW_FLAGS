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

    Zoning_Overlays = DataBridge.sde_path+'\\GIS_PLANNING.Zoning_RCO'

    PWD_PARCELS_DataBridge = DataBridge.sde_path+'\\GIS_WATER.PWD_PARCELS'

    Council_Districts_2016 = DataBridge.sde_path+'\\GIS_PLANNING.Council_Districts_2016'

    zoningFC = 'ZoningRCO_'+ today.strftime("%d%b%Y")
    zoningLayer = 'ZoningLayer'
    zoningCurrent = 'ZoningCurrent'

    PR_FLAG_Temp = 'Flags_Table_Temp'
    PWD_Parcels_Local = 'PWD_Parcels_'+ today.strftime("%d%b%Y")
    Council_Districts_Local = 'Districts_'+ today.strftime("%d%b%Y")

    localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
    inMemory = 'in_memory'

    arcpy.env.workspace = localWorkspace
    arcpy.env.overwriteOutput = True
    locallySaved = arcpy.ListFeatureClasses()

    #Delete local files that are more than a week old

    deleteFiles = [fc for fc in locallySaved if (fc.endswith(str(datetime.datetime.now().year)) or fc.endswith(str(int(datetime.datetime.now().year)-1))) and datetime.datetime.strptime(fc.split('_')[-1], "%d%b%Y") < oneWeekAgo]
    print('Checking for local versions of files')
    for fc in deleteFiles:
        print('Deleting ' + fc)
        arcpy.Delete_management(fc)
    localFiles = [[zoningFC, Zoning_Overlays], [PWD_Parcels_Local, PWD_PARCELS_DataBridge], [Council_Districts_Local, Council_Districts_2016]]

    #If there are no local files less than a week old, copy a new one
    #TODO get this to stop unecessary copies

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

    #Append all ROC Names to a list.  Each RCO will be iterated through and added to the dictionary
    print(zoningFC)
    print([f.name for f in arcpy.ListFields(zoningFC)])

    rcoOIDCursor = arcpy.da.SearchCursor(zoningFC, 'ORGANIZATION_NAME')
    rcoIDS = list(set([row[0] for row in rcoOIDCursor]))
    del rcoOIDCursor

    #Create lookup dictionary for RCO Objectid names:
    from li_dbs_Lazy import DataBridge
    lookupSQL = "select OBJECTID, ORGANIZATION_NAME from GIS_PLANNING.ZONING_RCO"
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
        #if overlayCount == 0: #######################  <-----------
        arcpy.env.workspace = localWorkspace
        overlayCount += 1
        print('Starting ' + str(overlayType) + ', ' + str(overlayCount)+ ' of ' + str(overlayTotal))
        arcpy.SelectLayerByAttribute_management(zoningLayer, 'NEW_SELECTION', "ORGANIZATION_NAME = '" + str(overlayType if "'" not in overlayType else overlayType.replace("'", "|| CHR(39) ||")) + "'")
        arcpy.MakeFeatureLayer_management(zoningLayer, zoningCurrent)
        IntersectOutput = localWorkspace + '\\' + zoningFC + '_Int'
        arcpy.Intersect_analysis([PWD_Parcels_Local] + [zoningCurrent], IntersectOutput, 'ALL')
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
                print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
            # if (row[2] / float(row[1])) > 0.01:  #To implment 3% coverage and thinness minimum: row[3] > 0.3 and (row[2] / float(row[1])) > 0.03:
            if row[fieldList.index('PARCELID')] in parcelDict:
                tempList = parcelDict.get(row[0])
                parcelDict[row[fieldList.index('PARCELID')]] = list(set([lookupDict[row[fieldList.index('ORGANIZATION_NAME')]]] + tempList))
            else:
                parcelDict[row[fieldList.index('PARCELID')]] = [lookupDict[row[fieldList.index('ORGANIZATION_NAME')]]]
        arcpy.Delete_management(IntersectOutput)


        currentTract = 'CurrentDistrict'
        tempParcels = 'TempParcels'
        tempZone = 'TempZone'
        districtCount = 0
        districtTotal = int(arcpy.GetCount_management(Council_Districts_Local).getOutput(0))
        arcpy.CalculateField_management(Council_Districts_Local, 'DISTRICT', '!DISTRICT!.strip(' ')', 'PYTHON_9.3')
        districtTileCursor = arcpy.da.SearchCursor(Council_Districts_Local, 'DISTRICT')

        del districtTileCursor
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
    recipientslist = ['DANI.INTERRANTE@PHILA.GOV', 'SHANNON.HOLM@PHILA.GOV', 'Philip.Ribbens@Phila.gov', 'LIGISTeam@phila.gov']
    commaspace = ', '
    msg = MIMEText('AUTOMATIC EMAIL \n Plan Review Flags Update Failed during update: \n' + pymsg)
    msg['To'] = commaspace.join(recipientslist)
    msg['From'] = sender
    msg['X-Priority'] = '2'
    msg['Subject'] = 'Plan Review Flags Table Update Failure'
    server.server.sendmail(sender, recipientslist, msg.as_string())
    server.server.quit()
    sys.exit(1)
