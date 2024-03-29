# L&I Plan Review Flags For Eclipse
This process was originally planned to support the ArcGIS Feature Service: [Plan Review Flags Eclipse](http://phl.maps.arcgis.com/home/item.html?id=7a474e2bb78b4f258751e22161e4cc75).  This has been since modified to support the GIS_LNI.LI_PR_FLAG_SUMMARY table on DataBridge gis_sde_viewer.  This table represents applicable zoning review data based on that parcel's [PWD_PARCEL's](http://metadata.phila.gov/#home/datasetdetails/5543864620583086178c4e7a/representationdetails/55438a829b989a05172d0cfa/) geometry in GIS.  

## Property Data Displayed with table
### Inspection Districts
<pre>LI_INSPECTION_DISTRICT</pre>
The L&I inspection district responsible to the property

### Corner Properties
<pre>CORNER_PROPERTY</pre>
Produced from a one-time GIS analysis of PWD Parcels and their proximity to street centerlines.  There is no plan to automate this process, but parcels incorrectly labeled as 'corner properties' can be manually removed by L&I BIDV/GIS upon request.

### Philadelphia Art Commission (PAC) Review
<pre>PAC_FLAG</pre>
The PAC review layer indicates one of three review types:
* **Building ID Signage Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Basemap as:<br>
  * ICMX
  * I-1
  * IRMX
* **Parkway Buffer Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:<br>
  * CTR Center City Overlay District - Parkway Buffer
* **Signage Special Control -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:<br>
  * CTR Center City Overlay District - Rittenhouse Square
  * CTR Center City Overlay District - Center City Commercial Area
  * CTR Center City Overlay District - Convention Center Area
  * CTR Center City Overlay District - Independence Hall Area
  * CTR Center City Overlay District - Vine Street Area
  * CTR Center City Overlay District - Washington Square
  * NCA Neighborhood Commercial Area Overlay District - East Falls Neighborhood
  * NCA Neighborhood Commercial Area Overlay District - Germantown Avenue
  * NCA Neighborhood Commercial Area Overlay District - Main Street/Manayunk and Venice Island
  * NCA Neighborhood Commercial Area Overlay District - Logan Triangle
  * NCA Neighborhood Commercial Area Overlay District - Ridge Avenue
  * NCA Neighborhood Commercial Area Overlay District - Lower and Central Germantown
  * NCA Neighborhood Commercial Area Overlay District - North Delaware Avenue
  * NCA Neighborhood Commercial Area Overlay District - Spring Garden
  * Accessory Sign Controls - Special Controls for Cobbs Creek, Roosevelt Boulevard, and Department of Parks and Recreation Land
  * NCA Neighborhood Commercial Area Overlay District - Germantown Avenue - Mount Airy Subarea
  
  

### Philadelphia City Planning Commission (PCPC) Review
<pre>PCPC_FLAG</pre>
The PCPC review layer indicates one of eight review types, although two (100 Year Floodplain and Steep Slopes) reside in their own data layers:
* **City Ave Site Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:
  * CAO City Avenue Overlay District - City Avenue Regional Center Area
  * CAO City Avenue Overlay District - City Avenue Village Center Area
* **Ridge Ave Facade Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:
  * NCA Neighborhood Commercial Area Overlay District - Ridge Avenue
* **Master Plan Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Basemap as:
  * RMX-1
  * RMX-2
  * SP-ENT
  * SP-INS
  * SP-STA
* **Center City Facade Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:
  * CTR Center City Overlay District - Chestnut and Walnut Street Area
  * CTR Center City Overlay District - Broad Street Area South
  * CTR Center City Overlay District - Market Street Area East
* **Neighborhood Conservation Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:
  * NCO Neighborhood Conservation Overlay District - Central Roxborough
  * NCO Neighborhood Conservation Overlay District - Overbrook Farms
  * NCO Neighborhood Conservation Overlay District - Powelton Village Zone 1
  * NCO Neighborhood Conservation Overlay District - Powelton Village Zone 2
  * NCO Neighborhood Conservation Overlay District - Queen Village
  * NCO Neighborhood Conservation Overlay District - Ridge Park Roxborough
* **Wissahickon Watershed Site Review -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:
  * WWO Wissahickon Watershed Overlay District
* **GermantownMtAirySubareaFacadeReview -** This review is triggered on areas defined by the City of Philadelphia's Zoning Overlay Map as:
  * NCA Neighborhood Commercial Area Overlay District - Germantown Avenue - Mount Airy Subarea

#### 100 Year Floodplain Review (1% Chance of annual flood)
<pre>FLOODPLAIN</pre>
A floodplain review is triggered on areas defined as the 100 Year Floodplain/1% Chance Annual Flood by the FEMA Floodplain map.

#### Steep Slope Review
<pre>STEEP_SLOPE</pre>
A steep slope review is triggered on areas that fall within the bounds of the Steep Slope Overlay as defined by city ordinance [14-704(2)](http://library.amlegal.com/nxt/gateway.dll/Pennsylvania/philadelphia_pa/title14zoningandplanning/chapter14-700developmentstandards?f=templates$fn=default.htm$3.0$vid=amlegal:philadelphia_pa$anc=JD_14-704(2)) .

### Philadelphia Historic Commission (PHC) Review
<pre>PHC_FLAG</pre>
The PHC review layer indicates a historic review flag.  A historic review is triggered on areas that are defined by the Philadelphia Register of Historic Places.

### Philadelphia Water Department (PWD) Plan Review
<pre>PWD_FLAG</pre>
The PWD review layer indicates a one of two PWD related reviews:
* **Green Roof Review -** This review is triggered on any property that houses a green roof as located within the Philadelphia Water Department's Green Stormwater Infrasture Project dataset.
* **Green Stormwater Infrastructure Buffer -** This review is triggered on any property that falls within a 50 foot buffer of any green infrastructure project as located within Philadelphia Water Department's Green Stormwater Infrasture Project dataset.

