select 
	p.parcel_id 
from 
	viewer_pwd.pwd_parcels p
inner join
	li.li_pr_corner_properties cp
on
    ST_INTERSECTS(ST_Centroid(p.shape), cp.shape)