# Build
In order to build the application, temporarily move main.py to root folder and run the following command in project's root folder:
```
pyinstaller --debug=imports `
    --add-data "joyshockgraphic/resources/;joyshockgraphic/resources/" `
    --paths "joyshockgraphic/database" `
    --paths "joyshockgraphic/input" `
    --paths "joyshockgraphic/ui" `
    --noconsole `
    --icon "joyshockgraphic/resources/icons/joyshockgraphic.ico" `
    "main.py"
```
