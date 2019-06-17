"""
Note:
This script was originally designed to create a table listing every pwd parcel in the city and related attributes.
The need for this list has since been scraped but there is still a need for the PR GIS layers created in this script.
Much of the process has been commented out but left in place in case the need for this ever returns
"""

import sys
import traceback

import arcpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = 'in_memory'
workspace = arcpy.env.workspace
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

try:
    # Step 2: Set script parameters
    print('Step 2: Setting script parameters...')
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
    ArtCommission_BuildingIDSinageReview = 'ArtCommission_BuildingIDSinageReview'
    FloodPlain100Yr = 'PCPC_100YrFloodPlain'
    PCPC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PCPC_Intersect'
    PAC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PAC_Intersect'
    Flags_Table_Temp = 'Flags_Table_Temp'

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

    PR_FLAG_SUMMARY = 'Database Connections\\GISLNI.sde\\GIS_LNI.LI_PR_FLAG_SUMMARY'
    print('SUCCESS at Step 2')

    # Step 3: Create plan review feature classes

    print('Copying Overlays local')
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_BaseDistricts, workspace, Zon_BaseDistricts)
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_Overlays, workspace, Zon_Overlays)
    arcpy.FeatureClassToFeatureClass_conversion(Zoning_SteepSlopeProtectArea_r, workspace, Zoning_SteepSlope)
    arcpy.FeatureClassToFeatureClass_conversion(GSI_SMP_TYPES, workspace, PWD_GSI_SMP_TYPES)


    # Function that will be used later to create plan review feature classes by selecting certain data from
    # the overlays
    def parcelFlag(reviewName, reviewType, sourceFC, fieldCalculation, whereClause, outputFC, workspace, parcels,
                   parcelDict):
        reviewLayer = reviewType + '_' + reviewName
        reviewField = 'CODE' if reviewType == zonB else 'OVERLAY_NAME' if reviewType == zonO else reviewName + 'ReviewReason'
        print reviewField

        if '_Buffer' in reviewName:
            print('Buffering')
            arcpy.Buffer_analysis(sourceFC, reviewLayer, '500 Feet')
        else:
            print('Creating Local FC for ' + reviewName)
            arcpy.FeatureClassToFeatureClass_conversion(sourceFC, workspace, reviewLayer,
                                                        whereClause)

        # All FCs except for Zoning are copied to LIGISDB
        if outputFC:
            print('Copying FC to GISLNI')
            arcpy.AddField_management(reviewLayer, reviewField, 'TEXT')
            arcpy.CalculateField_management(reviewLayer, reviewField, fieldCalculation)
            arcpy.AddField_management(reviewLayer, 'REVIEW_TYPE', 'TEXT', field_length=2000)
            arcpy.CalculateField_management(reviewLayer, 'REVIEW_TYPE', '"' + reviewName + '"')
            arcpy.DeleteRows_management(outputFC)
            arcpy.Append_management(reviewLayer, outputFC, 'NO_TEST')

        arcpy.Delete_management(reviewLayer)

        return parcelDict


    # Plan review flag types
    pcpcR = 'PCPC'
    pacR = 'PAC'
    pwdR = 'PWD'
    phcR = 'PHC'
    zonB = 'BaseZoning'
    zonO = 'OverlayZoning'

    # Inputs to be run through parcelFlag function in order to create the plan review feature classes
    PCPC_CityAveSiteReview = ['CityAveSiteReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                              "Overlay_Name IN('/CAO City Avenue Overlay District - City Avenue Regional Center Area','/CAO City Avenue Overlay District - City Avenue Village Center Area')",
                              GIS_LNI_PR_PCPC_CityAveSiteReview]
    PCPC_RidgeAveFacadeReview = ['RidgeAveFacadeReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                                 "Overlay_Name IN('/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue')",
                                 GIS_LNI_PR_PCPC_RidgeAveFacadeReview]
    PCPC_MasterPlanReview = ['MasterPlanReview', pcpcR, Zon_BaseDistricts, '[Long_Code]',
                             "Long_Code IN('RMX-1', 'RMX-2', 'SP-ENT', 'SP-INS', 'SP-STA')",
                             GIS_LNI_PR_PCPC_MasterPlanReview]
    PCPC_CenterCityFacadeReview = ['CenterCityFacadeReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                                   "Overlay_Name IN('/CTR Center City Overlay District - Chestnut and Walnut Street Area', '/CTR Center City Overlay District - Broad Street Area South','/CTR Center City Overlay District - Market Street Area East')",
                                   GIS_LNI_PR_PCPC_CenterCityFacadeReview]
    PCPC_NeighborConsReview = ['NeighborConsReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                               "Overlay_Name IN('/NCO Neighborhood Conservation Overlay District - Central Roxborough','/NCO Neighborhood Conservation Overlay District - Overbrook Farms','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2','/NCO Neighborhood Conservation Overlay District - Queen Village','/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough')",
                               GIS_LNI_PR_PCPC_NeighborConsReview]
    PCPC_WissahickonWatershedSiteReview = ['WissahickonWatershedSiteReview', pcpcR, Zon_Overlays, '[Overlay_Name]',
                                           "Overlay_Name IN('/WWO Wissahickon Watershed Overlay District')",
                                           GIS_LNI_PR_PCPC_WissWaterSiteReview]
    PCPC_100YrFloodPlain = ['FloodPlainReview', pcpcR, FEMA_100_flood_Plain, '"100 Year Flood Plain"', None,
                            GIS_LNI_PR_PCPC_100YrFloodPlain]
    PCPC_SteepSlope = ['SteepSlopeReview', pcpcR, Zoning_SteepSlopeProtectArea_r, '"Steep Slope"', None,
                       GIS_LNI_PR_PCPC_SteepSlope]
    PCPC_SkyPlaneReview = ['SkyPlaneReview', pcpcR, Zon_BaseDistricts, '[Long_Code]', "Long_Code IN('CMX-4','CMX-5')",
                           GIS_LNI_PR_PCPC_SkyPlaneReview]
    PAC_BuildIDSignageReview = ['BuildIDSignageReview', pacR, Zon_BaseDistricts, '[LONG_CODE]',
                                "Long_Code IN('ICMX', 'I-1', 'IRMX')", GIS_LNI_PR_PAC_BuildIDSignageReview]
    PAC_ParkwayBufferReview = ['ParkwayBufferReview', pacR, Zon_Overlays, '[Overlay_Name]',
                               "Overlay_Name IN('/CTR Center City Overlay District - Parkway Buffer')",
                               GIS_LNI_PR_PAC_ParkwayBufferReview]
    PAC_SinageSpecialControl = ['SinageSpecialControl', pacR, Zon_Overlays, '[Overlay_Name]',
                                "Overlay_Name IN('/CTR Center City Overlay District - Rittenhouse Square','/CTR Center City Overlay District - Center City Commercial Area','/CTR Center City Overlay District - Convention Center Area','/CTR Center City Overlay District - Independence Hall Area','/CTR Center City Overlay District - Vine Street Area','/CTR Center City Overlay District - Washington Square','/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood','/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue','/NCA Neighborhood Commercial Area Overlay District - Main Street/Manayunk and Venice Island','/NCA Neighborhood Commercial Area Overlay District - Logan Triangle','/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue','/NCA Neighborhood Commercial Area Overlay District - Lower and Central Germantown','/NCA Neighborhood Commercial Area Overlay District - North Delaware Avenue','/NCA Neighborhood Commercial Area Overlay District - Spring Garden','Accessory Sign Controls - Special Controls for Cobbs Creek, Roosevelt Boulevard, and Department of Parks and Recreation Land')",
                                GIS_LNI_PR_PAC_SignageSpecialControl]
    PHC_HistoricalResReview = ['HistoricalResReview', phcR, Historic_Sites_PhilReg, '"Historic Designation"', None,
                               GIS_LNI_PR_PHC_HistoricalResReview]
    PWD_GreenRoofReview = ['GreenRoofReview', pwdR, PWD_GSI_SMP_TYPES, '[SUBTYPE] &"-GREEN ROOF"', "SUBTYPE IN( 10 )",
                           GIS_LNI_PR_PWD_GreenRoofReview]
    PWD_GSI_Buffer = ['GSI_Buffer', pwdR, PWD_GSI_SMP_TYPES, '"Green Infrastructure"', None, GIS_LNI_PR_PWD_GSI_Buffer]

    # List to iterate inputs through parcel flag function
    reviewList = [PCPC_CityAveSiteReview, PCPC_RidgeAveFacadeReview, PCPC_MasterPlanReview, PCPC_CenterCityFacadeReview,
                  PCPC_NeighborConsReview,
                  PCPC_WissahickonWatershedSiteReview, PCPC_100YrFloodPlain, PCPC_SteepSlope, PCPC_SkyPlaneReview,
                  PAC_BuildIDSignageReview,
                  PAC_ParkwayBufferReview, PAC_SinageSpecialControl, PHC_HistoricalResReview, PWD_GreenRoofReview,
                  PWD_GSI_Buffer]

    # Set fake variable to by-pass lack of parcel creation
    parcelDict = {}

    # Call the parcelFlag funtion on each plan review input in order to create the plan review feature classes
    for r in reviewList:
        print('Beginning ' + r[0])
        inputs = tuple(r[:] + [workspace, PWD_Spatial_Join, parcelDict])
        parcelFlag(*inputs)


    # Step 4: Merge the individual plan review flag feature classes into summary classes for each type (PAC, PCPC, PWD)

    # Function that adds input fields to field maps that will be used later when merging individaul plan review flag
    # feature classes into summary pr flag feature classes.
    def add_input_fields_to_field_maps(input_fc, output_fc, review_type_field_map, sub_category_field_map,
                                       review_category_field_name, sub_category_field_name):
        arcpy.FeatureClassToFeatureClass_conversion(input_fc, workspace, output_fc)
        review_type_field_map.addInputField(output_fc, review_category_field_name)
        if len(sub_category_field_name) > 0:
            sub_category_field_map.addInputField(output_fc, sub_category_field_name)
        return {"review_type_field_map": review_type_field_map,
                "sub_category_field_map": sub_category_field_map}


    # Function that merges the individaul plan review flag feature classes into summary pr flag feature classes.
    def merge_incl_mappings(fc_and_field_name_list, output_fc):
        fc_list = []  # used to keep track of FCs that will be merged
        field_mappings = arcpy.FieldMappings()
        review_type_field_map = arcpy.FieldMap()
        review_type_field_name = 'REVIEW_TYPE'
        sub_category_field_map = arcpy.FieldMap()
        for fc_and_field_name in fc_and_field_name_list:
            return_dict = add_input_fields_to_field_maps(fc_and_field_name[0], fc_and_field_name[1],
                                                         review_type_field_map, sub_category_field_map,
                                                         review_type_field_name, fc_and_field_name[2])
            fc_list.append(fc_and_field_name[1])
            review_type_field_map = return_dict["review_type_field_map"]
        outField = review_type_field_map.outputField
        outField.name = review_type_field_name
        outField.aliasName = review_type_field_name
        outField.length = 2000
        review_type_field_map.outputField = outField
        field_mappings.addFieldMap(review_type_field_map)

        outField = sub_category_field_map.outputField
        outField.name = 'SUB_CATEGORY'
        outField.aliasName = 'SUB_CATEGORY'
        outField.length = 2000
        sub_category_field_map.outputField = outField
        field_mappings.addFieldMap(sub_category_field_map)

        arcpy.Merge_management(fc_list, output_fc, field_mappings)

        print("Deleting feature classes from memory")
        for fc in fc_list:
            arcpy.Delete_management(fc)


    # Merge PAC layers
    pac_fc_and_field_name_list = [[GIS_LNI_PR_PAC_BuildIDSignageReview, "PR_PAC_BuildIDSignageReview", "LONG_CODE"],
                                  [GIS_LNI_PR_PAC_ParkwayBufferReview, "PR_PAC_ParkwayBufferReview", "OVERLAY_NAME"],
                                  [GIS_LNI_PR_PAC_SignageSpecialControl, "PR_PAC_SignageSpecialControl",
                                   "OVERLAY_NAME"]]
    merge_incl_mappings(pac_fc_and_field_name_list, "Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC")

    # Merge PCPC layers
    pcpc_fc_and_field_name_list = [[GIS_LNI_PR_PCPC_100YrFloodPlain, "PR_PCPC_100YrFloodPlain", "FLD_ZONE"],
                                   [GIS_LNI_PR_PCPC_CenterCityFacadeReview, "PR_PCPC_CenterCityFacadeReview",
                                    "OVERLAY_NAME"],
                                   [GIS_LNI_PR_PCPC_CityAveSiteReview, "PR_PCPC_CityAveSiteReview", "OVERLAY_NAME"],
                                   [GIS_LNI_PR_PCPC_MasterPlanReview, "PR_PCPC_MasterPlanReview", "LONG_CODE"],
                                   [GIS_LNI_PR_PCPC_NeighborConsReview, "PR_PCPC_NeighborConsReview", "OVERLAY_NAME"],
                                   [GIS_LNI_PR_PCPC_RidgeAveFacadeReview, "PR_PCPC_RidgeAveFacadeReview",
                                    "OVERLAY_NAME"],
                                   [GIS_LNI_PR_PCPC_SkyPlaneReview, "PR_PCPC_SkyPlaneReview", "LONG_CODE"],
                                   [GIS_LNI_PR_PCPC_SteepSlope, "PR_PCPC_SteepSlope", ""],
                                   [GIS_LNI_PR_PCPC_WissWaterSiteReview, "PR_PCPC_WissWaterSiteReview", "OVERLAY_NAME"]]
    merge_incl_mappings(pcpc_fc_and_field_name_list, "Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC")

    # Merge PWD layers
    pwd_fc_and_field_name_list = [[GIS_LNI_PR_PWD_GreenRoofReview, "PR_PWD_GreenRoofReview", "SUBTYPE"],
                                  [GIS_LNI_PR_PWD_GSI_Buffer, "PR_PWD_GSI_Buffer", "SUBTYPE"]]
    pwd_output_fc = "Database Connections\\GISLNI.sde\\GIS_LNI.PR_PWD"
    merge_incl_mappings(pwd_fc_and_field_name_list, pwd_output_fc)


    # Step 5: Set subtypes for GIS_LNI PWD feature class

    # Function to set Green Stormwater Infrastructure (GSI) subtypes
    def set_gsi_subtype(input_feature_class, field):
        arcpy.SetSubtypeField_management(input_feature_class, field)
        # Store all the subtype values in a dictionary with the subtype code as the "key" and the
        # subtype description as the "value" (subtypeDict[code])
        gsi_subtype_dict = {"1": "TRENCH", "2": "BUMPOUT", "3": "RAIN GARDEN", "4": "WETLAND", \
                            "5": "BASIN", "6": "TREE TRENCH", "7": "PLANTER", "8": "PERVIOUS PLANTER", \
                            "9": "SWALE", "10": "GREEN ROOF", "11": "CISTERN"}
        for code in gsi_subtype_dict:
            arcpy.AddSubtype_management(input_feature_class, code, gsi_subtype_dict[code])
        # Set Default Subtype...
        arcpy.SetDefaultSubtype_management(input_feature_class, "1")


    # Set Subtype Field for GIS_LNI PWD feature class
    set_gsi_subtype(pwd_output_fc, "SUB_CATEGORY")

    # Step 6: Make fields of feature classes that will be included in the PLAN_REVIEW_FLAGS_ECLIPSE feature service
    # (http://phl.maps.arcgis.com/home/item.html?id=7a474e2bb78b4f258751e22161e4cc75) lowercase. Doing because____________

    feature_classes_to_make_lower = [GIS_LNI_PR_PCPC_100YrFloodPlain, GIS_LNI_PR_PCPC_SteepSlope,
                                     'Database Connections\\GISLNI.sde\\GIS_LNI.PR_CORNER_PROPERTIES',
                                     'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PWD',
                                     'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PHC',
                                     'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PCPC',
                                     'Database Connections\\GISLNI.sde\\GIS_LNI.PR_PAC',
                                     'Database Connections\\GISLNI.sde\\GIS_LNI.DISTRICTS_NEW']


    # Function to make the field names of a given feature class lowercase
    def fields_to_lower(input_feature_class, workspace, output_feature_class, output_save_location):
        print('Copying input data source' + input_feature_class + ' into memory')
        arcpy.FeatureClassToFeatureClass_conversion(input_feature_class, workspace, output_feature_class)
        field_names = [f.name for f in arcpy.ListFields(output_feature_class)]
        print('Building Field Maps')
        field_mappings = arcpy.FieldMappings()
        for field_name in field_names:
            field_map = arcpy.FieldMap()
            if field_name != 'Shape':  # https://gis.stackexchange.com/questions/30370/arcpy-error-in-adding-input-field-to-field-map
                field_map.addInputField(output_feature_class, field_name)
                outField = field_map.outputField
                outField.name = field_name.lower()
                field_map.outputField = outField
                field_mappings.addFieldMap(field_map)

        print('Field Maps built')

        print('Saving ' + output_feature_class + ' to PR_Flags_Phil geodatabase')
        arcpy.FeatureClassToFeatureClass_conversion(output_feature_class, output_save_location, output_feature_class,
                                                    field_mapping=field_mappings)
        print('Saved ' + output_feature_class + ' to PR_Flags_Phil geodatabase')

        arcpy.Delete_management(output_feature_class)


    # Geodatabase where we're saving the data to be used in the feature service
    PR_Flags_gdb = 'S:\\GIS\\FeatureServices\\PR_Flags\\PR_Flags_Phil.gdb'

    for feature_class in feature_classes_to_make_lower:
        output_feature_class = feature_class.split("GIS_LNI.")[1]
        fields_to_lower(feature_class, workspace, output_feature_class, PR_Flags_gdb)

    # Set Subtype Field for PWD feature service feature class
    set_gsi_subtype('S:\\GIS\\FeatureServices\\PR_Flags\\PR_Flags_Phil.gdb\\PR_PWD', "sub_category")

except arcpy.ExecuteError:
    # log.critical('The script failed in Step 7' )
    msgs = arcpy.GetMessages(2)
    print(msgs)
    print('Step 18 Failed')  # log.error(msgs)
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
