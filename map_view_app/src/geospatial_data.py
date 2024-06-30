import keyring
from sqlalchemy import create_engine
import psycopg2
import geopandas as gpd


horton_password = keyring.get_password('reef', 'horton_password')

con = create_engine(f'postgresql://data_science:{horton_password}@btanalytics.mlops.reefplatform.com:5432/bt_analytics')

gdf = gpd.read_postgis("""
select gid, gid::text as name, msa_short as msa, attractive as geoscore, geom
from census.na_heatmap nh 
union
select gid, gid::text || ' (' || postcode || ') - ' || name as name, msa_name || ', ' || ctrycode as msa, bracket as geoscore, geom
from census.eu_heatmap eh;
""", con)

print(type(gdf))
