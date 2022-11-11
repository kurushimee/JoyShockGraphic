# Build
In order to build the application, run the following command in project's root folder:
```
pyinstaller --add-data "joyshockgraphic/resources/;joyshockgraphic/resources/" `
    --noconsole `
    --icon "joyshockgraphic/resources/icons/joyshockgraphic.ico" `
    "joyshockgraphic/main.py"
```
