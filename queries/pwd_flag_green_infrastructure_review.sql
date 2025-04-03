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
		owner in ('PPRPWDMAINT', 'PRIVPWDMAINT', 'PWD')) gsi
on
    ST_DWithin(p.shape, gsi.shape, 50)