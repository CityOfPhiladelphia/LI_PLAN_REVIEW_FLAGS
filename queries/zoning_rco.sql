select 
	p.parcel_id, 
	string_agg(rco.organization_name, '| ') as rco_name
from 
	viewer_pwd.pwd_parcels p
inner join
	viewer_planning.zoning_rco rco
on
    ST_INTERSECTS(p.shape, rco.shape)
group by
	p.parcel_id