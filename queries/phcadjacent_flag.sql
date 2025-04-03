select 
	p.parcel_id 
from 
	viewer_pwd.pwd_parcels p
inner join
	viewer_planning.historic_sites_philreg hist
on
    ST_DWithin(p.shape, hist.shape, 5)
where
	p.parcel_id not in (
	SELECT  
		p.parcel_id
	FROM 
		viewer_pwd.pwd_parcels p 
	INNER JOIN 
		viewer_planning.historic_sites_philreg hist 
	ON
	    ST_INTERSECTS(p.shape, hist.shape)
	WHERE 
		ST_Area(ST_Intersection(p.shape, hist.shape)) / ST_Area(p.shape) >= 0.05)