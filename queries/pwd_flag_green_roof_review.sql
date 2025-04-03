select 
	p.parcel_id 
from 
	viewer_pwd.pwd_parcels p
inner join
	(select 
		*
	from 
		viewer_pwd.gsi_smp_types 
	where 
		owner in ('PPRPWDMAINT', 'PRIVPWDMAINT', 'PWD')
		and subtype = 10) gsi
on
    ST_Intersects(p.shape, gsi.shape)