"""
Plan Review Flags - Part 1 of 5
This script copies all source data local produces the individual flag attributes for every property.
Base Zoning, Overlay Zoning, and RCO information are populated by subsequent scripts in this package.
These processes were moved to separate scripts due to CPU memory issues
The final product is pushed back to databridge in CopyToEnterprise.py
#TODO MAJOR: Rewrite entire process into 1 .py file.  New script should populate Base Zoning, Overlay Zoning, Floodplain, and PWD intially
#TODO MAJOR: Second part of script should build boolean fields from initial populated fields rather than more intersect analysis
"""
import datetime
import logging
import sys
import os
import traceback
from datetime import timedelta

import arcpy
from sde_connections import DataBridge, GISLNI
dir_path = os.path.dirname(os.path.realpath(__file__))
localWorkspace = log_file_path = os.path.dirname(dir_path) + '\\Workspace.gdb'
DORinputGDB = os.path.dirname(dir_path) + '\\DORInput.gdb'
inMemory = 'in_memory'

arcpy.env.workspace = localWorkspace
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(2272)
arcpy.env.geographicTransformations = 'WGS_1984_(ITRF00)_To_NAD_1983'
editDB = GISLNI.sde_path
edit = arcpy.da.Editor(editDB)
print('''Starting script 'PermitReviewScripts.py'...''')

# Step 1: Configure log file
try:

    print('Step 1: Configuring log file...')
    log_file_path = os.path.dirname(dir_path) + '\\Logs\\PermitReviewFlags.log'
    log = logging.getLogger('PR Flags Part 1')
    log.setLevel(logging.INFO)
    hdlr = logging.FileHandler(log_file_path)
    hdlr.setLevel(logging.INFO)
    hdlrFormatter = logging.Formatter('%(name)s - %(levelname)s - %(asctime)s - %(message)s',
                                      datefmt='%m/%d/%Y  %I:%M:%S %p')
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
    log.info('Beginning PR Flags Part 1')

    # Step 2: Set script parameters
    print('Step 2: Setting script parameters...')
    # Identify Dates
    today = datetime.datetime.today()
    oneWeekAgo = today - timedelta(days=7)

    # External data sources
    PWD_PARCELS_DataBridge = DataBridge.sde_path + '\\GIS_WATER.PWD_PARCELS'
    Zoning_BaseDistricts = DataBridge.sde_path + '\\GIS_PLANNING.Zoning_BaseDistricts'
    FEMA_100_flood_Plain = DataBridge.sde_path + '\\GIS_PLANNING.FEMA_100_flood_Plain'
    Historic_Sites_PhilReg = DataBridge.sde_path + '\\GIS_PLANNING.Historic_Sites_PhilReg'
    Zoning_Overlays = DataBridge.sde_path + '\\GIS_PLANNING.Zoning_Overlays'
    Zoning_SteepSlopeProtectArea_r = DataBridge.sde_path + '\\GIS_PLANNING.Zoning_SteepSlopeProtectArea_r'
    GSI_SMP_TYPES = DataBridge.sde_path + '\\GIS_WATER.GSI_SMP_TYPES'
    GISLNI_Corner_Properties = GISLNI.sde_path + '\\GIS_LNI.PR_CORNER_PROPERTIES'
    DataBridge_Districts = DataBridge.sde_path + '\\GIS_LNI.LI_DISTRICTS'
    Council_Districts_2016 = DataBridge.sde_path + '\\GIS_PLANNING.Council_Districts_2016'
    PPR_Properties = DataBridge.sde_path + '\\GIS_PPR.PPR_Properties'
    Park_IDs = GISLNI.sde_path + '\\GIS_LNI.PR_PARK_NAME_IDS'

    # Internal data sources
    PWD_Parcels_Raw = 'PWDParcels_Raw'
    PWD_Parcels_Working = 'PWDParcels_Working'
    CornerProperties = 'Corner_Properties'
    PWD_PARCELS_SJ = 'PWD_PARCELS_Spatial_Join'
    CornerPropertiesSJ_P = 'CornerPropertiesSJ_P'
    Districts = 'Districts'
    Hist_Sites_PhilReg = 'Hist_Sites_PhilReg'
    Zon_Overlays = 'ZoningOverlays_'
    Zoning_SteepSlope = 'PCPC_SteepSlope'
    PWD_GSI_SMP_TYPES = 'PWD_GSI_SMP_TYPES'
    Zon_BaseDistricts = 'ZonBaseDistricts_'
    ArtCommission_BuildingIDSinageReview = 'ArtCommission_BuildingIDSinageReview'
    FloodPlain100Yr = 'PCPC_100YrFloodPlain'
    PCPC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PCPC_Intersect'
    PAC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PAC_Intersect'
    Flags_Table_Temp = 'Flags_Table_Temp'
    Council_Districts_Local = 'Districts_'
    Park_IDs_Local = 'ParkNameIDs_'
    PPR_Properties_Local = 'PPRProperties_'
    PPR_Properties_Temp_Pre_Dissolve = 'in_memory\\PPR_Properties_Temp_Pre_Dissolve'
    PPR_Properties_Temp = 'in_memory\\PPR_Properties_Temp'
    DORMismatchParcels = 'DORMismatchParcels'

    # LIGISDB Output FeatureClasses
    GIS_LNI_PR_PCPC_CityAveSiteReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_CityAveSiteReview'
    GIS_LNI_PR_PCPC_RidgeAveFacadeReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_RidgeAveFacadeReview'
    GIS_LNI_PR_PCPC_MasterPlanReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_MasterPlanReview'
    GIS_LNI_PR_PCPC_CenterCityFacadeReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_CenterCityFacadeReview'
    GIS_LNI_PR_PCPC_NeighborConsReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_NeighborConsReview'
    GIS_LNI_PR_PCPC_WissWaterSiteReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_WissWaterSiteReview'
    GIS_LNI_PR_PCPC_GtownMtAiryFacadeReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_GtownMtAiryFacReview'
    GIS_LNI_PR_PCPC_100YrFloodPlain = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_100YrFloodPlain'
    GIS_LNI_PR_PCPC_SteepSlope = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_SteepSlope'
    GIS_LNI_PR_PCPC_SkyPlaneReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_SkyPlaneReview'
    GIS_LNI_PR_PAC_BuildIDSignageReview = GISLNI.sde_path + '\\GIS_LNI.PR_PAC_BuildIDSignageReview'
    GIS_LNI_PR_PAC_ParkwayBufferReview = GISLNI.sde_path + '\\GIS_LNI.PR_PAC_ParkwayBufferReview'
    GIS_LNI_PR_PAC_SignageSpecialControl = GISLNI.sde_path + '\\GIS_LNI.PR_PAC_SinageSpecialControl'
    GIS_LNI_PR_PWD_GSI_Buffer = GISLNI.sde_path + '\\GIS_LNI.PR_PWD_GSI_Buffer'
    GIS_LNI_PR_PWD_GreenRoofReview = GISLNI.sde_path + '\\GIS_LNI.PR_PWD_GreenRoofReview'
    GIS_LNI_PR_PHC_HistoricalResReview = GISLNI.sde_path + '\\GIS_LNI.PR_PHC'
    GIS_LNI_PR_PCPC_DORMismatchParcels = GISLNI.sde_path + '\\GIS_LNI.DORMismatchParcels'

    PR_FLAG_SUMMARY = GISLNI.sde_path + '\\GIS_LNI.LI_PR_FLAG_SUMMARY'
    print('SUCCESS at Step 2')

    # Step 3A: Update Local Copies of DataBridge Files
    print('Updating Zoning Base Districts')
    if arcpy.Exists(Zon_BaseDistricts):
        arcpy.Delete_management(Zon_BaseDistricts)
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_BaseDistricts, localWorkspace, Zon_BaseDistricts)
    print('Updating Zoning Overlays')
    if arcpy.Exists(Zon_Overlays):
        arcpy.Delete_management(Zon_Overlays)
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_Overlays, localWorkspace, Zon_Overlays)
    print('Updating Council Districts')
    if arcpy.Exists(Council_Districts_Local):
        arcpy.Delete_management(Council_Districts_Local)
    arcpy.FeatureClassToFeatureClass_conversion(Council_Districts_2016, localWorkspace, Council_Districts_Local)
    print('Updating PWD Parcels')
    if arcpy.Exists(PWD_Parcels_Raw):
        arcpy.Delete_management(PWD_Parcels_Raw)
    arcpy.FeatureClassToFeatureClass_conversion(PWD_PARCELS_DataBridge, localWorkspace, PWD_Parcels_Raw)
    print('Updating PPR Properties')
    if arcpy.Exists(PPR_Properties_Local):
        arcpy.Delete_management(PPR_Properties_Local)
    # you need to apply the where clause so you only capture the parent feature of families of PPR_Property features
    arcpy.FeatureClassToFeatureClass_conversion(PPR_Properties, localWorkspace, PPR_Properties_Local, where_clause="NESTED = 'N'")

    print('updated feature classes')
    logging.info('updated feature classes')

    # Step 3B: Merge Parks with Parcels
    # Determine if parks have been added yet
    tCursor = arcpy.da.SearchCursor(PWD_Parcels_Raw, 'PARCELID')
    print('Identifying Lowest Parcel ID')
    isNeg = min([int(row[0]) for row in tCursor])
    del tCursor
    if isNeg > 0:
        logging.info('Adding new park data')
        print('Adding new park data')
        cursor1 = arcpy.da.SearchCursor(Park_IDs, ['PARENT_NAME', 'LI_TEMP_ID', 'CHILD_OF', 'DPP_ASSET_ID'])
        parkDict = {row[0]: row[1:4] for row in cursor1}
        del cursor1
        minID = min([v for v in parkDict.values()])[0]
        print('Dissolving Parks Polygons')
        arcpy.Dissolve_management(PPR_Properties_Local, PPR_Properties_Temp, ['PARENT_NAME', 'DPP_ASSET_ID'])

        # The IDs are negative so we're looking for the next LOWEST value to add
        cursor2 = arcpy.da.SearchCursor(PPR_Properties_Temp, ['PARENT_NAME', 'DPP_ASSET_ID'])
        cursor2b = arcpy.da.InsertCursor(Park_IDs, ['PARENT_NAME', 'LI_TEMP_ID', 'DPP_ASSET_ID'])
        noChange = True
        edit = arcpy.da.Editor(editDB)
        try:
            edit.startEditing(False, True)
            edit.startOperation()
        except:
            pass
        for row in cursor2:
            if row[0] not in parkDict:
                noChange = False
                minID -= 1
                cursor2b.insertRow([row[0], minID, row[1]])
        del cursor2
        del cursor2b
        try:
            edit.stopOperation()
            edit.stopEditing(True)
        except:
            pass

        print('Adding and calculating geometry')
        arcpy.AddGeometryAttributes_management(PPR_Properties_Temp, 'AREA', Area_Unit='SQUARE_FEET_US')
        arcpy.AddField_management(PPR_Properties_Temp, 'PARCEL_AREA', 'LONG')
        # arcpy.CalculateField_management(PPR_Assets_Temp, 'PARCEL_AREA', '!POLY_AREA!', 'PYTHON')
        arcpy.CalculateField_management(PPR_Properties_Temp, 'PARCEL_AREA', '!POLY_AREA!', 'PYTHON3')


        # Join Park IDs to Temp Parks Layer
        arcpy.JoinField_management(PPR_Properties_Temp, 'PARENT_NAME', Park_IDs, 'PARENT_NAME', ['LI_TEMP_ID'])

        # Map Fields for Append
        fms = arcpy.FieldMappings()
        fm_ID = arcpy.FieldMap()
        fm_ID.addInputField(PPR_Properties_Temp, 'LI_TEMP_ID')
        fm_ID_Out = fm_ID.outputField
        fm_ID_Out.name = 'PARCELID'
        fm_ID.outputField = fm_ID_Out
        fm_Area = arcpy.FieldMap()
        fm_Area.addInputField(PPR_Properties_Temp, 'PARCEL_AREA')
        fm_Area_Out = fm_Area.outputField
        fm_Area_Out.name = 'GROSS_AREA'
        fm_Area.outputField = fm_Area_Out
        fms.addFieldMap(fm_ID)
        fms.addFieldMap(fm_Area)
        arcpy.Append_management(PPR_Properties_Temp, PWD_Parcels_Raw, schema_type='NO_TEST', field_mapping=fms)

    print('Copying Corner Properties Local')
    arcpy.FeatureClassToFeatureClass_conversion(GISLNI_Corner_Properties, localWorkspace, CornerProperties)
    print('Copying Districts Local')
    arcpy.FeatureClassToFeatureClass_conversion(DataBridge_Districts, localWorkspace, Districts)
    print('Spatial Joining Parcels and Districts')
    # Creates District Field in Parcel FC
    arcpy.SpatialJoin_analysis(PWD_Parcels_Raw, Districts, PWD_PARCELS_SJ)
    print('Converting Corner Properties to Points')
    # Create 'corner' field in parcel FC when the parcel contains the corner polygon centroid
    arcpy.FeatureToPoint_management(CornerProperties, CornerPropertiesSJ_P, 'INSIDE')
    print('Creating Corner Field')
    arcpy.AddField_management(CornerPropertiesSJ_P, 'Corner', 'SHORT')
    arcpy.CalculateField_management(CornerPropertiesSJ_P, 'Corner', '1', 'PYTHON3')
    arcpy.Delete_management(CornerProperties)
    arcpy.Delete_management(PWD_Parcels_Raw)
    arcpy.Delete_management(Districts)
    print('Spatial Join Parcels and Corner Properties')
    arcpy.SpatialJoin_analysis(PWD_PARCELS_SJ, CornerPropertiesSJ_P, PWD_Parcels_Working)
    arcpy.Delete_management(CornerPropertiesSJ_P)
    arcpy.Delete_management(PWD_PARCELS_SJ)
    print('SUCCESS at Step 3')

    # Step 3C: Create plan review feature classes

    print('Copying Overlays local')
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_SteepSlopeProtectArea_r, localWorkspace, Zoning_SteepSlope)
    arcpy.FeatureClassToFeatureClass_conversion(GSI_SMP_TYPES, localWorkspace, PWD_GSI_SMP_TYPES,
                                                where_clause="OWNER IN ('PPRPWDMAINT', 'PRIVPWDMAINT', 'PWD')")

    print('Adding Corner properties to dictionary')
    cornerPropertyCursor = arcpy.da.SearchCursor(PWD_Parcels_Working,
                                                 ['PARCELID', 'ADDRESS', 'GROSS_AREA', 'DISTRICT', 'Corner'])
    parcelDict = {}
    for parcel in cornerPropertyCursor:
        if parcel[4] == 1:
            parcelDict[parcel[0]] = {'Address': parcel[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [],
                                     'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': 1, 'ParcelArea': parcel[2],
                                     'BaseZoning': [], 'OverlayZoning': [], 'District': parcel[3]}
        else:
            parcelDict[parcel[0]] = {'Address': parcel[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [],
                                     'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': 0, 'ParcelArea': parcel[2],
                                     'BaseZoning': [], 'OverlayZoning': [], 'District': parcel[3]}

    del cornerPropertyCursor


    # Function that will be used later to create plan review feature classes by selecting certain data from
    # the overlays
    def parcelFlag(reviewName, reviewType, sourceFC, fieldCalculation, whereClause, outputFC, localWorkspace, parcels,
                   parcelDict):
        try:
            sourceFC = localWorkspace + '\\' + sourceFC if '.sde' not in sourceFC else sourceFC
            DORsourceFC = DORinputGDB + '\\' + sourceFC
            IntersectOutput = localWorkspace + '\\' + reviewName + '_intersect'
            reviewLayer = reviewType + '_' + reviewName
            reviewField = 'CODE' if reviewType == zonB else 'OVERLAY_NAME' if reviewType == zonO else reviewName + 'ReviewReason'

            if '_Buffer' in reviewName:
                print('Buffering')
                arcpy.Buffer_analysis(sourceFC, reviewLayer, '50 Feet')
            elif 'DOR' in reviewName:
                print('Creating Local FC for ' + reviewName)
                arcpy.FeatureClassToFeatureClass_conversion(DORsourceFC, DORinputGDB, reviewLayer,
                                                            whereClause)
            else:
                print('Creating Local FC for ' + reviewName)
                arcpy.FeatureClassToFeatureClass_conversion(sourceFC, localWorkspace, reviewLayer,
                                                            whereClause)

            # All FCs except for Zoning are copied to LIGISDB
            if outputFC:
                print('Copying FC to GISLNI')
                arcpy.AddField_management(reviewLayer, reviewField, 'TEXT')
                arcpy.CalculateField_management(reviewLayer, reviewField, fieldCalculation, 'PYTHON3')
                arcpy.AddField_management(reviewLayer, 'REVIEW_TYPE', 'TEXT', field_length=2000)
                arcpy.CalculateField_management(reviewLayer, 'REVIEW_TYPE', '"' + reviewName + '"', 'PYTHON3')
                arcpy.DeleteRows_management(outputFC)
                arcpy.Append_management(reviewLayer, outputFC, 'NO_TEST')

            print('Performing Intersect')
            # Create polygons where review polygons overlap with parcels
            arcpy.Intersect_analysis([parcels] + [reviewLayer], IntersectOutput, 'ALL')
            print('Intersect Complete')

            arcpy.Delete_management(reviewLayer)

            # To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
            actualFields = [f.name for f in arcpy.ListFields(IntersectOutput)]
            arcpy.AddField_management(IntersectOutput, 'ThinessRatio', 'FLOAT')
            # NOTE Thiness calculation was removed by request, this is designed remove small overlaps in zoning from adjacent parcels
            arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
            """
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
                # Only polygons with a thiness ratio of over 0.3 and a parcel coverage of more than 3% are included in analysis
                if row[1] != '' and row[1] is not None and row[7] != '' and (
                        row[5] / float(row[4])) > 0.01:  # 0.03  # and row[6] >  0.3 :
                    # If parcel has not made it into dictionary, parcel gets a new entry added
                    if row[0] not in parcelDict and reviewType != zonB and reviewType != zonO:
                        tempDict = {'Address': row[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [],
                                    'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': row[3], 'ParcelArea': row[4],
                                    'BaseZoning': [], 'OverlayZoning': [], 'District': row[2]}
                        tempDict[reviewType] = [row[7]]
                        if fieldCalculation == '"100 Year Flood Plain"':
                            tempDict['Floodplain'] = 1
                        if fieldCalculation == '"Steep Slope"':
                            tempDict['SteepSlope'] = 1
                        parcelDict[row[0]] = tempDict
                    # If parcel already exists, its current dictionary entry is appended with new review information
                    elif row[0] in parcelDict:
                        tempDict = parcelDict.get(row[0])
                        oldList = tempDict.get(reviewType)
                        # The set function removes all duplicates from list
                        tempDict[reviewType] = list(set([row[7]] + oldList))
                        if fieldCalculation == '"100 Year Flood Plain"':
                            tempDict['Floodplain'] = 1
                        if fieldCalculation == '"Steep Slope"':
                            tempDict['SteepSlope'] = 1
                        parcelDict[row[0]] = tempDict

            arcpy.Delete_management(IntersectOutput)

            return parcelDict

        except:
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
            arcpy.AddError(pymsg)
            log.error(pymsg)
            sys.exit(1)


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
    PCPC_GermantownMtAirySubareaFacadeReview = ['GermantownAveMtAiryFaçReview', pcpcR, Zon_Overlays, '!Overlay_Name!',
                                           "Overlay_Name IN('/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue - Mount Airy Subarea')", GIS_LNI_PR_PCPC_GtownMtAiryFacadeReview]
    PCPC_DOR_Mismatch_Review = ['DORMismatchReview', pcpcR, DORMismatchParcels, '"DOR Mismatch Review"', None, GIS_LNI_PR_PCPC_DORMismatchParcels]
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
                                "Overlay_Name IN('/CTR Center City Overlay District - Rittenhouse Square','/CTR Center City Overlay District - Center City Commercial Area','/CTR Center City Overlay District - Convention Center Area','/CTR Center City Overlay District - Independence Hall Area','/CTR Center City Overlay District - Vine Street Area','/CTR Center City Overlay District - Washington Square','/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood','/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue','/NCA Neighborhood Commercial Area Overlay District - Main Street/Manayunk and Venice Island','/NCA Neighborhood Commercial Area Overlay District - Logan Triangle','/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue','/NCA Neighborhood Commercial Area Overlay District - Lower and Central Germantown','/NCA Neighborhood Commercial Area Overlay District - North Delaware Avenue','/NCA Neighborhood Commercial Area Overlay District - Spring Garden','Accessory Sign Controls - Special Controls for Cobbs Creek, Roosevelt Boulevard, and Department of Parks and Recreation Land', '/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue - Mount Airy Subarea')",
                                GIS_LNI_PR_PAC_SignageSpecialControl]
    PHC_HistoricalResReview = ['HistoricalResReview', phcR, Historic_Sites_PhilReg, '"Historic Designation"', None,
                               GIS_LNI_PR_PHC_HistoricalResReview]
    PWD_GreenRoofReview = ['GreenRoofReview', pwdR, PWD_GSI_SMP_TYPES, '"GREEN ROOF"', "SUBTYPE IN( 10 )",
                           GIS_LNI_PR_PWD_GreenRoofReview]
    PWD_GSI_Buffer = ['GSI_Buffer', pwdR, PWD_GSI_SMP_TYPES, '"Green Infrastructure"', None, GIS_LNI_PR_PWD_GSI_Buffer]

    # List to iterate inputs through parcel flag function
    reviewList = [PCPC_CityAveSiteReview, PCPC_RidgeAveFacadeReview, PCPC_MasterPlanReview, PCPC_CenterCityFacadeReview,
                  PCPC_NeighborConsReview,
                  PCPC_WissahickonWatershedSiteReview, PCPC_GermantownMtAirySubareaFacadeReview, PCPC_DOR_Mismatch_Review, PCPC_100YrFloodPlain, PCPC_SteepSlope, PCPC_SkyPlaneReview,
                  PAC_BuildIDSignageReview,
                  PAC_ParkwayBufferReview, PAC_SinageSpecialControl, PHC_HistoricalResReview, PWD_GreenRoofReview,
                  PWD_GSI_Buffer]
    #reviewList = [PHC_HistoricalResReview]


    # Call the parcelFlag function on each plan review input in order to create the plan review feature classes
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
        arcpy.MakeFeatureLayer_management(localWorkspace + '\\' + Council_Districts_Local, currentTract,
                                          "DISTRICT = '" + tract[0] + "'")
        arcpy.Clip_analysis(localWorkspace + '\\' + PWD_Parcels_Working, currentTract, tempParcels)
        for r in reviewList:
            print('Beginning ' + r[0])
            inputs = tuple(r[:] + [localWorkspace, tempParcels, parcelDict])
            parcelFlag(*inputs)

    # Add remaining parcels to table
    remainingCursor = arcpy.da.SearchCursor(PWD_Parcels_Working,
                                            ['PARCELID', 'ADDRESS', 'DISTRICT', 'Corner', 'GROSS_AREA'])
    print('Adding remaining parcels to dictionary')
    for row in remainingCursor:
        if row[0] not in parcelDict:
            parcelDict[row[0]] = {'Address': row[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [],
                                  'SteepSlope': 0,
                                  'Floodplain': 0, 'CornerProp': row[3], 'ParcelArea': row[4], 'BaseZoning': [],
                                  'OverlayZoning': [], 'District': row[2]}
    del remainingCursor

    # Update Flags Table
    arcpy.CreateTable_management(localWorkspace, Flags_Table_Temp, PR_FLAG_SUMMARY)
    # ParcelDict Schema: {PWD_PARCELID:{Address:'', PAC:[], PCPC:[], PHC:[], PWD:[], 'SteepSlope':bool, 'Floodplain':bool, CornerProp:bool, ParcelArea:'', BaseZoning:[], OverlayZoning:[], LIDistrict:''}
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
    for k, v in parcelDict.items():
        count += 1
        if count in breaks:
            arcpy.AddMessage('Creation of Table Rows ' + str(int(round(count * 100.0 / countin))) + '% complete...')
        parcelID = str(k)
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
        flagCursor.insertRow(
            [address, parcelID, pacBool, pac, pcpcBool, pcpc, phcBool, phc, pwdBool, pwd, corner, area, district, flood,
             slope])

    log.info('PR Flags Part 1 complete')

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    arcpy.AddError(pymsg)
    log.error(pymsg)

    import smtplib
    from email.mime.text import MIMEText
    from phila_mail import server

    sender = 'LIGISTeam@phila.gov'
    recipientslist = ['DANI.INTERRANTE@PHILA.GOV', 'daniel.whaland@phila.gov', 'bailey.glover@Phila.gov',
                      'LIGISTeam@phila.gov']
    commaspace = ', '
    msg = MIMEText('AUTOMATIC EMAIL \n Plan Review Flags Update Failed during update: \n' + pymsg)
    msg['To'] = commaspace.join(recipientslist)
    msg['From'] = sender
    msg['X-Priority'] = '2'
    msg['Subject'] = 'Plan Review Flags Table Update Failure'
    server.server.sendmail(sender, recipientslist, msg.as_string())
    server.server.quit()
    sys.exit(1)