import tomllib

with open(".streamlit/secrets.toml", "rb") as f:
    config = tomllib.load(f)

env = config["env"]

postgres_conn = 'temp'

match env:
    case "prod":
        postgres_conn = "remote_postgresql"
        
    case "dev":
        postgres_conn = "local_postgresql"
        
    case _:
        raise ValueError(f"Unknown environment: {env}")