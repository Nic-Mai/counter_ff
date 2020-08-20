
# ff alarm

## Installation

### Install libraries:
```
pip install -r requirements.txt
```

### Install tesseract:
[https://github.com/tesseract-ocr/tesseract/wiki](https://github.com/tesseract-ocr/tesseract/wiki)

Ensure the *tesseract* executable is in your PATH. (open a command prompt and type "tesseract -v" to check)

## Usage

### Run script:
```
python main.py <left> <top> <width> <height> <auto_surrend (yes/no)> [<bot_url> <bot_token>]
```

### Parameters:

Adjust **left**, **top**, **width** and **height** parameters to match the chat position (type "/allcommands" to fill the chat with yellow text)

Preview should look like this:

![example](img/example.png "Example")

If **auto_surrend** is set to "yes", the script will automatically type "/ff".

If **bot_url** and **bot_token** are set, the script will request the bot.

Example (with 1440p monitor):
```
python main.py 10 1062 680 190 yes
```
