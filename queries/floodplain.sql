select 
	p.parcel_id 
from 
	viewer_pwd.pwd_parcels p
inner join
	viewer_planning.fema_100_flood_plain fp100
on
    ST_INTERSECTS(p.shape, fp100.shape)