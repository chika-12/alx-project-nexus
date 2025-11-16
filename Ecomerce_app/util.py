import os
from dotenv import load_dotenv
load_dotenv()

def verify_env(env_string):
  variable = os.getenv(env_string)
  if variable is None:
    raise ValueError("Env variable is not reachable")
  return variable 
