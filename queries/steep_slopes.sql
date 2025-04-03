select 
	p.parcel_id 
from 
	viewer_pwd.pwd_parcels p
inner join
	viewer_planning.zoning_steepslopeprotectarea_r ss
on
    ST_INTERSECTS(p.shape, ss.shape)