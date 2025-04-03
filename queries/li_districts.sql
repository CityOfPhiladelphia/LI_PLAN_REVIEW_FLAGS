select 
	p.parcel_id,
	d.district
from
	viewer_pwd.pwd_parcels p
inner join
	li.li_districts d
on
    ST_INTERSECTS(ST_Centroid(p.shape), d.shape)