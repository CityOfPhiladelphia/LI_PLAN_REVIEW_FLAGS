select distinct
    row_number() OVER () AS objectid,
    parcel_id pwd_parcel_id,
    address,
    gross_area as parcel_area
from
    viewer_pwd.pwd_parcels