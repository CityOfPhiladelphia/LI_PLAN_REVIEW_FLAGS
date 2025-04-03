select distinct 
	pwd_parcel_id as parcel_id, 
	string_agg(distinct replace(zoning, '-', ''), '| ') as base_zoning_district
from
	viewer_ais.vw_address_servicearea_summary
where 
	pwd_parcel_id is not null
group by
	pwd_parcel_id