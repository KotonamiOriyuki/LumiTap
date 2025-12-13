# Backend of LumiTap
This REPO follows the modularization criteria since the number of components of the backend are large.

- We use different folders to classify different .py scripts (store models, accept API calls);
- We use seperate .py scripts for different functions (handling auth API calls and handling ranking API calls);
- We use definitions "def" to encapsulate each functions.

### run.py
Execute the FastAPI backend using uvicorn.

### app/
It stores all FastAPI components of LumiTap.

#### app/models
This stores all models required for API calls.

#### app/routes
This stores all actions required for API calls.

#### app/uploads
This stores all uploaded files by users.

#### app/utils
This stores other functions required for this project.