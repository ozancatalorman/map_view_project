import keyring
from sqlalchemy import create_engine
import psycopg2
import geopandas as gpd

def generate_parquet():
    horton_password = keyring.get_password('reef', 'horton_password')

    # horton_password = "Dm[9.QxAXdx{3k1"

    connection = create_engine(
        f'postgresql://data_science:{horton_password}@btanalytics.mlops.reefplatform.com:5432/bt_analytics')

    geo_df = gpd.read_postgis("""
    select gid, gid::text as name, msa_short as msa, attractive as geoscore, geom
    from census.na_heatmap nh 
    union
    select gid, gid::text || ' (' || postcode || ') - ' || name as name, msa_name || ', ' || ctrycode as msa, bracket as geoscore, geom
    from census.eu_heatmap eh;
    """, connection)

    return geo_df



