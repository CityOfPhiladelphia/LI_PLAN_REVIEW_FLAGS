"""
Note:
This script was originally designed to create a table listing every pwd parcel in the city and related attributes.
The need for this list has since been scraped but there is still a need for the PR GIS layers created in this script.
Much of the process has been commented out but left in place in case the need for this ever returns
"""

import arcpy
import sys
import traceback

arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'in_memory'
workspace= arcpy.env.workspace
print('''Starting script 'PermitReviewScripts.py'...''')


#TODO Check parameters for what is considered a corner property

# Step 1: Configure log file
try:
    '''
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
    '''
except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    arcpy.AddError(pymsg)
    sys.exit(1)

# Step 2: Set script parameters
try:
    print('Step 2: Setting script parameters...')
    # External data sources
    PWD_PARCELS_DataBridge = 'Database Connections\\DataBridge.sde\\GIS_WATER.PWD_PARCELS'
    Zoning_BaseDistricts = 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_BaseDistricts'
    FEMA_100_flood_Plain= 'Database Connections\\DataBridge.sde\\GIS_PLANNING.FEMA_100_flood_Plain'
    Historic_Sites_PhilReg= 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Historic_Sites_PhilReg'
    Zoning_Overlays= 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_Overlays'
    Zoning_SteepSlopeProtectArea_r= 'Database Connections\\DataBridge.sde\\GIS_PLANNING.Zoning_SteepSlopeProtectArea_r'
    GSI_SMP_TYPES= 'Database Connections\\DataBridge.sde\\GIS_WATER.GSI_SMP_TYPES'
    GISLNI_Corner_Properties = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_CORNER_PROPERTIES'
    GISLNI_Districts = 'Database Connections\\GISLNI.sde\\GIS_LNI.DISTRICTS_BROAD'

    # Internal data sources
    PWD_Parcels = 'PWD_Parcels'
    PWD_Spatial_Join = 'PWD_Spatial_Join'
    CornerProperties = 'Corner_Properties'
    PWD_PARCELS_SJ = 'PWD_PARCELS_Spatial_Join'
    CornerPropertiesSJ_P = 'CornerPropertiesSJ_P'
    Districts = 'Districts'
    Hist_Sites_PhilReg = 'Hist_Sites_PhilReg'
    Zon_Overlays = 'R_Zoning_Overlays'
    Zoning_SteepSlope = 'PCPC_SteepSlope'
    PWD_GSI_SMP_TYPES = 'PWD_GSI_SMP_TYPES'
    Zon_BaseDistricts = 'Zon_BaseDistricts'
    ArtCommission_BuildingIDSinageReview= 'ArtCommission_BuildingIDSinageReview'
    FloodPlain100Yr = 'PCPC_100YrFloodPlain'
    PCPC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PCPC_Intersect'
    PAC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PAC_Intersect'
    Flags_Table_Temp = 'Flags_Table_Temp'

    #LIGISDB Output FeatureClasses
    PR_PCPC_CityAveSiteReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_CityAveSiteReview'
    PR_PCPC_RidgeAveFacadeReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_RidgeAveFacadeReview'
    PR_PCPC_MasterPlanReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_MasterPlanReview'
    PR_PCPC_CenterCityFacadeReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_CenterCityFacadeReview'
    PR_PCPC_NeighborConsReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_NeighborConsReview'
    PR_PCPC_WissWaterSiteReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_WissWaterSiteReview'
    PR_PCPC_100YrFloodPlain = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_100YrFloodPlain'
    PR_PCPC_SteepSlope = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_SteepSlope'
    PR_PCPC_SkyPlaneReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC_SkyPlaneReview'
    PR_PAC_BuildIDSignageReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC_BuildIDSignageReview'
    PR_PAC_ParkwayBufferReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC_ParkwayBufferReview'
    PR_PAC_SinageSpecialControl = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC_SinageSpecialControl'
    PR_PWD_GSI_Buffer = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PWD_GSI_Buffer'
    PR_PWD_GreenRoofReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PWD_GreenRoofReview'
    PR_PHC_HistoricalResReview = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PHC'

    PR_FLAG_SUMMARY = 'Database Connections\\GISLNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY'
    print('SUCCESS at Step 2')

    """
    #Step 3A: Build Initial PWD Spatial Join Data
    print('Building parcel layer..')

    print('Copying PWD Parcels Local')
    arcpy.FeatureClassToFeatureClass_conversion(PWD_PARCELS_DataBridge, workspace, PWD_Parcels)
    print('Copying Corner Properties Local')
    arcpy.FeatureClassToFeatureClass_conversion(GISLNI_Corner_Properties, workspace, CornerProperties)
    print('Copying Districts Local')
    arcpy.FeatureClassToFeatureClass_conversion(GISLNI_Districts, workspace, Districts)
    print ('Spatial Joining Parcels and Districts')
    #Creates District Field in Parcel FC
    arcpy.SpatialJoin_analysis(PWD_Parcels, Districts, PWD_PARCELS_SJ)
    print('Converting Corner Properties to Points')
    #Create 'corner' field in parcel FC when the parcel contains the corner polygon centroid
    arcpy.FeatureToPoint_management(CornerProperties, CornerPropertiesSJ_P, 'INSIDE')
    print('Creating Corner Field')
    arcpy.AddField_management(CornerPropertiesSJ_P, 'Corner', 'SHORT')
    arcpy.CalculateField_management(CornerPropertiesSJ_P, 'Corner', '1')
    arcpy.Delete_management(CornerProperties)
    arcpy.Delete_management(PWD_Parcels)
    arcpy.Delete_management(Districts)
    print('Spatial Joing Parcels and Corner Properties')
    arcpy.SpatialJoin_analysis(PWD_PARCELS_SJ, CornerPropertiesSJ_P, PWD_Spatial_Join)
    arcpy.Delete_management(CornerPropertiesSJ_P)
    arcpy.Delete_management(PWD_PARCELS_SJ)
    print('SUCCESS at Step 3')
    ############################################################################################################
    """
    #SECTION 2: Build and collect PCPC Data
    print('Copying Overlays local')
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_BaseDistricts, workspace, Zon_BaseDistricts)
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_Overlays, workspace, Zon_Overlays)
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_SteepSlopeProtectArea_r, workspace, Zoning_SteepSlope)
    arcpy.FeatureClassToFeatureClass_conversion(GSI_SMP_TYPES, workspace, PWD_GSI_SMP_TYPES)
    """

    print('Adding Corner properties to dictionary')
    cornerPropertyCursor = arcpy.da.SearchCursor(PWD_Spatial_Join, ['PARCELID', 'ADDRESS', 'GROSS_AREA', 'DISTRICT', 'Corner'] )
    parcelDict = {}
    for parcel in cornerPropertyCursor:
        if parcel[4] == 1:
            parcelDict[parcel[0]] = {'Address': parcel[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [], 'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': 1, 'ParcelArea': parcel[2], 'BaseZoning': [], 'OverlayZoning': [], 'District': parcel[3]}
        else:
            parcelDict[parcel[0]] = {'Address': parcel[1], 'PAC': [], 'PCPC': [], 'TempPCPC': [], 'PHC': [], 'PWD': [], 'SteepSlope': 0, 'Floodplain': 0, 'CornerProp': 0, 'ParcelArea': parcel[2], 'BaseZoning': [], 'OverlayZoning': [], 'District': parcel[3]}

    del cornerPropertyCursor

    """
    #Run each review type through parcel flag function. This populates a dictionary that will eventually populate final table
    def parcelFlag(reviewName, reviewType, sourceFC, fieldCalculation, whereClause, outputFC, workspace, parcels,
                   parcelDict):
        reviewLayer = reviewType + '_' + reviewName
        IntersectOutput = workspace + '\\' + reviewName + 'Intersect'
        reviewField = 'CODE' if reviewType == zonB else 'OVERLAY_NAME' if reviewType == zonO else reviewName + 'ReviewReason'
        print reviewField

        if '_Buffer' in reviewName:
            print('Buffering')
            arcpy.Buffer_analysis(sourceFC, reviewLayer, '500 Feet')
        else:
            print('Creating Local FC for ' + reviewName)
            arcpy.FeatureClassToFeatureClass_conversion(sourceFC, workspace, reviewLayer,
                                                    whereClause)

        #All FCs except for Zoning are copied to LIGISDB
        if outputFC:
            print('Copying FC to GISLNI')
            arcpy.AddField_management(reviewLayer, reviewField, 'TEXT')
            arcpy.CalculateField_management(reviewLayer, reviewField, fieldCalculation)
            arcpy.DeleteRows_management(outputFC)
            arcpy.Append_management(reviewLayer, outputFC, 'NO_TEST')
        """
        print('Performing Intersect')
        #Create polygons where review polygons overlap with parcels
        arcpy.Intersect_analysis([parcels]+[reviewLayer], IntersectOutput, 'ALL')
        print('Intersect Complete')
        """
        arcpy.Delete_management(reviewLayer)
        """
        #To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
        actualFields = [f.name for f in arcpy.ListFields(IntersectOutput)]
        print actualFields
        arcpy.AddField_management(IntersectOutput, 'ThinessRatio', 'FLOAT')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
        arcpy.CalculateField_management(IntersectOutput, 'ThinessRatio',
                                        "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')

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
        """
        return parcelDict



    #Overlay Input Schema = [temp layer name, review type, source layer, field calculation, where clause, LIGISDB Layer]
    #Flag Types
    pcpcR = 'PCPC'
    pacR = 'PAC'
    pwdR = 'PWD'
    phcR = 'PHC'
    zonB = 'BaseZoning'
    zonO = 'OverlayZoning'


    #Review inputs
    PCPC_CityAveSiteReview = ['CityAveSiteReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                              "Overlay_Name IN('/CAO City Avenue Overlay District - City Avenue Regional Center Area','/CAO City Avenue Overlay District - City Avenue Village Center Area')",
                              PR_PCPC_CityAveSiteReview]
    PCPC_RidgeAveFacadeReview = ['RidgeAveFacadeReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                                 "Overlay_Name IN('/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue')",
                                 PR_PCPC_RidgeAveFacadeReview]
    PCPC_MasterPlanReview = ['MasterPlanReview', pcpcR, Zon_BaseDistricts, '[Long_Code]',
                             "Long_Code IN('RMX-1', 'RMX-2', 'SP-ENT', 'SP-INS', 'SP-STA')", PR_PCPC_MasterPlanReview]
    PCPC_CenterCityFacadeReview = ['CenterCityFacadeReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                                   "Overlay_Name IN('/CTR Center City Overlay District - Chestnut and Walnut Street Area', '/CTR Center City Overlay District - Broad Street Area South','/CTR Center City Overlay District - Market Street Area East')",
                                   PR_PCPC_CenterCityFacadeReview]
    PCPC_NeighborConsReview = ['NeighborConsReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                               "Overlay_Name IN('/NCO Neighborhood Conservation Overlay District - Central Roxborough','/NCO Neighborhood Conservation Overlay District - Overbrook Farms','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2','/NCO Neighborhood Conservation Overlay District - Queen Village','/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough')",
                               PR_PCPC_NeighborConsReview]
    PCPC_WissahickonWatershedSiteReview = ['WissahickonWatershedSiteReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                                           "Overlay_Name IN('/NCO Neighborhood Conservation Overlay District - Central Roxborough','/NCO Neighborhood Conservation Overlay District - Overbrook Farms','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2','/NCO Neighborhood Conservation Overlay District - Queen Village','/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough')",
                                           PR_PCPC_WissWaterSiteReview]
    PCPC_100YrFloodPlain = ['FloodPlainReview', pcpcR, FEMA_100_flood_Plain,  '"100 Year Flood Plain"', None,
                            PR_PCPC_100YrFloodPlain]
    PCPC_SteepSlope = ['SteepSlopeReview', pcpcR, Zoning_SteepSlopeProtectArea_r,  '"Steep Slope"', None, PR_PCPC_SteepSlope]
    PCPC_SkyPlaneReview = ['SkyPlaneReview', pcpcR, Zon_BaseDistricts, '[Long_Code]', "Long_Code IN('CMX-4','CMX-5')",
                           PR_PCPC_SkyPlaneReview]
    PAC_BuildIDSignageReview = ['BuildIDSignageReview', pacR, Zon_BaseDistricts, '[LONG_CODE]',
                                "Long_Code IN('ICMX', 'I-1', 'IRMX')", PR_PAC_BuildIDSignageReview]
    PAC_ParkwayBufferReview = ['ParkwayBufferReview', pacR, Zon_Overlays, '[Overlay_Name]',
                               "Overlay_Name IN('/CTR Center City Overlay District - Parkway Buffer')",
                               PR_PAC_ParkwayBufferReview]
    PAC_SinageSpecialControl = ['SinageSpecialControl', pacR, Zon_Overlays, '[Overlay_Name]',
                                "Overlay_Name IN('/CTR Center City Overlay District - Rittenhouse Square','/CTR Center City Overlay District - Center City Commercial Area','/CTR Center City Overlay District - Convention Center Area','/CTR Center City Overlay District - Independence Hall Area','/CTR Center City Overlay District - Vine Street Area','/CTR Center City Overlay District - Washington Square','/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood','/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue','/NCA Neighborhood Commercial Area Overlay District - Main Street/Manayunk and Venice Island','/NCA Neighborhood Commercial Area Overlay District - Logan Triangle','/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue','/NCA Neighborhood Commercial Area Overlay District - Lower and Central Germantown','/NCA Neighborhood Commercial Area Overlay District - North Delaware Avenue','/NCA Neighborhood Commercial Area Overlay District - Spring Garden','Accessory Sign Controls - Special Controls for Cobbs Creek, Roosevelt Boulevard, and Department of Parks and Recreation Land')",
                                PR_PAC_SinageSpecialControl]
    PHC_HistoricalResReview = ['HistoricalResReview', phcR, Historic_Sites_PhilReg,  '"Historic Designation"', None, PR_PHC_HistoricalResReview]
    PWD_GreenRoofReview = ['GreenRoofReview', pwdR, PWD_GSI_SMP_TYPES, '[SUBTYPE] &"-GREEN ROOF"', "SUBTYPE IN( 10 )", PR_PWD_GreenRoofReview]
    PWD_GSI_Buffer = ['GSI_Buffer', pwdR, PWD_GSI_SMP_TYPES, '"Green Infrastructure"', None, PR_PWD_GSI_Buffer]


    #List to iterate inputs through parcel flag function
    reviewList = [PCPC_CityAveSiteReview, PCPC_RidgeAveFacadeReview, PCPC_MasterPlanReview, PCPC_CenterCityFacadeReview, PCPC_NeighborConsReview,
                  PCPC_WissahickonWatershedSiteReview, PCPC_100YrFloodPlain, PCPC_SteepSlope, PCPC_SkyPlaneReview, PAC_BuildIDSignageReview,
                  PAC_ParkwayBufferReview, PAC_SinageSpecialControl, PHC_HistoricalResReview, PWD_GreenRoofReview, PWD_GSI_Buffer]

    #Set fake variable to by-pass lack of parcel creation
    parcelDict = {}

    #Back to original script
    for r in reviewList:
        print('Beginning ' + r[0])
        inputs = tuple(r[:] + [workspace, PWD_Spatial_Join, parcelDict])
        parcelFlag(*inputs)
    """

    #Step 20: Update Flags Table
    arcpy.CreateTable_management(workspace, Flags_Table_Temp, PR_FLAG_SUMMARY)
    #ParcelDict Schema: {PWD_PARCELID:{Address:'', PAC:[], PCPC:[], PHC:[], PWD:[], 'SteepSlope':bool, 'Floodplain':bool, CornerProp:bool, ParcelArea:'', BaseZoning:[], OverlayZoning:[], LIDistrict:''}
    PR_FLAG_SUMMARY = 'Database Connections\\GISLNI.sde\\GIS_LNI.PR_FLAG_SUMMARY'
    flagFields = [f.name for f in arcpy.ListFields('in_memory\\Flags_Table_Temp')]
    del flagFields[flagFields.index('OBJECTID')]
    del flagFields[flagFields.index('BASE_ZONING')]
    del flagFields[flagFields.index('OVERLAY_ZONING')]
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
    arcpy.TruncateTable_management(PR_FLAG_SUMMARY)
    print('Copying to GISLNI')
    arcpy.Append_management(Flags_Table_Temp, PR_FLAG_SUMMARY, 'NO_TEST')
    print('Copy Complete')
    """

    #Merge Into Feature Service Layers



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


