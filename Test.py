#Run each review type through parcel flag function. This populates a dictionary that will eventually populate final table
    def parcelFlag(reviewName, reviewType, sourceFC, fieldCalculation, whereClause, outputFC, workspace, parcels,
                   parcelDict):
        reviewLayer = reviewType + '_' + reviewName
        IntersectOutput = workspace + '\\' + reviewName + 'Intersect'
        reviewField = 'CODE' if reviewType == zonB else 'OVERLAY_NAME' if reviewType == zonO else reviewName + 'ReviewReason'
        print reviewField
        '''
        if '_Buffer' in reviewName:
            print('Buffering')
            arcpy.Buffer_analysis(sourceFC, reviewLayer, '500 Feet', '', '', 'ALL')
        else:
            print('Creating Local FC for ' + reviewName)
            arcpy.FeatureClassToFeatureClass_conversion(sourceFC, workspace, reviewLayer,
                                                    whereClause)
        #All FCs except for Zoning are copied to LIGISDB
        if outputFC:
            'Copying FC to LIGISDB'
            arcpy.AddField_management(reviewLayer, reviewField, 'TEXT')
            arcpy.CalculateField_management(reviewLayer, reviewField, fieldCalculation)
            arcpy.TruncateTable_management(outputFC)
            arcpy.Append_management(reviewLayer, outputFC, 'NO_TEST')
        print('Performing Intersect')
        #Create polygons where review polygons overlap with parcels
        arcpy.Intersect_analysis([parcels]+[reviewLayer], IntersectOutput, 'ALL')
        print('Intersect Complete')
        arcpy.Delete_management(reviewLayer)
        #To ensure no slivers are included a thiness ratio and shape area are calculated for intersecting polygons
        arcpy.AddField_management(IntersectOutput, 'ThinessRatio', 'FLOAT')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'AREA', Area_Unit='SQUARE_FEET_US')
        arcpy.AddGeometryAttributes_management(IntersectOutput, 'PERIMETER_LENGTH', 'FEET_US')
        arcpy.CalculateField_management(IntersectOutput, 'ThinessRatio',
                                        "4 * 3.14 * !POLY_AREA! / (!PERIMETER! * !PERIMETER!)", 'PYTHON_9.3')
        '''
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
            if row[1] != '' and row[1] is not None and row[6] > 0.3 and (row[5] / float(row[4])) > 0.03 and row[
                7] != '':
                #If parcel has not made it into dictionary, parcel gets a new entry added
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