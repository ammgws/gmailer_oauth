# gmailer_oauth
CLI app to send emails (including attachments) using GMail with OAuth.

## Requirements
Python 3.6+
pip install -r requirements.txt

## Before Use
Use the [Google API Console](https://console.developers.google.com/apis/api) to create OAuth credentials for the GMail you want to send from.

 1. Click ｀My Project` and create a new project. After completion it will take you back to the main page.
 2. Click `Credentials` in the left pane and choose `OAuth client ID` from the `Create credentials` drop-down menu.
 3. Choose `Other` as the application type.
 4. Save the client ID and secret.

## Usage
### Command line

>Usage: gmailer_oauth.py [OPTIONS] RECIPIENT
>
>  todo.
>
>Options:
>  -s, --subject TEXT      Subject of the email to send.
>  -a, --attachment PATH   Path to attachment.
>  -c, --config_path PATH  Path to directory containing config file.
>  --dry-run
>  --help                  Show this message and exit.

### As a module
TO DO
```
import ...
```
