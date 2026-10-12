# adapter-design-api

## API (Adapter Design)

As we are considering the web portal is read-only, there are three APIs created. 
1. GET a meter
2. INDEX of all meters
3. SEARCH among all meters (meter number or serial)

## Setup

1. Create a file named ```.env``` with following content.
  ````
   FLOCK_API_TOKEN=K7vQm2xN9pL4sR8wT3yH6cD1fG5jB0aZ_UpEoI7kXmN
   SESSION_COOKIE=*paste from inspect section of logged in browser window*
  ````
2. Run the server
  ````
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ````

## File structure

1. Config file

   For all configuration for the app.
   All secrets and portal URLs all defined here.

2. api_client file

   For all APIs, call to underlying Flock API is done here.

3. html_parser file

   The response from Flock API is parsed and converted to json form here.

4. main.py file

   This has all APIs and all the above files imported here.
