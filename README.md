# gmailer_oauth
CLI app to send emails using GMail with OAuth.

## Why?
Security - your Gmail password is never used or saved on the system.

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
```
Usage: gmailer_oauth.py [OPTIONS] RECIPIENT

  TODO.

Options:
  -m, --message TEXT        Message to send in email body.
  -s, --subject TEXT        Subject of the email to send.
  -a, --attachment PATH     Path to attachment.
  -c, --cc TEXT             Carbon copy recipient.
  -b, --bcc TEXT            Blind carbon copy recipient.
  --client-id TEXT          Google OAUTH client ID.
  --client-secret TEXT      Google OAUTH client secret.
  --config-path PATH        Path to directory containing config file.
  --cache-path PATH         Path to directory to store logs and such.
  --dry-run
  -i, --interactive
  --help                    Show this message and exit.
```

### As a module
TO DO
```
import ...
```
