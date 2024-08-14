# Foxydownloader

Script to download SGF-Files from Fox Weiqi
- fixing the strange Komi format of Fox
- encode shift_jis
- Convert User ID to real name (professional go player)

Script to download SGF-Files from Golaxy
- encode shift_jis


## Requirements
- python v3.x
- the modules `simple-term-menu`, `pyyaml`, `appdirs`, and `python-dotenv`
  ``` 
  pip install simple-term-menu pyyaml appdirs python-dotenv
  ```
  Note that `simple-term-menu` doesn't work in Windows terminals. If you are using Windows it's best to us this script from the Windows Subsystem for Linux (WSL, https://docs.microsoft.com/en-us/windows/wsl/install)


## Configuration
`.env`file
Golaxy user id
```
USER_ID=0000-0000000000
```


## Usage 
``` 
python /path/to/foxydownloader.py 
```

## Thanks
to the people in this thread https://github.com/featurecat/go-dataset/issues/1 whose code was mainly adapted here
