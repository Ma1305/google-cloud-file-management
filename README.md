# google-cloud-file-management

A management tool for using google cloud to sync data into your computer.  
Goal is to store assets in storage and sync them between multiple users.

# setup
1. Create a `config.py` file
2. Set the following parameters in the config file:
    - `CREDENTIAL_FILENAME` - this is the path of your google cloud storage credentials
    - `BUCKET_NAME` - this is the name of your bucket in google cloud storage
    - `USERNAME` - this can be set for individuals to track who made what changes
    - `IGNORES` - an array of the files to be ignored (no wild cards), for folders do not add "/" at the end of the name
    - An example config file:  
      `CREDENTIAL_FILENAME = "my_credentials.json"`   
      `BUCKET_NAME = "attempt1_mvk"`  
      `USERNAME = "John"`  
      `IGNORES = ["scripts", "prev_version", "venv", ".idea"]`
3. Run the following in terminal: `python3 main.py setup`
4. [Optional] if you already have any of the files on your computer, 
you can use the following to set them up in google storage: `python3 main.py upload-all`
5. [Optional] if you already have any of the files on google cloud, 
you can use the following to set them up on your computer: `python3 main.py download-all`

# How to use


# How it works