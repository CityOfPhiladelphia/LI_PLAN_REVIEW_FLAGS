select 
	p.parcel_id, 
	string_agg(zo.overlay_name, '| ') as zoning_overlay_district
from 
	viewer_pwd.pwd_parcels p
inner join
	viewer_planning.zoning_overlays zo
on
    ST_INTERSECTS(p.shape, zo.shape)
group by
	p.parcel_id