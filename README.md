# google-cloud-file-management

A management tool for using google cloud to sync data into your computer.  
Goal is to store assets in storage and sync them between multiple users.

# setup
1. Create a `config.py` file
2. Set the following parameters in the config file:
    - `CREDENTIAL_FILENAME` - this is the path of your google cloud storage credentials
    - `BUCKET_NAME` - this is the name of your bucket in google cloud storage
    - `USERNAME` - this can be set for individuals to track who made what changes
    - `WORKING_DIR_PATH` - path of the main project compare to the python file
    - `OLD_VERSION_DIR_PATH` - path older version directory to compare the changes to. The path should be relative to 
       the python file path. The folder material gets updated after every push or pull 
    - `IGNORES` - an array of the files to be ignored (no wild cards), for folders do not add "/" at the end of the name
    - An example config file:  
      `CREDENTIAL_FILENAME = "my_credentials.json"`   
      `BUCKET_NAME = "attempt1_mvk"`  
      `USERNAME = "John"`  
      `WORKING_DIR_PATH = "/"`  
      `OLD_VERSION_DIR_PATH = "/old_directiory/"`  
      `IGNORES = ["scripts", "old_directory", "venv", ".idea"]`
3. Run the following in terminal: `python3 main.py setup`

# How to use
When starting a project call the setup command to get a log files setup on your storage  
Then make sure to include the "logs.csv" in your IGNORES array
After this its simple, you can use the pull command to pull in the cloud's changes: `python3 main.py pull`    
And you can use the push command to push your changes to the cloud: `python3 main.py push`
