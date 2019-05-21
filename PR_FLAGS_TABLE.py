"""
Note:
This script was originally designed to create a table listing every pwd parcel in the city and related attributes.
The need for this list has since been scraped but there is still a need for the PR GIS layers created in this script.
Much of the process has been commented out but left in place in case the need for this ever returns
"""

import sys
import traceback

import arcpy
import datetime
from datetime import timedelta

localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
inMemory = 'in_memory'
arcpy.env.overwriteOutput = True
arcpy.env.workspace = localWorkspace
print('''Starting script 'PermitReviewScripts.py'...''')


# TODO Check parameters for what is considered a corner property

# Step 1: Configure log file
'''
try:
    print('Step 1: Configuring log file...')
    log_file_path = 'C:\Users\Shannon.Holm\Documents\LNI_Data\PermitReviewTriggers\PermitReviews.log'
    log = logging.getLogger('ReviewTriggerIdentifier')
    log.setLevel(logging.INFO)
    hdlr = logging.FileHandler(log_file_path)
    hdlr.setLevel(logging.INFO)
    hdlrFormatter = logging.Formatter('%(name)s - %(levelname)s - %(asctime)s - %(message)s', datefmt='%m/%d/%Y  %I:%M:%S %p')
    hdlr.setFormatter(hdlrFormatter)
    log.addHandler(hdlr)
    log.info('Script Started...')
    log.info('Step 1: Log file configured.')
    print('SUCCESS at Step 1')
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    arcpy.AddError(pymsg)
    sys.exit(1)
'''


# Step 2: Set script parameters
print('Step 2: Setting script parameters...')
#Identify Dates
today = datetime.datetime.today()
oneWeekAgo = today - timedelta(days=7)

# External data sources
PWD_PARCELS_DataBridge = 'Database Connections\\DataBridge.sde\\GIS_WATER.PWD_PARCELS'
Zoning_BaseDistricts = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_BaseDistricts'
FEMA_100_flood_Plain = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.FEMA_100_flood_Plain'
Historic_Sites_PhilReg = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Historic_Sites_PhilReg'
Zoning_Overlays = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_Overlays'
Zoning_SteepSlopeProtectArea_r = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_SteepSlopeProtectArea_r'
GSI_SMP_TYPES = 'Database Connections\\DataBridge.sde\\GIS_WATER.GSI_SMP_TYPES'
GISLNI_Corner_Properties = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_CORNER_PROPERTIES'
GISLNI_Districts = 'Database Connections\\GISLNI.sde\\GIS_LNI.DISTRICTS_BROAD'
Council_Districts_2016 = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Council_Districts_2016'

# Internal data sources
PWD_Parcels_Local = 'PWD_Parcels_'+ today.strftime("%d%b%Y")
PWD_Spatial_Join = 'PWD_Spatial_Join'
CornerProperties = 'Corner_Properties'
PWD_PARCELS_SJ = 'PWD_PARCELS_Spatial_Join'
CornerPropertiesSJ_P = 'CornerPropertiesSJ_P'
Districts = 'Districts'
Hist_Sites_PhilReg = 'Hist_Sites_PhilReg'
Zon_Overlays = 'R_Zoning_Overlays_' + today.strftime("%d%b%Y")
Zoning_SteepSlope = 'PCPC_SteepSlope'
PWD_GSI_SMP_TYPES = 'PWD_GSI_SMP_TYPES'
Zon_BaseDistricts = 'Zon_BaseDistricts_' + today.strftime("%d%b%Y")
ArtCommission_BuildingIDSinageReview = 'ArtCommission_BuildingIDSinageReview'
FloodPlain100Yr = 'PCPC_100YrFloodPlain'
PCPC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PCPC_Intersect'
PAC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PAC_Intersect'
Flags_Table_Temp = 'Flags_Table_Temp'
Council_Districts_Local = 'Districts_'+ today.strftime("%d%b%Y")

# LIGISDB Output FeatureClasses
GIS_LNI_PR_PCPC_CityAveSiteReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_CityAveSiteReview'
GIS_LNI_PR_PCPC_RidgeAveFacadeReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_RidgeAveFacadeReview'
GIS_LNI_PR_PCPC_MasterPlanReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_MasterPlanReview'
GIS_LNI_PR_PCPC_CenterCityFacadeReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_CenterCityFacadeReview'
GIS_LNI_PR_PCPC_NeighborConsReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_NeighborConsReview'
GIS_LNI_PR_PCPC_WissWaterSiteReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_WissWaterSiteReview'
GIS_LNI_PR_PCPC_100YrFloodPlain = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_100YrFloodPlain'
GIS_LNI_PR_PCPC_SteepSlope = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_SteepSlope'
GIS_LNI_PR_PCPC_SkyPlaneReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_SkyPlaneReview'
GIS_LNI_PR_PAC_BuildIDSignageReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC_BuildIDSignageReview'
GIS_LNI_PR_PAC_ParkwayBufferReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC_ParkwayBufferReview'
GIS_LNI_PR_PAC_SignageSpecialControl = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC_SinageSpecialControl'
GIS_LNI_PR_PWD_GSI_Buffer = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PWD_GSI_Buffer'
GIS_LNI_PR_PWD_GreenRoofReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PWD_GreenRoofReview'
GIS_LNI_PR_PHC_HistoricalResReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PHC'

PR_FLAG_SUMMARY = 'Database Connections\\GISLNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY_TEST' #TODO Test
print('SUCCESS at Step 2')


#Step 3A: Build Initial PWD Spatial Join Data
print('Building parcel layer..')

localFiles = [[Zon_BaseDistricts, Zoning_BaseDistricts], [Zon_Overlays, Zoning_Overlays], [PWD_Parcels_Local, PWD_PARCELS_DataBridge],
              [Council_Districts_Local, Council_Districts_2016]]

locallySaved = [l[0] for l in localFiles]
print locallySaved

# Delete local files that are more than a week old
if locallySaved is not None:
    deleteFiles = [fc for fc in locallySaved if datetime.datetime.strptime(fc.split('_')[-1], "%d%b%Y") < oneWeekAgo]
    print('Checking for local versions of files')
    for fc in deleteFiles:
        print('Deleting ' + fc)
        arcpy.Delete_management(fc)
    locallySaved = []


# If there are no local files less than a week old, copy a new one
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
Zon_BaseDistricts = localFiles[0][0]
Zon_Overlays = localFiles[1][0]
PWD_Parcels_Local = localFiles[2][0]
Council_Districts_Local = localFiles[-1][0]

#del localFiles


print('Copying Corner Properties Local')
arcpy.FeatureClassToFeatureClass_conversion(GISLNI_Corner_Properties, localWorkspace, CornerProperties)
print('Copying Districts Local')
arcpy.FeatureClassToFeatureClass_conversion(GISLNI_Districts, localWorkspace, Districts)
print ('Spatial Joining Parcels and Districts')
#Creates District Field in Parcel FC
arcpy.SpatialJoin_analysis(PWD_Parcels_Local, Districts, PWD_PARCELS_SJ)
print('Converting Corner Properties to Points')
#Create 'corner' field in parcel FC when the parcel contains the corner polygon centroid
arcpy.FeatureToPoint_management(CornerProperties, CornerPropertiesSJ_P, 'INSIDE')
print('Creating Corner Field')
arcpy.AddField_management(CornerPropertiesSJ_P, 'Corner', 'SHORT')
arcpy.CalculateField_management(CornerPropertiesSJ_P, 'Corner', '1', 'PYTHON_9.3')
arcpy.Delete_management(CornerProperties)
arcpy.Delete_management(PWD_Parcels_Local)
arcpy.Delete_management(Districts)
print('Spatial Joing Parcels and Corner Properties')
arcpy.SpatialJoin_analysis(PWD_PARCELS_SJ, CornerPropertiesSJ_P, PWD_Spatial_Join)
arcpy.Delete_management(CornerPropertiesSJ_P)
arcpy.Delete_management(PWD_PARCELS_SJ)
print('SUCCESS at Step 3')
############################################################################################################


# Step 3: Create plan review feature classes

print('Copying Overlays local')
#arcpy.FeatureClassToFeatureClass_conversion(Zoning_BaseDistricts, localWorkspace, Zon_BaseDistricts)
#arcpy.FeatureClassToFeatureClass_conversion(Zoning_Overlays, localWorkspace, Zon_Overlays)
arcpy.FeatureClassToFeatureClass_conversion(Zoning_SteepSlopeProtectArea_r, localWorkspace, Zoning_SteepSlope)
arcpy.FeatureClassToFeatureClass_conversion(GSI_SMP_TYPES, localWorkspace, PWD_GSI_SMP_TYPES)


print('Adding Corner properties to dictionary')
cornerPropertyCursor = arcpy.da.SearchCursor(PWD_Spatial_Join, ['PARCELID', 'ADDRESS', 'GROSS_AREA', 'DISTRICT', 'Corner'] )
parcelDict = {}
for parcel in cornerPropertyCursor:
    if parcel[4] == 1:
        parcelDict[parcel[0]] = {'Address': parcel[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [], 'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': 1, 'ParcelArea': parcel[2], 'BaseZoning': [], 'OverlayZoning': [], 'District': parcel[3]}
    else:
        parcelDict[parcel[0]] = {'Address': parcel[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [], 'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': 0, 'ParcelArea': parcel[2], 'BaseZoning': [], 'OverlayZoning': [], 'District': parcel[3]}

del cornerPropertyCursor




# Function that will be used later to create plan review feature classes by selecting certain data from
# the overlays
def parcelFlag(reviewName, reviewType, sourceFC, fieldCalculation, whereClause, outputFC, localWorkspace, parcels,
               parcelDict):
    sourceFC = localWorkspace + '\\' + sourceFC if 'Database Connection' not in sourceFC else sourceFC
    IntersectOutput = localWorkspace + '\\' + reviewName + '_intersect'
    reviewLayer = reviewType + '_' + reviewName
    reviewField = 'CODE' if reviewType == zonB else 'OVERLAY_NAME' if reviewType == zonO else reviewName + 'ReviewReason'
    print reviewField

    if '_Buffer' in reviewName:
        print('Buffering')
        arcpy.Buffer_analysis(sourceFC, reviewLayer, '500 Feet')
    else:
        print('Creating Local FC for ' + reviewName)
        arcpy.FeatureClassToFeatureClass_conversion(sourceFC, localWorkspace, reviewLayer,
                                                    whereClause)

    # All FCs except for Zoning are copied to LIGISDB
    if outputFC:
        print('Copying FC to GISLNI')
        arcpy.AddField_management(reviewLayer, reviewField, 'TEXT')
        arcpy.CalculateField_management(reviewLayer, reviewField, fieldCalculation, 'PYTHON_9.3')
        arcpy.AddField_management(reviewLayer, 'REVIEW_TYPE', 'TEXT', field_length=2000)
        arcpy.CalculateField_management(reviewLayer, 'REVIEW_TYPE', '"' + reviewName + '"', 'PYTHON_9.3')
        arcpy.DeleteRows_management(outputFC)
        arcpy.Append_management(reviewLayer, outputFC, 'NO_TEST')

    print('Performing Intersect')
    #Create polygons where review polygons overlap with parcels
    arcpy.Intersect_analysis([parcels]+[reviewLayer], IntersectOutput, 'ALL')
    print('Intersect Complete')

    arcpy.Delete_management(reviewLayer)

    #To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
    actualFields = [f.name for f in arcpy.ListFields(IntersectOutput)]
    print actualFields
    arcpy.AddField_management(IntersectOutput, 'ThinessRatio', 'FLOAT')
    arcpy.AddField_management(IntersectOutput, 'POLY_AREA', 'FLOAT') #This is a dummy field to statisfy cursor, delete this line if thiness ratio is brought back.  The field indexes below are too hard coded to rearrange
    """ #NOTE Thiness calculation was removed by request
    arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
    arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
    arcpy.CalculateField_management(IntersectOutput, 'ThinessRatio',
                                    "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')

    """
    fieldList = ['PARCELID', 'ADDRESS', 'DISTRICT', 'Corner', 'GROSS_AREA', 'POLY_AREA',
                 'ThinessRatio', reviewField]
    IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fieldList)
    countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
    count = 0
    print('Found ' + str(countin) + ' records in input table')
    breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
    for row in IntersectCursor:
        count += 1
        if count in breaks:
            print('Parsing Intersect FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
        #Only polygons with a thiness ratio of over 0.3 and a parcel coverage of more than 3% are included in analysis
        if row[1] != '' and row[1] is not None and row[7] != '': #and row[6] > 0.3 and (row[5] / float(row[4])) > 0.03 :
            #If parcel has not made it into dictionary, parcel gets a new entry added
            if row[0] not in parcelDict and reviewType != zonB and reviewType != zonO:
                tempDict = {'Address': row[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [], 'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': row[3], 'ParcelArea': row[4], 'BaseZoning': [], 'OverlayZoning': [], 'District': row[2]}
                tempDict[reviewType] = [row[7]]
                if fieldCalculation == '"100 Year Flood Plain"':
                    tempDict['Floodplain'] = 1
                if fieldCalculation == '"Steep Slope"':
                    tempDict['SteepSlope'] = 1
                parcelDict[row[0]] = tempDict
            #If parcel already exists, its current dictionary entry is appended with new review information
            elif row[0] in parcelDict:
                tempDict = parcelDict.get(row[0])
                oldList = tempDict.get(reviewType)
                #The set function removes all duplicates from list
                tempDict[reviewType] = list(set([row[7]] + oldList))
                if fieldCalculation == '"100 Year Flood Plain"':
                    tempDict['Floodplain'] = 1
                if fieldCalculation == '"Steep Slope"':
                    tempDict['SteepSlope'] = 1
                parcelDict[row[0]] = tempDict

    arcpy.Delete_management(IntersectOutput)

    return parcelDict
###################################################################################################################

# Plan review flag types
pcpcR = 'PCPC'
pacR = 'PAC'
pwdR = 'PWD'
phcR = 'PHC'
zonB = 'BaseZoning'
zonO = 'OverlayZoning'

# Inputs to be run through parcelFlag function in order to create the plan review feature classes
PCPC_CityAveSiteReview = ['CityAveSiteReview', pcpcR, Zon_Overlays, '!Overlay_Name!',
                          "Overlay_Name IN('/CAO City Avenue Overlay District - City Avenue Regional Center Area','/CAO City Avenue Overlay District - City Avenue Village Center Area')",
                          GIS_LNI_PR_PCPC_CityAveSiteReview]
PCPC_RidgeAveFacadeReview = ['RidgeAveFacadeReview', pcpcR, Zon_Overlays, '!Overlay_Name!',
                             "Overlay_Name IN('/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue')",
                             GIS_LNI_PR_PCPC_RidgeAveFacadeReview]
PCPC_MasterPlanReview = ['MasterPlanReview', pcpcR, Zon_BaseDistricts, '!Long_Code!',
                         "Long_Code IN('RMX-1', 'RMX-2', 'SP-ENT', 'SP-INS', 'SP-STA')",
                         GIS_LNI_PR_PCPC_MasterPlanReview]
PCPC_CenterCityFacadeReview = ['CenterCityFacadeReview', pcpcR, Zon_Overlays, '!Overlay_Name!',
                               "Overlay_Name IN('/CTR Center City Overlay District - Chestnut and Walnut Street Area', '/CTR Center City Overlay District - Broad Street Area South','/CTR Center City Overlay District - Market Street Area East')",
                               GIS_LNI_PR_PCPC_CenterCityFacadeReview]
PCPC_NeighborConsReview = ['NeighborConsReview', pcpcR, Zon_Overlays, '!Overlay_Name!',
                           "Overlay_Name IN('/NCO Neighborhood Conservation Overlay District - Central Roxborough','/NCO Neighborhood Conservation Overlay District - Overbrook Farms','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2','/NCO Neighborhood Conservation Overlay District - Queen Village','/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough')",
                           GIS_LNI_PR_PCPC_NeighborConsReview]
PCPC_WissahickonWatershedSiteReview = ['WissahickonWatershedSiteReview', pcpcR, Zon_Overlays, '!Overlay_Name!',
                                       "Overlay_Name IN('/NCO Neighborhood Conservation Overlay District - Central Roxborough','/NCO Neighborhood Conservation Overlay District - Overbrook Farms','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2','/NCO Neighborhood Conservation Overlay District - Queen Village','/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough')",
                                       GIS_LNI_PR_PCPC_WissWaterSiteReview]
PCPC_100YrFloodPlain = ['FloodPlainReview', pcpcR, FEMA_100_flood_Plain, '"100 Year Flood Plain"', None,
                        GIS_LNI_PR_PCPC_100YrFloodPlain]
PCPC_SteepSlope = ['SteepSlopeReview', pcpcR, Zoning_SteepSlopeProtectArea_r, '"Steep Slope"', None,
                   GIS_LNI_PR_PCPC_SteepSlope]
PCPC_SkyPlaneReview = ['SkyPlaneReview', pcpcR, Zon_BaseDistricts, '!Long_Code!', "Long_Code IN('CMX-4','CMX-5')",
                       GIS_LNI_PR_PCPC_SkyPlaneReview]
PAC_BuildIDSignageReview = ['BuildIDSignageReview', pacR, Zon_BaseDistricts, '!LONG_CODE!',
                            "Long_Code IN('ICMX', 'I-1', 'IRMX')", GIS_LNI_PR_PAC_BuildIDSignageReview]
PAC_ParkwayBufferReview = ['ParkwayBufferReview', pacR, Zon_Overlays, '!Overlay_Name!',
                           "Overlay_Name IN('/CTR Center City Overlay District - Parkway Buffer')",
                           GIS_LNI_PR_PAC_ParkwayBufferReview]
PAC_SinageSpecialControl = ['SinageSpecialControl', pacR, Zon_Overlays, '!Overlay_Name!',
                            "Overlay_Name IN('/CTR Center City Overlay District - Rittenhouse Square','/CTR Center City Overlay District - Center City Commercial Area','/CTR Center City Overlay District - Convention Center Area','/CTR Center City Overlay District - Independence Hall Area','/CTR Center City Overlay District - Vine Street Area','/CTR Center City Overlay District - Washington Square','/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood','/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue','/NCA Neighborhood Commercial Area Overlay District - Main Street/Manayunk and Venice Island','/NCA Neighborhood Commercial Area Overlay District - Logan Triangle','/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue','/NCA Neighborhood Commercial Area Overlay District - Lower and Central Germantown','/NCA Neighborhood Commercial Area Overlay District - North Delaware Avenue','/NCA Neighborhood Commercial Area Overlay District - Spring Garden','Accessory Sign Controls - Special Controls for Cobbs Creek, Roosevelt Boulevard, and Department of Parks and Recreation Land')",
                            GIS_LNI_PR_PAC_SignageSpecialControl]
PHC_HistoricalResReview = ['HistoricalResReview', phcR, Historic_Sites_PhilReg, '"Historic Designation"', None,
                           GIS_LNI_PR_PHC_HistoricalResReview]
PWD_GreenRoofReview = ['GreenRoofReview', pwdR, PWD_GSI_SMP_TYPES, '"GREEN ROOF"', "SUBTYPE IN( 10 )",
                       GIS_LNI_PR_PWD_GreenRoofReview]
PWD_GSI_Buffer = ['GSI_Buffer', pwdR, PWD_GSI_SMP_TYPES, '"Green Infrastructure"', None, GIS_LNI_PR_PWD_GSI_Buffer]

# List to iterate inputs through parcel flag function
reviewList = [PCPC_CityAveSiteReview, PCPC_RidgeAveFacadeReview, PCPC_MasterPlanReview, PCPC_CenterCityFacadeReview,
              PCPC_NeighborConsReview,
              PCPC_WissahickonWatershedSiteReview, PCPC_100YrFloodPlain, PCPC_SteepSlope, PCPC_SkyPlaneReview,
              PAC_BuildIDSignageReview,
              PAC_ParkwayBufferReview, PAC_SinageSpecialControl, PHC_HistoricalResReview, PWD_GreenRoofReview,
              PWD_GSI_Buffer]


# Call the parcelFlag funtion on each plan review input in order to create the plan review feature classes
currentTract = 'CurrentDistrict'
tempParcels = 'TempParcels'
tempZone = 'TempZone'
districtCount = 0
districtTotal = int(arcpy.GetCount_management(Council_Districts_Local).getOutput(0))
arcpy.CalculateField_management(Council_Districts_Local, 'DISTRICT', '!DISTRICT!.strip(' ')', 'PYTHON_9.3')
districtTileCursor = arcpy.da.SearchCursor(Council_Districts_Local, 'DISTRICT')
parcelDict = {}
for tract in districtTileCursor:
    districtCount += 1
    print('Processing Tract ' + tract[0] + "\n" + str(
        (float(districtCount) / float(districtTotal)) * 100.0) + '% Complete')
    print("DISTRICT = '" + tract[0] + "'")
    # arcpy.FeatureClassToFeatureClass_conversion(Council_Districts_Local, inMemory, currentTract, "DISTRICT = '" + tract[0] + "'")
    arcpy.MakeFeatureLayer_management(localWorkspace + '\\' + Council_Districts_Local, currentTract,
                                      "DISTRICT = '" + tract[0] + "'")
    arcpy.Clip_analysis(localWorkspace + '\\' + PWD_Spatial_Join, currentTract, tempParcels)
    for r in reviewList:
        print('Beginning ' + r[0])
        inputs = tuple(r[:] + [localWorkspace, tempParcels, parcelDict])
        parcelFlag(*inputs)


#Step 20: Update Flags Table
arcpy.CreateTable_management(localWorkspace, Flags_Table_Temp, PR_FLAG_SUMMARY)
#ParcelDict Schema: {PWD_PARCELID:{Address:'', PAC:[], PCPC:[], PHC:[], PWD:[], 'SteepSlope':bool, 'Floodplain':bool, CornerProp:bool, ParcelArea:'', BaseZoning:[], OverlayZoning:[], LIDistrict:''}
flagFields = [f.name for f in arcpy.ListFields(Flags_Table_Temp)]
del flagFields[flagFields.index('OBJECTID')]
del flagFields[flagFields.index('BASE_ZONING')]
del flagFields[flagFields.index('OVERLAY_ZONING')]
del flagFields[flagFields.index('ZONING_RCO')]
countin = len(parcelDict)
count = 0
breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
print('Preparing to Append ' + str(countin) + ' rows')
flagCursor = arcpy.da.InsertCursor(Flags_Table_Temp, flagFields)
for k, v in parcelDict.iteritems():
    count += 1
    if count in breaks:
        arcpy.AddMessage('Creation of Table Rows ' + str(int(round(count * 100.0 / countin))) + '% complete...')
    parcelID = k
    address = v['Address']
    pacBool = 1 if v['PAC'] else 0
    pac = '|'.join(v['PAC'])
    pcpcBool = 1 if v['PCPC'] else 0
    pcpc = '|'.join(v['PCPC'])
    phcBool = 1 if v['PHC'] else 0
    phc = '|'.join(v['PHC'])
    pwdBool = 1 if v['PWD'] else 0
    pwd = '|'.join(v['PWD'])
    slope = v['SteepSlope']
    flood = v['Floodplain']
    corner = 1 if v['CornerProp'] else 0
    area = v['ParcelArea']
    district = v['District']
    flagCursor.insertRow([address, parcelID, pacBool, pac, pcpcBool, pcpc, phcBool, phc, pwdBool, pwd, corner, area, district, flood, slope])
"""
#Table should not be copied to DB until all fields are populated
arcpy.TruncateTable_management(PR_FLAG_SUMMARY)
print('Copying to GISLNI')
arcpy.Append_management(Flags_Table_Temp, PR_FLAG_SUMMARY, 'NO_TEST')
print('Copy Complete')
"""
