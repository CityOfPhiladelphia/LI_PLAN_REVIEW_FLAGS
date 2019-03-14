import arcpy

try:

    print("Let's see how this goes...")
    # IntersectOutput = 'G:\\Scripts\\li-queries\\PR_FLAGS\\Workspace.gdb' if zoneType == zonO else'in_memory\\'+zoningFC+'_Int'
    zoningFCLocal = 'G:\\Scripts\\li-queries\\PR_FLAGS\\Workspace.gdb\\ZoningBaseFromDB'
    IntersectOutput = 'G:\\Scripts\\li-queries\\PR_FLAGS\\Workspace.gdb\\' + zoningFC + '_Int'

    arcpy.RepairGeometry_management(zoningFCLocal)
    arcpy.Intersect_analysis([parcels] + [zoningFCLocal], IntersectOutput, 'ALL')
    print('Intersect Complete')

    # To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
    actualFields = [f.name for f in arcpy.ListFields(IntersectOutput)]
    print actualFields
    arcpy.AddField_management(IntersectOutput, 'Thinness', 'FLOAT')
    arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
    arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
    arcpy.CalculateField_management(IntersectOutput, 'Thinness',
                                    "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')
    fieldList = ['PARCELID', 'GROSS_AREA', 'POLY_AREA',
                 'Thinness', codefield]
    IntersectCursor = arcpy.da.SearchCursor(IntersectOutput, fieldList)
    countin = int(arcpy.GetCount_management(IntersectOutput).getOutput(0))
    count = 0
    print('Found ' + str(countin) + ' records in input table')
    breaks = [int(float(countin) * float(b) / 100.0) for b in range(10, 100, 10)]
    for row in IntersectCursor:
        count += 1
        if count in breaks:
            print('Parsing Zoning FC ' + str(int(round(count * 100.0 / countin))) + '% complete...')
        if row[
            0] in parcelDict:  # and (row[2] / float(row[1])) > 0.01: #and row[3] > 0.3 and (row[2] / float(row[1])) > 0.03:
            tempDict = parcelDict.get(row[0])
            oldList = tempDict.get(zoneType)
            tempDict[zoneType] = list(set([row[4]] + oldList))
            parcelDict[row[0]] = tempDict
    arcpy.Delete_management(IntersectOutput)
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