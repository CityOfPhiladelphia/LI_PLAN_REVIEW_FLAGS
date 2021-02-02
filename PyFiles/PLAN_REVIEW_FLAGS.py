def matchCentroid(parcel_outline, fields, parcel_id, orig_area, overlap_area, thinness, zoning, address, parcelDict, zoningFC, z):

def matchGeom(parcel_outline, fields, parcel_id, orig_area, overlap_area, thinness, zoning, address, parcelDict, zoningFC, z):
    print(datetime.datetime.now())
    parcelCrash = ''
    currentTract = 'CurrentDistrict'
    #tempParcels = 'TempParcels'
    tempZone = 'TempZone'
    districtCount = 0
    districtTotal = int(arcpy.GetCount_management(Council_Districts_Local).getOutput(0))
    arcpy.CalculateField_management(Council_Districts_Local, 'DISTRICT', '!DISTRICT!.strip(' ')', 'PYTHON_9.3')

    #Run Intersect Between Parcels and Zoning Layer
    IntersectOutput = localWorkspace + '\\' + z[0].replace(' ','_') + '_Int'
    print('Running Intersect')
    arcpy.Intersect_analysis([localWorkspace + '\\' + parcel_outline] + [zoningFC], IntersectOutput, 'ALL')

    # To ensure no slivers are included, a thiness ratio and shape area are calculated for intersecting polygons
    arcpy.AddField_management(IntersectOutput, 'Thinness', 'FLOAT')
    # NOTE Thiness calculation was removed by request, this is designed remove small overlaps in zoning from adjacent parcels
    arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
    """
    arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
    arcpy.CalculateField_management(IntersectOutput, 'ThinessRatio',
                                                  "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')

    """
    # inFL = ['PARCELID', 'GROSS_AREA', 'POLY_AREA',
    #        'Thinness', 'CODE', 'ADDRESS']
    IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fields)
    countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
    count = 0
    print('Found ' + str(countin) + ' records in intersect table')
    breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
    for row in IntersectCursor:
        # try:
        count += 1
        if count in breaks:
            print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
        if (float(row[overlap_area]) / float(row[
                                                 orig_area])) > 0.01:  # To implment 3% coverage and thinness minimum: and row[thinness] > 0.3 and (row[overlap_area] / float(row[orig_area])) > 0.03:
            # Instances where a specific value is being extracted from a field
            if zoning is not None:
                # print('1')
                for i, zf in enumerate(zoning):
                    # print('2')
                    if row[parcel_id] in parcelDict:
                        if row[fields.index(zf)] is not None:
                            # print('3')
                            prevZonDict = parcelDict[row[parcel_id]]
                            # print(prevZonDict)
                            newZon = None
                            if z[i] in prevZonDict:
                                # print('4')
                                prevZone = prevZonDict[z[i]]
                                newZon = list(set(str(row[fields.index(zf)]).split('|') + prevZone))
                            else:
                                # print('5')
                                newZon = None if row[fields.index(zf)] is None else str(row[fields.index(zf)]).split(
                                    '|')
                            newZonDict = prevZonDict
                            newZonDict[z[i]] = newZon
                            parcelDict[row[parcel_id]] = newZonDict
                    else:
                        """
                        print('6')
                        print(row[parcel_id])
                        print(z[i])
                        print(fields)
                        print(row[:])
                        print(zf)
                        print(row[fields.index(zf)])
                        print(row[address])
                        """
                        parcelDict[row[parcel_id]] = {z[i]: [row[fields.index(zf)]], 'ADDRESS': row[address]}
            # When all that is needed is an overlap between parcels and input layer
            else:
                # print('7')
                if row[parcel_id] in parcelDict:
                    prevZonDict = parcelDict[row[parcel_id]]
                    newZonDict = prevZonDict
                    newZonDict[z[0]] = z[0]
                    parcelDict[row[parcel_id]] = newZonDict
                else:
                    # print('8')
                    parcelDict[row[parcel_id]] = {z[0]: z[0], 'ADDRESS': row[address]}
        """
        except:
        continue
    """
    """
    districtTileCursor = arcpy.da.SearchCursor(Council_Districts_Local, 'DISTRICT') #ToDO Temp <--- Uncomment for Prod
    #districtTileCursor = ['4']#TODO TEMP <--- For testing only
    
    
    for tract in districtTileCursor:
        memory = inMemory
        districtCount += 1
        print('Processing District ' + tract[0] + "\n" + str(
            (float(districtCount) / float(districtTotal)) * 100.0) + '% Complete')
        arcpy.MakeFeatureLayer_management(localWorkspace + '\\' + Council_Districts_Local, currentTract,
                                          "DISTRICT = '" + tract[0] + "'")
        if arcpy.Exists(tempZone):
            arcpy.Delete_management(tempZone)
        print(localWorkspace + '\\' + zoningFC)
        print(currentTract)
        print(tempZone)
        arcpy.Clip_analysis(zoningFC, currentTract, tempZone)
        if arcpy.Exists(tempParcels):
            arcpy.Delete_management(tempParcels)
        print(localWorkspace)
        print(parcel_outline)
        print(currentTract)
        print(tempParcels)
        arcpy.Clip_analysis(localWorkspace + '\\' + parcel_outline, currentTract, tempParcels)
        IntersectOutput = localWorkspace + '\\Current_Int'
        print('Running Intersect')
        arcpy.Intersect_analysis([tempParcels] + [tempZone], IntersectOutput, 'ALL')

        # To ensure no slivers are included, a thiness ratio and shape area are calculated for intersecting polygons
        arcpy.AddField_management(IntersectOutput, 'Thinness', 'FLOAT')
        # NOTE Thiness calculation was removed by request, this is designed remove small overlaps in zoning from adjacent parcels
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
        """
    """
                arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
                arcpy.CalculateField_management(IntersectOutput, 'ThinessRatio',
                                                "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')

                """ """

        #inFL = ['PARCELID', 'GROSS_AREA', 'POLY_AREA',
        #        'Thinness', 'CODE', 'ADDRESS']
        IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fields)
        countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
        count = 0
        print('Found ' + str(countin) + ' records in intersect table')
        breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
        for row in IntersectCursor:
            #try:
            count += 1
            if count in breaks:
                print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
            if (float(row[overlap_area]) / float(row[orig_area])) > 0.01:  # To implment 3% coverage and thinness minimum: and row[thinness] > 0.3 and (row[overlap_area] / float(row[orig_area])) > 0.03:
                #Instances where a specific value is being extracted from a field
                if zoning is not None:
                    #print('1')
                    for i, zf in enumerate(zoning):
                        #print('2')
                        if row[parcel_id] in parcelDict:
                            if row[fields.index(zf)] is not None:
                                #print('3')
                                prevZonDict = parcelDict[row[parcel_id]]
                                #print(prevZonDict)
                                newZon = None
                                if z[i] in prevZonDict:
                                    #print('4')
                                    prevZone = prevZonDict[z[i]]
                                    newZon = list(set(str(row[fields.index(zf)]).split('|') + prevZone))
                                else:
                                    #print('5')
                                    newZon = None if row[fields.index(zf)] is None else str(row[fields.index(zf)]).split('|')
                                newZonDict = prevZonDict
                                newZonDict[z[i]] = newZon
                                parcelDict[row[parcel_id]] = newZonDict
                        else:
                            """"""
                            print('6')
                            print(row[parcel_id])
                            print(z[i])
                            print(fields)
                            print(row[:])
                            print(zf)
                            print(row[fields.index(zf)])
                            print(row[address])
                            """"""
                            parcelDict[row[parcel_id]] = {z[i]:[row[fields.index(zf)]], 'ADDRESS':row[address]}
                #When all that is needed is an overlap between parcels and input layer
                else:
                    #print('7')
                    if row[parcel_id] in parcelDict:
                        prevZonDict = parcelDict[row[parcel_id]]
                        newZonDict = prevZonDict
                        newZonDict[z[0]] = z[0]
                        parcelDict[row[parcel_id]] = newZonDict
                    else:
                        #print('8')
                        parcelDict[row[parcel_id]] = {z[0]: z[0], 'ADDRESS': row[address]}
            """"""
            except:
                continue
            """"""
        del IntersectCursor
        arcpy.Delete_management(IntersectOutput)
        arcpy.Delete_management(currentTract)
        arcpy.Delete_management(tempZone)
        arcpy.Delete_management(tempParcels)
    del districtTileCursor
    """
    print(datetime.datetime.now())
    return parcelDict

def parsedZoning(r, zid, zinfo, pwdDict, lookupFields):
    pac_types = [rv for rv in [r.PAC_BuildIDSignageReview(), r.PAC_SinageSpecialControl()] if rv is not None]
    pcpc_types = [rv for rv in [r.PCPC_SteepSlope(), r.PCPC_100YrFloodPlain(), r.PCPC_SkyPlaneReview(),
                                r.PCPC_CenterCityFacadeReview(),
                                r.PCPC_WissahickonWatershedSiteReview(), r.PCPC_CityAveSiteReview(),
                                r.PCPC_MasterPlanReview(),
                                r.PCPC_NeighborConsReview(), r.PCPC_RidgeAveFacadeReview()] if rv is not None]
    phc_types = [rv for rv in [r.PHC_HistoricalResReview()] if rv is not None]
    pwd_types = [rv for rv in [r.PWD_GreenRoofReview(), r.PWD_GSI_Buffer()] if rv is not None]

    pAddress = pwdDict[zid][lookupFields.index('ADDRESS')]
    pwdParcelid = pwdDict[zid][lookupFields.index('PARCELID')]
    pac_flag = 1 if any(rv for rv in pac_types) else 0
    pac_review_type = None if pac_flag == 0 else '|'.join(pac_types)
    pcpc_flag = 1 if any(rv for rv in pcpc_types) else 0
    pcpc_review_type = None if pcpc_flag == 0 else '|'.join(pcpc_types)
    phc_flag = 1 if any(rv for rv in phc_types) else 0
    phc_review_type = None if phc_flag == 0 else '|'.join(phc_types)
    pwd_flag = 1 if any(rv for rv in pwd_types) else 0
    pwd_review_type = None if pwd_flag == 0 else '|'.join(pwd_types)
    corner_property = pwdDict[zid][lookupFields.index('Corner')]
    parcel_area = pwdDict[zid][lookupFields.index('GROSS_AREA')]
    base_zoning = zinfo['BASE_ZONING']
    overlay_zoning = zinfo['OVERLAY_ZONING']
    li_inspection_district = pwdDict[k][lookupFields.index('DISTRICT')]
    floodplain = 1 if zinfo['FLOODPLAIN'] else 0
    steep_slope = 1 if zinfo['STEEP_SLOPE'] else 0
    zoning_rco = None if zinfo['ZONING_RCO'] is None else '|'.join(zinfo['ZONING_RCO'].split(', '))
    iList = [pAddress, pwdParcelid, pac_flag, pac_review_type, pcpc_flag, pcpc_review_type,
                  phc_flag, phc_review_type, pwd_flag, pwd_review_type, corner_property, parcel_area, base_zoning,
                  overlay_zoning, li_inspection_district, floodplain, steep_slope, zoning_rco]
    return iList

class ReviewType:
    def __init__(self, infoDict):
        self.infoDict = infoDict


    def PCPC_CityAveSiteReview(self):
        CityAveSiteReview = ['/CAO City Avenue Overlay District - City Avenue Regional Center Area','/CAO City Avenue Overlay District - City Avenue Village Center Area']
        if self.infoDict['OVERLAY_ZONING'] is not None:
            if any(o in CityAveSiteReview for o in self.infoDict['OVERLAY_ZONING'].split('|')):
                return 'CityAveSiteReview'


    def PCPC_RidgeAveFacadeReview(self):
        RidgeAveFacadeReview = ['/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue']
        if self.infoDict['OVERLAY_ZONING']:
            if any(o in RidgeAveFacadeReview for o in self.infoDict['OVERLAY_ZONING'].split('|')):
                return 'RidgeAveFacadeReview'


    def PCPC_MasterPlanReview(self):
        MasterPlanReview = ['RMX-1', 'RMX-2', 'SP-ENT', 'SP-INS', 'SP-STA']
        if self.infoDict['BASE_ZONING']:
            if any(z in MasterPlanReview for z in self.infoDict['BASE_ZONING'].split('|')):
                return 'MasterPlanReview'

    def PCPC_CenterCityFacadeReview(self):
        CenterCityFacadeReview = ['/CTR Center City Overlay District - Chestnut and Walnut Street Area', '/CTR Center City Overlay District - Broad Street Area South','/CTR Center City Overlay District - Market Street Area East']
        if self.infoDict['OVERLAY_ZONING'] is not None:
            if any(o in CenterCityFacadeReview for o in self.infoDict['OVERLAY_ZONING'].split('|')):
                return 'CenterCityFacadeReview'

    def PCPC_NeighborConsReview(self):
        NeighborConsReview = ['/NCO Neighborhood Conservation Overlay District - Central Roxborough','/NCO Neighborhood Conservation Overlay District - Overbrook Farms','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2','/NCO Neighborhood Conservation Overlay District - Queen Village','/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough']
        if self.infoDict['OVERLAY_ZONING'] is not None:
            if any(o in NeighborConsReview for o in self.infoDict['OVERLAY_ZONING'].split('|')):
                return 'NeighborConsReview'

    def PCPC_WissahickonWatershedSiteReview (self):
        WissahickonWatershedSiteReview = ['/NCO Neighborhood Conservation Overlay District - Central Roxborough','/NCO Neighborhood Conservation Overlay District - Overbrook Farms','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1','/NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2','/NCO Neighborhood Conservation Overlay District - Queen Village','/NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough']
        if self.infoDict['OVERLAY_ZONING'] is not None:
            if any(o in WissahickonWatershedSiteReview for o in self.infoDict['OVERLAY_ZONING'].split('|')):
                return 'WissahickonWatershedSiteReview'

    def PCPC_100YrFloodPlain(self):
        if self.infoDict['FLOODPLAIN'] == 1:
            return '100 Year Floodplain'

    def PCPC_SteepSlope(self):
        if self.infoDict['STEEP_SLOPE'] == 1:
            return 'Steep Slope'

    def PCPC_SkyPlaneReview(self):
        SkyPlaneReview = ['CMX-4','CMX-5']
        if self.infoDict['BASE_ZONING'] is not None:
            if any(z in SkyPlaneReview for z in self.infoDict['BASE_ZONING'].split('|')):
                return 'SkyPlaneReview'

    def PAC_BuildIDSignageReview(self):
        BuildIDSignageReview = ['ICMX', 'I-1', 'IRMX']
        if self.infoDict['BASE_ZONING'] is not None:
            if any(z in BuildIDSignageReview for z in self.infoDict['BASE_ZONING'].split('|')):
                return 'BuildIDSignageReview'

    def PAC_ParkwayBufferReview(self):
        ParkwayBufferReview = ['/CTR Center City Overlay District - Parkway Buffer']
        if self.infoDict['OVERLAY_ZONING'] is not None:
            if any(o in ParkwayBufferReview for o in self.infoDict['OVERLAY_ZONING'].split('|')):
                return 'ParkwayBufferReview'

    def PAC_SinageSpecialControl(self):
        SinageSpecialControl = ['/CTR Center City Overlay District - Rittenhouse Square','/CTR Center City Overlay District - Center City Commercial Area','/CTR Center City Overlay District - Convention Center Area','/CTR Center City Overlay District - Independence Hall Area','/CTR Center City Overlay District - Vine Street Area','/CTR Center City Overlay District - Washington Square','/NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood','/NCA Neighborhood Commercial Area Overlay District - Germantown Avenue','/NCA Neighborhood Commercial Area Overlay District - Main Street/Manayunk and Venice Island','/NCA Neighborhood Commercial Area Overlay District - Logan Triangle','/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue','/NCA Neighborhood Commercial Area Overlay District - Lower and Central Germantown','/NCA Neighborhood Commercial Area Overlay District - North Delaware Avenue','/NCA Neighborhood Commercial Area Overlay District - Spring Garden','Accessory Sign Controls - Special Controls for Cobbs Creek, Roosevelt Boulevard, and Department of Parks and Recreation Land']
        if self.infoDict['OVERLAY_ZONING'] is not None:
            if any(o in SinageSpecialControl for o in self.infoDict['OVERLAY_ZONING'].split('|')):
                return 'SinageSpecialControl'

    def PHC_HistoricalResReview(self):
        if self.infoDict['STEEP_SLOPE'] == 1:
            return 'HistoricalResReview'

    def PWD_GreenRoofReview(self):
        if self.infoDict['PWD_REVIEW_TYPE'] is not None:
            if any(p == 'GREEN ROOF' for p in self.infoDict['PWD_REVIEW_TYPE'].split('|')):
                return 'GREEN ROOF'

    def PWD_GSI_Buffer(self):
        if self.infoDict['PWD_REVIEW_TYPE']:
            return self.infoDict['PWD_REVIEW_TYPE']




#############################################################################################################



import datetime
import logging
import sys
import traceback

import arcpy
from sde_connections import DataBridge, GISLNI

try:
    print('Step 1: Configuring log file...')
    log_file_path = 'E:\LI_PLAN_REVIEW_FLAGS\Logs\PermitReviewFlags.log'
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

startTime = datetime.datetime.now()
print(startTime)
localWorkspace = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb'
inMemory = 'in_memory'

arcpy.env.workspace = localWorkspace
arcpy.env.overwriteOutput = True
editDB = GISLNI.sde_path
edit = arcpy.da.Editor(editDB)
log.info('Beginning PR Flags')
#try:
# External data sources
#PWD_PARCELS_DataBridge = DataBridge.sde_path + '\\GIS_WATER.pwd_parcels' #TODO Uncomment for Prod
PWD_PARCELS_DataBridge = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb\\PWD_Input_Main_St'#TODO Temp
PWD_PARCELS_PINNED_DataBridge = DataBridge.sde_path + '\\GIS_WATER.pwd_parcels_pinned'
Zoning_BaseDistricts = DataBridge.sde_path + '\\GIS_PLANNING.Zoning_BaseDistricts' # Based off DOR Parcels
FEMA_100_flood_Plain = DataBridge.sde_path + '\\GIS_PLANNING.FEMA_100_flood_Plain'
Historic_Sites_PhilReg = DataBridge.sde_path + '\\GIS_PLANNING.Historic_Sites_PhilReg' # Based off PWD Parcels
Zoning_Overlays = DataBridge.sde_path + '\\GIS_PLANNING.Zoning_Overlays' # Based off DOR Parcels
Zoning_SteepSlopeProtectArea_r = DataBridge.sde_path + '\\GIS_PLANNING.Zoning_SteepSlopeProtectArea_r'
GSI_SMP_TYPES = DataBridge.sde_path + '\\GIS_WATER.GSI_SMP_TYPES'
GISLNI_Corner_Properties = GISLNI.sde_path + '\\GIS_LNI.PR_CORNER_PROPERTIES'
DataBridge_Districts = DataBridge.sde_path + '\\GIS_LNI.LI_DISTRICTS'
Council_Districts_2016 = DataBridge.sde_path + '\\GIS_PLANNING.Council_Districts_2016'
PPR_Assets = DataBridge.sde_path + '\\GIS_PPR.PPR_Assets'
Park_IDs = GISLNI.sde_path + '\\GIS_LNI.PR_PARK_NAME_IDS'
Zoning_RCOs = DataBridge.sde_path+'\\GIS_PLANNING.Zoning_RCO'
#DOR_PARCELS_DataBridge = DataBridge.sde_path + '\\GIS_DOR.dor_parcel' # TODO Uncomment for Prod
DOR_PARCELS_DataBridge = 'E:\\LI_PLAN_REVIEW_FLAGS\\Workspace.gdb\\DOR_Input_Main_St'# TODO TEMP

# Internal data sources
PWD_Parcels_Raw = 'PWDParcels_Raw'
PWD_Parcels_PINED = 'PWDParcels_PIN'
PWD_Parcels_Working = 'PWDParcels'
PWD_Parcels_Remaining = 'PWD_Parcels_Remaining'
CornerProperties = 'Corner_Properties'
PWD_PARCELS_SJ = 'PWD_PARCELS_Spatial_Join'
CornerPropertiesSJ_P = 'CornerPropertiesSJ_P'
Districts = 'Districts'
Hist_Sites_PhilReg = 'Hist_Sites_PhilReg' #We only look at properties on the local register--
Zon_Overlays = 'ZoningOverlays_'
Zoning_SteepSlope = 'PCPC_SteepSlope'
PWD_GSI_SMP_TYPES = 'PWD_GSI_SMP_TYPES'
PWD_Green_Roof = 'PWD_Green_Roof'
PWD_GSI_SMP_Buffer = 'PWD_GSI_SMP_Buffer'
Zon_BaseDistricts = 'ZonBaseDistricts_'
Zon_RCOs = 'ZonRCO'
ArtCommission_BuildingIDSinageReview = 'ArtCommission_BuildingIDSinageReview'
FloodPlain100Yr = 'PCPC_100YrFloodPlain'
PCPC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PCPC_Intersect'
PAC_Intersect = 'G:\\01_Dan_Interrante_Project_Folder\\ToolScratch.gdb\\PAC_Intersect'
Flags_Table_Temp = 'Flags_Table_Temp'
Flags_Table_Clean = 'Flags_Table_Clean'
Council_Districts_Local = 'Districts_'
Park_IDs_Local = 'ParkNameIDs_'
PPR_Assets_Local = 'PPRAssests_'
PPR_Assets_Temp_Pre_Dissolve = 'in_memory\\PPR_Assets_Temp_Pre_Dissolve'
PPR_Assets_Temp = 'in_memory\\PPR_Assets_Temp'
DOR_Parcels_Local = 'DOR_Parcels_Testing' #TODO Temp for Testing
DOR_For_Spatial = 'DOR_For_Spatial'
Floodplain = 'Floodplain'



# Output FeatureClasses
GIS_LNI_PR_PCPC_CityAveSiteReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_CityAveSiteReview'
GIS_LNI_PR_PCPC_RidgeAveFacadeReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_RidgeAveFacadeReview'
GIS_LNI_PR_PCPC_MasterPlanReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_MasterPlanReview'
GIS_LNI_PR_PCPC_CenterCityFacadeReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_CenterCityFacadeReview'
GIS_LNI_PR_PCPC_NeighborConsReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_NeighborConsReview'
GIS_LNI_PR_PCPC_WissWaterSiteReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_WissWaterSiteReview'
GIS_LNI_PR_PCPC_100YrFloodPlain = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_100YrFloodPlain'
GIS_LNI_PR_PCPC_SteepSlope = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_SteepSlope'
GIS_LNI_PR_PCPC_SkyPlaneReview = GISLNI.sde_path + '\\GIS_LNI.PR_PCPC_SkyPlaneReview'
GIS_LNI_PR_PAC_BuildIDSignageReview = GISLNI.sde_path + '\\GIS_LNI.PR_PAC_BuildIDSignageReview'
GIS_LNI_PR_PAC_ParkwayBufferReview = GISLNI.sde_path + '\\GIS_LNI.PR_PAC_ParkwayBufferReview'
GIS_LNI_PR_PAC_SignageSpecialControl = GISLNI.sde_path + '\\GIS_LNI.PR_PAC_SinageSpecialControl'
GIS_LNI_PR_PWD_GSI_Buffer = GISLNI.sde_path + '\\GIS_LNI.PR_PWD_GSI_Buffer'
GIS_LNI_PR_PWD_GreenRoofReview = GISLNI.sde_path + '\\GIS_LNI.PR_PWD_GreenRoofReview'
GIS_LNI_PR_PHC_HistoricalResReview = GISLNI.sde_path + '\\GIS_LNI.PR_PHC'

PR_FLAG_SUMMARY = GISLNI.sde_path + '\\GIS_LNI.LI_PR_FLAG_SUMMARY'
print('SUCCESS at Step 2')

"""
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
print('Updating PWD Parcels PINNED')
if arcpy.Exists(PWD_Parcels_PINED):
    arcpy.Delete_management(PWD_Parcels_PINED)
arcpy.FeatureClassToFeatureClass_conversion(PWD_PARCELS_PINNED_DataBridge, localWorkspace, PWD_Parcels_PINED)
print('Updating PPR Assets')
if arcpy.Exists(PPR_Assets_Local):
    arcpy.Delete_management(PPR_Assets_Local)
arcpy.FeatureClassToFeatureClass_conversion(PPR_Assets, localWorkspace, PPR_Assets_Local)
print('Updating DOR Parcels')
if arcpy.Exists(DOR_Parcels_Local):
    arcpy.Delete_management(DOR_Parcels_Local)
arcpy.FeatureClassToFeatureClass_conversion(DOR_PARCELS_DataBridge, localWorkspace, DOR_Parcels_Local, 'STATUS = 1 AND MAPREG IS NOT NULL')
if arcpy.Exists(Floodplain):
    arcpy.Delete_management(Floodplain)
arcpy.FeatureClassToFeatureClass_conversion(FEMA_100_flood_Plain, localWorkspace, Floodplain)
if arcpy.Exists(Zon_RCOs):
    arcpy.Delete_management(Zon_RCOs)
arcpy.FeatureClassToFeatureClass_conversion(Zoning_RCOs, localWorkspace,Zon_RCOs)

if arcpy.Exists(Hist_Sites_PhilReg):
    arcpy.Delete_management(Hist_Sites_PhilReg)
arcpy.FeatureClassToFeatureClass_conversion(Historic_Sites_PhilReg, localWorkspace, Hist_Sites_PhilReg)
"""

# Create Local Working Table
arcpy.CreateTable_management(localWorkspace, Flags_Table_Temp, PR_FLAG_SUMMARY)


# Run DOR Parcels through Base Zoning
print('Applying Base Zoning to DOR')
print('Calculating Parcel Size')
arcpy.AddField_management(DOR_Parcels_Local, 'PARCEL_AREA', 'FLOAT')
arcpy.CalculateGeometryAttributes_management(DOR_Parcels_Local, [['PARCEL_AREA', 'AREA']], area_unit='SQUARE_FEET_US')
DOR_Base_Fields = ['MAPREG', 'PARCEL_AREA', 'POLY_AREA',
        'Thinness', 'CODE', 'ADDR_STD']
print('Beginning DOR Spatial Association')
dorDict = {}
dorDict = matchGeom(DOR_Parcels_Local, DOR_Base_Fields, DOR_Base_Fields.index('MAPREG'),
                    DOR_Base_Fields.index('PARCEL_AREA'), DOR_Base_Fields.index('POLY_AREA'),
                    DOR_Base_Fields.index('Thinness'), ['CODE'], DOR_Base_Fields.index('ADDR_STD'),
                    dorDict, Zon_BaseDistricts, ['Base_Zone'])
""" #TODO DELETE
# Run DOR Parcels through Zoning Overlays
zoningLayer = 'zoningLayer'
specOverlayCursor = arcpy.da.SearchCursor(Zon_Overlays, 'OVERLAY_NAME')
overlayTypes = []
for row in specOverlayCursor:
    if row[0] not in overlayTypes:
        overlayTypes.append(row[0])
del specOverlayCursor

# Create a layer based off of each overlay type saved from previous list
print('Applying Zoning Overlay to DOR')
overlayTotal = len(overlayTypes)
overlayCount = 0
arcpy.MakeFeatureLayer_management(Zon_Overlays, zoningLayer)
parcelDict = {}
DOR_Overlay_fields = DOR_Base_Fields
DOR_Overlay_fields[DOR_Overlay_fields.index('CODE')] = 'OVERLAY_NAME'
#for overlayType in overlayTypes[:2]: #TODO Delete
#for overlayType in ['/NCA Neighborhood Commercial Area Overlay District - Ridge Avenue']: #TODO Temp for testing
for overlayType in overlayTypes:
    overlayCount += 1
    print('Starting '+ overlayType +' overlay ' + str(overlayCount)+ ' of ' + str(overlayTotal))
    #arcpy.SelectLayerByAttribute_management(zoningLayer, 'NEW_SELECTION', "OVERLAY_NAME LIKE '" + overlayType + "%'") #TODO Delete
    arcpy.SelectLayerByAttribute_management(zoningLayer, 'NEW_SELECTION', "OVERLAY_NAME = '" + overlayType.replace("'", '"') + "'")
    zoningCurrent = overlayType.lstrip('/') + '_layer'
    arcpy.MakeFeatureLayer_management(zoningLayer, zoningCurrent)
    dorDict = matchGeom(DOR_Parcels_Local, DOR_Overlay_fields, DOR_Overlay_fields.index('MAPREG'), DOR_Overlay_fields.index('PARCEL_AREA'),
                       DOR_Overlay_fields.index('POLY_AREA'), DOR_Overlay_fields.index('Thinness'), ['OVERLAY_NAME'],
                       DOR_Overlay_fields.index('ADDR_STD'), dorDict, zoningCurrent, ['Overlay_Zone'])
"""
DOR_Overlay_fields = DOR_Base_Fields
DOR_Overlay_fields[DOR_Overlay_fields.index('CODE')] = 'OVERLAY_NAME'
dorDict = matchGeom(DOR_Parcels_Local, DOR_Overlay_fields, DOR_Overlay_fields.index('MAPREG'), DOR_Overlay_fields.index('PARCEL_AREA'),
                   DOR_Overlay_fields.index('POLY_AREA'), DOR_Overlay_fields.index('Thinness'), ['OVERLAY_NAME'],
                   DOR_Overlay_fields.index('ADDR_STD'), dorDict, Zon_Overlays, ['Overlay_Zone'])


# Zoning RCO
print('Applying Zoning RCO to DOR')
DOR_RCO_fields = DOR_Overlay_fields
DOR_RCO_fields[4] = 'LNI_ID'
dorDict = matchGeom(DOR_Parcels_Local, DOR_RCO_fields, DOR_RCO_fields.index('MAPREG'), DOR_RCO_fields.index('PARCEL_AREA'),
                       DOR_RCO_fields.index('POLY_AREA'), DOR_RCO_fields.index('Thinness'), ['LNI_ID'],
                       DOR_RCO_fields.index('ADDR_STD'), dorDict, Zon_RCOs, ['ZONING_RCO'])

# PWD Green Roof
print('Applying Green Roof to DOR')
arcpy.AddField_management(PWD_GSI_SMP_TYPES, 'PWD', 'TEXT', field_length='3')
DOR_PWD_fields = DOR_Overlay_fields
DOR_PWD_fields[4] = 'PWD'
arcpy.MakeFeatureLayer_management(PWD_GSI_SMP_TYPES, PWD_Green_Roof, "SUBTYPE IN( 10 )")
dorDict = matchGeom(DOR_Parcels_Local, DOR_PWD_fields, DOR_PWD_fields.index('MAPREG'), DOR_PWD_fields.index('PARCEL_AREA'),
                       DOR_PWD_fields.index('POLY_AREA'), DOR_PWD_fields.index('Thinness'), None,
                       DOR_PWD_fields.index('ADDR_STD'), dorDict, PWD_Green_Roof, ['GREEN ROOF'])

# PWD SMP Type Buffer
print('Applying PWD Buffer to DOR')
arcpy.Buffer_analysis(PWD_GSI_SMP_TYPES, PWD_GSI_SMP_Buffer, '50 Feet')
dorDict = matchGeom(DOR_Parcels_Local, DOR_PWD_fields, DOR_PWD_fields.index('MAPREG'), DOR_PWD_fields.index('PARCEL_AREA'),
                       DOR_PWD_fields.index('POLY_AREA'), DOR_PWD_fields.index('Thinness'), None,
                       DOR_PWD_fields.index('ADDR_STD'), dorDict, PWD_GSI_SMP_Buffer, ['Green Infrastructure'])

# Floodplain
print('Applying Floodplain to DOR')
arcpy.AddField_management(Floodplain, 'Floodplain', 'TEXT', field_length='3')
DOR_Flood_fields = DOR_PWD_fields
DOR_Flood_fields[4] = 'Floodplain'
dorDict = matchGeom(DOR_Parcels_Local, DOR_Flood_fields, DOR_Flood_fields.index('MAPREG'), DOR_Flood_fields.index('PARCEL_AREA'),
                       DOR_Flood_fields.index('POLY_AREA'), DOR_Flood_fields.index('Thinness'), None,
                       DOR_Flood_fields.index('ADDR_STD'), dorDict, Floodplain, ['Floodplain'])
# Steep Slope
print('Applying Steep Slope to DOR')
arcpy.AddField_management(Zoning_SteepSlope, 'Steep_Slope', 'TEXT', field_length='3')
DOR_Slope_fields = DOR_Flood_fields
DOR_Slope_fields[4] = 'Steep_Slope'
dorDict = matchGeom(DOR_Parcels_Local, DOR_Slope_fields, DOR_Slope_fields.index('MAPREG'), DOR_Slope_fields.index('PARCEL_AREA'),
                       DOR_Slope_fields.index('POLY_AREA'), DOR_Slope_fields.index('Thinness'), None,
                       DOR_Slope_fields.index('ADDR_STD'), dorDict, Zoning_SteepSlope, ['Steep_Slope'])

# Historic Properties
print('Applying Historic Areas')
arcpy.AddField_management(Hist_Sites_PhilReg, 'Historic', 'TEXT', field_length='3')
DOR_Historic_fields = DOR_Slope_fields
DOR_Historic_fields[4] = 'Historic'
dorDict = matchGeom(DOR_Parcels_Local, DOR_Historic_fields, DOR_Historic_fields.index('MAPREG'), DOR_Historic_fields.index('PARCEL_AREA'),
                       DOR_Historic_fields.index('POLY_AREA'), DOR_Historic_fields.index('Thinness'), None,
                       DOR_Historic_fields.index('ADDR_STD'), dorDict, Hist_Sites_PhilReg, ['Historic'])

# Add Values to Local DOR GIS
arcpy.management.AddFields(DOR_Parcels_Local, [['BASE_ZONING', 'TEXT','', '1999'],
                                               ['OVERLAY_ZONING', 'TEXT','', '1999'], ['ZONING_RCO', 'TEXT','', '1999'],
                                               ['PWD_REVIEW_TYPE', 'TEXT','', '1999'], ['FLOODPLAIN', 'SHORT'],
                                               ['STEEP_SLOPE', 'SHORT'], ['HISTORIC', 'SHORT'], ['COMPLETED', 'SHORT'], ['ADDRESS', 'TEXT','', '1999']])
arcpy.CalculateField_management(DOR_Parcels_Local, 'ADDRESS', '!ADDR_STD!', 'PYTHON3')
cursorFieldList = ['MAPREG', 'BASE_ZONING', 'OVERLAY_ZONING', 'ZONING_RCO', 'PWD_REVIEW_TYPE', 'FLOODPLAIN', 'STEEP_SLOPE', 'HISTORIC', 'ADDRESS','PIN', 'COMPLETED']
dorUpdateCursor = arcpy.da.UpdateCursor(DOR_Parcels_Local, cursorFieldList)
pinDict = {}
countin = int(arcpy.GetCount_management(DOR_Parcels_Local).getOutput(0))
count = 0
print('Found ' + str(countin) + ' records in input table')
breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
for row in dorUpdateCursor:
    count += 1
    if count in breaks:
        print('DOR Update Cursor ' + str(int(round(count * 100.0 / countin))) + '% complete...')
    if row[cursorFieldList.index('MAPREG')] in dorDict:
        pInfo = dorDict[row[cursorFieldList.index('MAPREG')]]
        if 'Base_Zone' in pInfo:
            row[cursorFieldList.index('BASE_ZONING')] = '|'.join(pInfo['Base_Zone'])
        if 'Overlay_Zone' in pInfo:
            row[cursorFieldList.index('OVERLAY_ZONING')] = '|'.join(pInfo['Overlay_Zone'])
        if 'ZONING_RCO' in pInfo:
            row[cursorFieldList.index('ZONING_RCO')] = '|'.join([str(z) for z in pInfo['ZONING_RCO']])
        if 'GREEN ROOF' in pInfo and 'Green Infrastructure' in pInfo:
            row[cursorFieldList.index('PWD_REVIEW_TYPE')] = pInfo['GREEN ROOF'] + '|' + pInfo['Green Infrastructure']
        elif 'GREEN ROOF' in pInfo:
            row[cursorFieldList.index('PWD_REVIEW_TYPE')] = pInfo['GREEN ROOF']
        elif 'Green Infrastructure' in pInfo:
            row[cursorFieldList.index('PWD_REVIEW_TYPE')] = pInfo['Green Infrastructure']
        if 'Floodplain' in pInfo:
            row[cursorFieldList.index('FLOODPLAIN')] = 1
        if 'Steep_Slope' in pInfo:
            row[cursorFieldList.index('STEEP_SLOPE')] = 1
        if 'Historic' in pInfo:
            row[cursorFieldList.index('HISTORIC')] = 1
        if row[cursorFieldList.index('PIN')] is not None:
            pinDict[row[cursorFieldList.index('PIN')]] = {f:row[cursorFieldList.index(f)] for f in cursorFieldList if f != 'PIN'}
        dorUpdateCursor.updateRow(row)
del dorUpdateCursor


# Prepare PWD Parcels
# Merge Parks with Parcels
# Determine if parks have been added yet
tCursor = arcpy.da.SearchCursor(PWD_Parcels_Raw, 'PARCELID')
print('Identifying Lowest Parcel ID')
isNeg = min([int(row[0]) for row in tCursor])
del tCursor
if isNeg > 0:
    log.info('Adding new park data')
    print('Adding new park data')
    cursor1 = arcpy.da.SearchCursor(Park_IDs, ['CHILD_OF', 'LI_TEMP_ID'])
    parkDict = {row[0]: row[1] for row in cursor1}
    del cursor1
    minID = min([v for v in parkDict.values()])
    print('Dissolving Parks Polygons')
    arcpy.Dissolve_management(PPR_Assets_Local, PPR_Assets_Temp, ['CHILD_OF'])

    # The IDs are negative so we're looking for the next LOWEST value to add
    cursor2 = arcpy.da.SearchCursor(PPR_Assets_Temp, ['CHILD_OF'])
    cursor2b = arcpy.da.InsertCursor(Park_IDs, ['CHILD_OF', 'LI_TEMP_ID'])
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
            parkDict[row[0]] = minID
            cursor2b.insertRow([row[0], minID])
    del cursor2
    del cursor2b
    try:
        edit.stopOperation()
        edit.stopEditing(True)
    except:
        pass

    print('Adding and calculating geometry')
    arcpy.AddGeometryAttributes_management(PPR_Assets_Temp, 'AREA', Area_Unit='SQUARE_FEET_US')
    arcpy.AddField_management(PPR_Assets_Temp, 'PARCEL_AREA', 'LONG')
    # arcpy.CalculateField_management(PPR_Assets_Temp, 'PARCEL_AREA', '!POLY_AREA!', 'PYTHON')
    arcpy.CalculateField_management(PPR_Assets_Temp, 'PARCEL_AREA', '!POLY_AREA!', 'PYTHON3')

    # Join Park IDs to Temp Parks Layer
    arcpy.JoinField_management(PPR_Assets_Temp, 'CHILD_OF', Park_IDs, 'CHILD_OF', ['LI_TEMP_ID'])

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
    arcpy.Append_management(PPR_Assets_Temp, PWD_Parcels_Raw, schema_type='NO_TEST', field_mapping=fms)



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
print('Spatial Joing Parcels and Corner Properties')
arcpy.SpatialJoin_analysis(PWD_PARCELS_SJ, CornerPropertiesSJ_P, PWD_Parcels_Working)
corZcursor = arcpy.da.UpdateCursor(PWD_Parcels_Working, 'Corner')
for row in corZcursor:
    if row[0] is None:
        row[0] = 0
        corZcursor.updateRow(row)
arcpy.Delete_management(CornerPropertiesSJ_P)
arcpy.Delete_management(PWD_PARCELS_SJ)
print('Adding PINS to Parcels')
arcpy.JoinField_management(PWD_Parcels_Working, 'PARCELID', PWD_Parcels_PINED, 'PARCELID', ['PIN'])
print('Completed PWD Parcel Preparation')

# Add Flood, Steep Slope, and PWD Info to All PWD Parcels

pwdPINFields = ['PARCELID', 'ADDRESS', 'PIN', 'GROSS_AREA', 'Corner', 'DISTRICT']
pwdPINcursor = arcpy.da.SearchCursor(PWD_Parcels_Working, pwdPINFields)
pwdPINLookupDict = {row[pwdPINFields.index('PIN')]:row[:] for row in pwdPINcursor}
del pwdPINcursor


# Join DOR and PWD via PIN
flagFields = [f.name for f in arcpy.ListFields(Flags_Table_Temp)]
del flagFields[flagFields.index('OBJECTID')]
pwdPINInsertcursor = arcpy.da.InsertCursor(Flags_Table_Temp, flagFields)
completedList = []
for k, v in pinDict.items():
    if k in pwdPINLookupDict:
        review = ReviewType(v)
        insertList = parsedZoning(review, k, v, pwdPINLookupDict, pwdPINFields)
        #print(insertList)
        pwdPINInsertcursor.insertRow(insertList)
        completedList.append(k)
#arcpy.TableToTable_conversion(Flags_Table_Temp, localWorkspace, 'FlagsTableTest')
#arcpy.TruncateTable_management(Flags_Table_Temp) #TODO TEMP
del pwdPINInsertcursor

# Mark matched parcels in DOR
addressDict = {}
completeDOR1 = arcpy.da.UpdateCursor(DOR_Parcels_Local, cursorFieldList)
count = 0
for row in completeDOR1:

    if row[cursorFieldList.index('PIN')] is not None and row[cursorFieldList.index('PIN')] in completedList:

        row[cursorFieldList.index('COMPLETED')] = 1
    else:

        addressDict[row[cursorFieldList.index('ADDRESS')]] = {f:row[cursorFieldList.index(f)] for f in cursorFieldList}
    completeDOR1.updateRow(row) #TODO Uncomment for prod
del completeDOR1

# Match Parcels Via Address
pwdAddressFields = ['PARCELID', 'ADDRESS', 'GROSS_AREA', 'Corner', 'DISTRICT']
pwdAddressCursor = arcpy.da.SearchCursor(PWD_Parcels_Working, pwdAddressFields)
pwdAddressDict = {row[pwdAddressFields.index('ADDRESS')]:row[:] for row in pwdAddressCursor}
del pwdAddressCursor
pwdAddressInsertCursor = arcpy.da.InsertCursor(Flags_Table_Temp, flagFields)
completedList = []
for k,v in addressDict.items():
    if k in pwdAddressDict:
        review = ReviewType(v)
        insertList = parsedZoning(review, k, v, pwdAddressDict, pwdAddressFields)
        #pwdAddressInsertCursor.insertRow(insertList) #TODO Uncomment for prod
        completedList.append(k)
del pwdAddressInsertCursor

#Mark Parcels as completed in DOR
intersectList = []
dorAddressCursor = arcpy.da.UpdateCursor(DOR_Parcels_Local, ['ADDRESS', 'COMPLETED', 'MAPREG'])
for row in dorAddressCursor:
    if row[0] in completedList:
        row[1] = 1
        dorAddressCursor.updateRow(row)
    else:
        intersectList.append(row[2])
del dorAddressCursor

# Intersect remaining parcels to PWD
#arcpy.MakeFeatureLayer_management(DOR_Parcels_Local, DOR_For_Spatial, "COMPLETED IS NULL")
arcpy.FeatureClassToFeatureClass_conversion(DOR_Parcels_Local, localWorkspace, DOR_For_Spatial, "COMPLETED IS NULL")
spatialDict = {}
copyList = ['BASE_ZONING', 'OVERLAY_ZONING', 'ZONING_RCO', 'PWD_REVIEW_TYPE', 'FLOODPLAIN', 'STEEP_SLOPE', 'HISTORIC']
PWD_Field_List = ['PARCELID', 'GROSS_AREA', 'POLY_AREA', 'Thinness', 'ADDRESS']+copyList
spatialDict = matchGeom(PWD_Parcels_Working, PWD_Field_List, PWD_Field_List.index('PARCELID'), PWD_Field_List.index('GROSS_AREA'), PWD_Field_List.index('POLY_AREA'), PWD_Field_List.index('Thinness'), copyList, PWD_Field_List.index('ADDRESS'), spatialDict, DOR_For_Spatial, copyList)

# Insert Spatial Dict into Flags Table
dorSpatialInsertCursor = arcpy.da.InsertCursor(Flags_Table_Temp, flagFields)
pwdIDDic = {r[0]:r for r in pwdAddressDict.values()}
testList = []
for k,v in spatialDict.items():
    if k in pwdIDDic:
        newV = {e:'|'.join([evv for evv in ev if evv is not None]) if type(ev) == list else ev for e,ev in v.items()}
        newV.update({e:None for e in flagFields if e not in v})
        review = ReviewType(newV)
        insertList = parsedZoning(review, k, newV, pwdIDDic, pwdAddressFields)
        dorSpatialInsertCursor.insertRow(insertList)
        completedList.append(k)
        testList.append(k)
del dorSpatialInsertCursor

# Need to run spatial join directly on remaining PWD Parcels that have not been matched
#Creating List of Parcels to ignore
dorMatchedPWD = arcpy.da.SearchCursor(Flags_Table_Temp, 'PWD_PARCEL_ID')
dorMatchedPWDList = [str(row[0]) for row in dorMatchedPWD]
del dorMatchedPWD

# Extract Remaining Parcels to separate featureclass
arcpy.FeatureClassToFeatureClass_conversion(PWD_Parcels_Working, localWorkspace, PWD_Parcels_Remaining, "PARCELID NOT IN ("+ ', '.join(dorMatchedPWDList) +')')

# Run PWD Parcels through Base Zoning
print('Applying Base Zoning to PWD Remain')
#print('Calculating Parcel Size')
#arcpy.AddField_management(DOR_Parcels_Local, 'PARCEL_AREA', 'FLOAT') #TODO Temp
#arcpy.CalculateGeometryAttributes_management(DOR_Parcels_Local, [['PARCEL_AREA', 'AREA']], area_unit='SQUARE_FEET_US') #TODO Temp
PWD_Base_Fields = ['PARCELID', 'GROSS_AREA', 'POLY_AREA',
        'Thinness', 'CODE', 'ADDRESS']
print('Beginning PWD Spatial Association')
pwdDict = {}
pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_Base_Fields, PWD_Base_Fields.index('PARCELID'),
                    PWD_Base_Fields.index('GROSS_AREA'), PWD_Base_Fields.index('POLY_AREA'),
                    PWD_Base_Fields.index('Thinness'), ['CODE'], PWD_Base_Fields.index('ADDRESS'),
                    pwdDict, Zon_BaseDistricts, ['Base_Zone'])

# Run PWD Parcels through Zoning Overlays
zoningLayer = 'zoningLayer'
specOverlayCursor = arcpy.da.SearchCursor(Zon_Overlays, 'OVERLAY_NAME')
overlayTypes = []
for row in specOverlayCursor:
    if row[0] not in overlayTypes:
        overlayTypes.append(row[0])
del specOverlayCursor


# Create a layer based off of each overlay type saved from previous list
print('Applying Zoning Overlay to PWD')
overlayTotal = len(overlayTypes)
overlayCount = 0
arcpy.MakeFeatureLayer_management(Zon_Overlays, zoningLayer)
parcelDict = {}
PWD_Overlay_fields = PWD_Base_Fields
PWD_Overlay_fields[PWD_Base_Fields.index('CODE')] = 'OVERLAY_NAME'
for overlayType in overlayTypes:
    overlayCount += 1
    print('Starting '+ overlayType +' overlay ' + str(overlayCount)+ ' of ' + str(overlayTotal))
    arcpy.SelectLayerByAttribute_management(zoningLayer, 'NEW_SELECTION', "OVERLAY_NAME = '" + overlayType.replace("'", '"') + "'")
    zoningCurrent = overlayType.lstrip('/') + '_layer'
    arcpy.MakeFeatureLayer_management(zoningLayer, zoningCurrent)
    pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_Overlay_fields, PWD_Overlay_fields.index('PARCELID'),
                        PWD_Overlay_fields.index('GROSS_AREA'),PWD_Overlay_fields.index('POLY_AREA'),
                        PWD_Overlay_fields.index('Thinness'), ['OVERLAY_NAME'],
                        PWD_Overlay_fields.index('ADDRESS'), pwdDict, zoningCurrent, ['Overlay_Zone'])

# Zoning RCO
print('Applying Zoning RCO to PWD')
PWD_RCO_fields = PWD_Overlay_fields
PWD_RCO_fields[4] = 'LNI_ID'
pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_RCO_fields, PWD_RCO_fields.index('PARCELID'),
                        PWD_RCO_fields.index('GROSS_AREA'),PWD_RCO_fields.index('POLY_AREA'),
                        PWD_RCO_fields.index('Thinness'), ['LNI_ID'],
                        PWD_RCO_fields.index('ADDRESS'), pwdDict, Zon_RCOs, ['ZONING_RCO'])

# PWD Green Roof
print('Applying Green Roof to PWD Parcels')
PWD_PWD_fields = PWD_Overlay_fields
PWD_PWD_fields[4] = 'PWD'
arcpy.MakeFeatureLayer_management(PWD_GSI_SMP_TYPES, PWD_Green_Roof, "SUBTYPE IN( 10 )")
pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_PWD_fields, PWD_PWD_fields.index('PARCELID'), PWD_PWD_fields.index('GROSS_AREA'),
                       PWD_PWD_fields.index('POLY_AREA'), PWD_PWD_fields.index('Thinness'), None,
                       PWD_PWD_fields.index('ADDRESS'), pwdDict, PWD_Green_Roof, ['GREEN ROOF'])

# PWD SMP Type Buffer
print('Applying PWD Buffer to PWD Parcels')
pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_PWD_fields, PWD_PWD_fields.index('PARCELID'), PWD_PWD_fields.index('GROSS_AREA'),
                       PWD_PWD_fields.index('POLY_AREA'), PWD_PWD_fields.index('Thinness'), None,
                       PWD_PWD_fields.index('ADDRESS'), pwdDict, PWD_GSI_SMP_Buffer, ['Green Infrastructure'])

# Floodplain
print('Applying Floodplain to DOR')
arcpy.AddField_management(Floodplain, 'Floodplain', 'TEXT', field_length='3')
PWD_Flood_fields = PWD_PWD_fields
PWD_Flood_fields[4] = 'Floodplain'
pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_Flood_fields, PWD_Flood_fields.index('PARCELID'), PWD_Flood_fields.index('GROSS_AREA'),
                       PWD_Flood_fields.index('POLY_AREA'), PWD_Flood_fields.index('Thinness'), None,
                       PWD_Flood_fields.index('ADDRESS'), pwdDict, Floodplain, ['Floodplain'])

# Steep Slope
print('Applying Steep Slope to PWD Parcels')
PWD_Slope_fields = PWD_Flood_fields
PWD_Slope_fields[4] = 'Steep_Slope'
pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_Slope_fields, PWD_Slope_fields.index('PARCELID'), PWD_Slope_fields.index('GROSS_AREA'),
                       PWD_Slope_fields.index('POLY_AREA'), PWD_Slope_fields.index('Thinness'), None,
                       PWD_Slope_fields.index('ADDRESS'), pwdDict, Zoning_SteepSlope, ['Steep_Slope'])

# Historic Properties
print('Applying Historic Areas')
PWD_Historic_fields = PWD_Slope_fields
PWD_Historic_fields[4] = 'Historic'
pwdDict = matchGeom(PWD_Parcels_Remaining, PWD_Historic_fields, PWD_Historic_fields.index('PARCELID'), PWD_Historic_fields.index('GROSS_AREA'),
                       PWD_Historic_fields.index('POLY_AREA'), PWD_Historic_fields.index('Thinness'), None,
                       PWD_Historic_fields.index('ADDRESS'), pwdDict, Hist_Sites_PhilReg, ['Historic'])

# Clean Dictionary for insertion
pwdIDFields = ['ADDRESS', 'PARCELID', 'Corner', 'GROSS_AREA', 'DISTRICT']
pwdIDCursor = arcpy.da.SearchCursor(PWD_Parcels_Remaining, pwdIDFields)
pwdIDDict = {row[pwdIDFields.index('PARCELID')]:row[:] for row in pwdIDCursor}
del pwdIDCursor
pwdDirectInsertCursor = arcpy.da.InsertCursor(Flags_Table_Temp, flagFields)
for k, v in pwdDict.items():
    print(k)
    pInfo = v
    inDict = {}
    pDict = {}
    inDict['BASE_ZONING'] = '|'.join(pInfo['Base_Zone']) if 'Base_Zone' in pInfo else None
    inDict['OVERLAY_ZONING'] = '|'.join(pInfo['Overlay_Zone']) if 'Overlay_Zone' in pInfo else None
    inDict['ZONING_RCO'] = '|'.join([str(z) for z in pInfo['ZONING_RCO']]) if 'ZONING_RCO' in pInfo else None
    if 'GREEN ROOF' in pInfo and 'Green Infrastructure' in pInfo:
        inDict['PWD_REVIEW_TYPE'] = pInfo['GREEN ROOF'] + '|' + pInfo['Green Infrastructure']
    elif 'GREEN ROOF' in pInfo:
        inDict['PWD_REVIEW_TYPE']  = pInfo['GREEN ROOF']
    elif 'Green Infrastructure' in pInfo:
        inDict['PWD_REVIEW_TYPE']  = pInfo['Green Infrastructure']
    else:
        inDict['PWD_REVIEW_TYPE'] = None
    inDict['FLOODPLAIN'] = 1 if 'Floodplain' in pInfo else None
    inDict['STEEP_SLOPE'] = 1 if 'Steep_Slope' in pInfo else None
    inDict['HISTORIC'] = 1 if 'Historic' in pInfo else None
    review = ReviewType(inDict)
    insertList = parsedZoning(review, k, inDict, pwdIDDict, pwdIDFields)
    pwdDirectInsertCursor.insertRow(insertList)
del pwdDirectInsertCursor

# Consolidate duplicate parcel ids
arcpy.TruncateTable_management(Flags_Table_Clean)
finalFields = [f.name for f in arcpy.ListFields(Flags_Table_Temp) if f.name != 'OBJECTID']
fOutCursor = arcpy.da.SearchCursor(Flags_Table_Temp, finalFields) #TODO Uncomment for prod
#fOutCursor = arcpy.da.SearchCursor(Flags_Table_Temp, finalFields, where_clause = "PWD_PARCEL_ID = 38804")
#fOutDict = {row[finalFields.index('PWD_PARCEL_ID')]:{f:row[finalFields.index(f)] for f in finalFields} for row in fOutCursor}
fInDict = {}
boolOutList = ['PAC_FLAG', 'PCPC_FLAG', 'PHC_FLAG', 'PWD_FLAG', 'FLOODPLAIN', 'STEEP_SLOPE']
tOutList = ['PAC_REVIEW_TYPE', 'PCPC_REVIEW_TYPE', 'PHC_REVIEW_TYPE', 'PWD_REVIEW_TYPE', 'BASE_ZONING', 'OVERLAY_ZONING', 'ZONING_RCO']
for row in fOutCursor:
    #print(fInDict)
    v = {f:row[finalFields.index(f)] for f in finalFields}
    if row[finalFields.index('PWD_PARCEL_ID')] not in fInDict:
        #print('Round 1')
        fInDict[row[finalFields.index('PWD_PARCEL_ID')]] = v
        #print(fInDict)
    else:
        #print('Round 2')
        # Text and boolean fields will be treated differently in this process
        # Boolean field values will always been overwritten by 1, otherwise they stay the same
        boolDict = {bk:bv for bk, bv in fInDict[row[finalFields.index('PWD_PARCEL_ID')]].items() if bk in boolOutList}
        # Text fields will be split into lists which will be appended to to and cleaned for dups
        tDict = {tK:tV for tK, tV in fInDict[row[finalFields.index('PWD_PARCEL_ID')]].items() if tK in tOutList}
        ##print(boolDict)
        #print(tDict)
        for nK, nV in {f:row[finalFields.index(f)] for f in finalFields}.items():
            if nK in boolDict:
                if nV == 1:
                    boolDict[nK] = 1
                    #print(boolDict)
            if nK in tDict:
                splitV = [] if tDict[nK] is None else tDict[nK].split('|')
                splitnV = [] if nV is None else nV.split('|')
                inV = splitV + splitnV
                tDict[nK] = '|'.join(list(set(inV)))
                #print(tDict)
        iV = {**boolDict, **tDict, **{lK:lV for lK, lV in v.items() if lK not in boolDict and lK not in tDict}}
        #print(iV)
        fInDict[row[finalFields.index('PWD_PARCEL_ID')]] = iV

fInCursor = arcpy.da.InsertCursor(Flags_Table_Clean, finalFields)
for v in fInDict.values():
    inList = [None] * len(finalFields)
    for i, f in enumerate(finalFields):
        inList[i] = v[f] if v[f] != '' else None
    #print(inList)
    fInCursor.insertRow(inList)
log.info('PR Flags Complete')
endTime = datetime.datetime.now()
print(endTime)
totalTime = endTime - startTime
print(totalTime)
"""
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
    recipientslist = ['DANI.INTERRANTE@PHILA.GOV', 'SHANNON.HOLM@PHILA.GOV', 'Philip.Ribbens@Phila.gov',
                      'LIGISTeam@phila.gov', 'Jessica.bradley@phila.gov']
    commaspace = ', '
    msg = MIMEText('AUTOMATIC EMAIL \n Plan Review Flags Update Failed during update: \n' + pymsg)
    msg['To'] = commaspace.join(recipientslist)
    msg['From'] = sender
    msg['X-Priority'] = '2'
    msg['Subject'] = 'Plan Review Flags Table Update Failure'
    server.server.sendmail(sender, recipientslist, msg.as_string())
    server.server.quit()
    sys.exit(1)
"""
# Create Layers for Each Review Type

CityAveSiteReview = ['/CAO City Avenue Overlay District - City Avenue Regional Center Area',
                     '/CAO City Avenue Overlay District - City Avenue Village Center Area']

