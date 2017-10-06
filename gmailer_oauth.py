# Standard library
import base64
import datetime as dt
import logging
import mimetypes
import os.path
from configparser import ConfigParser
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Third party
import click
import requests
from google_auth import GoogleAuth

APP_NAME = 'gmail-oauth'


def create_message_with_attachment(to, subject, message_text, attachment):
    """Returns a RFC2387 formatted email message as base64url encoded byte string.

    Maximum file size: 35MB.
    """

    message = MIMEMultipart('related')
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(message_text, _subtype='plain', _charset='UTF-8'))

    content_type, encoding = mimetypes.guess_type(attachment)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    handlers = {
        'text': MIMEText,
        'image': MIMEImage,
        'audio': MIMEAudio,
    }
    handler = handlers.get(main_type, MIMEBase)
    with open(attachment, 'rb') as f:
        part = handler(f.read(), _subtype=sub_type)
        if handler is MIMEBase:
            part.set_payload(f.read())

    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
    message.attach(part)

    return message.as_bytes()


def create_message(to, subject, message_text):
    """Returns a RFC2822 formatted email message as a base64url encoded string."""
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')}


@click.command()
@click.argument('recipient')
@click.option(
    '--message', '-m',
    default='',
    help='Message to send in email body.',
)
@click.option(
    '--subject', '-s',
    default='',
    help='Subject of the email to send.',
)
@click.option(
    '--attachment', '-a',
    type=click.Path(exists=True),
    help='Path to attachment.',
)
@click.option(
    '--client-id', '-i',
    type=click.STRING,
    help='Google OAUTH client ID.',
)
@click.option(
    '--client-secret', '-k',
    type=click.STRING,
    help='Google OAUTH client ID.',
)
@click.option(
    '--config-path',
    default=os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), APP_NAME),
    type=click.Path(exists=True),
    help='Path to directory containing config file.',
)
@click.option(
    '--cache-path',
    type=click.Path(exists=True),
    default=os.path.join(os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache')), APP_NAME),
    help='Path to directory to store logs and such.',
)
@click.option('--dry-run', is_flag=True)
@click.option('--interactive', '-i', is_flag=True)
def main(config_path, recipient, message, subject, attachment, dry_run, client_id, client_secret):
    """TODO.
    """

    # TODO: make logging optional
    configure_logging(config_path)

    # TODO: import from Google provided json file？
    # TODO: config from env vars
    cache_dir = os.path.join(os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache')), APP_NAME)
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    config_file = os.path.join(config_path, 'config.ini')
    logging.debug('Using config file: %s', config_file)
    config = ConfigParser()
    config.read(config_file)
    client_id = config.get('Gmail', 'client_id')
    client_secret = config.get('Gmail', 'client_secret')
    refresh_token_file = os.path.join(cache_dir, 'refresh_token')

    # Setup Google OAUTH instance for accessing Gmail
    scopes = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/userinfo.email',
    ]
    oauth = GoogleAuth(client_id, client_secret, scopes, refresh_token_file)
    oauth.authenticate()

    # TODO: authentication failure error handling

    # Create and send email
    # see https://developers.google.com/gmail/api/guides/uploads
    #     https://developers.google.com/gmail/api/v1/reference/users/messages/send
    if attachment:
        url = 'https://www.googleapis.com/upload/gmail/v1/users/me/messages/send?uploadType=multipart'
        headers = {
            'Authorization': f'Bearer {oauth.access_token}',
            'Content-Type': 'message/rfc822'
        }
        message_body = create_message_with_attachment(
                to=recipient,
                subject=subject,
                message_text=message,
                attachment=attachment,
        )
        req = requests.Request('POST', url, headers=headers, data=message_body)
    else:
        url = 'https://www.googleapis.com/gmail/v1/users/me/messages/send'
        headers = {'Authorization': f'Bearer {oauth.access_token}'}
        message_body = create_message(
                to=recipient,
                subject=subject,
                message_text=message,
        )
        req = requests.Request('POST', url, headers=headers, json=message_body)

    req = req.prepare()
    if dry_run:
        print(req.headers)
        print(req.body)
    else:
        s = requests.Session()
        r = s.send(req)
        logging.debug(r.status_code)
        logging.debug(r.content)

        if r.status_code == 200:
            logging.info('Successfully sent mail from %s.', oauth.get_email())
        else:
            logging.error('Something went wrong. Response from Google: %s.', r.content)


def configure_logging(log_dir):
    # Configure root logger. Level 5 = verbose to catch mostly everything.
    logger = logging.getLogger()
    logger.setLevel(level=5)

    log_folder = os.path.join(log_dir, 'logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_filename = '{0}.log'.format(dt.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss'))
    log_filepath = os.path.join(log_folder, log_filename)
    log_handler = logging.FileHandler(log_filepath)

    log_format = logging.Formatter(
        fmt='%(asctime)s.%(msecs).03d %(name)-12s %(levelname)-8s %(message)s (%(filename)s:%(lineno)d)',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    # Lower requests module's log level so that OAUTH2 details aren't logged
    logging.getLogger('requests').setLevel(logging.WARNING)


if __name__ == '__main__':
    main()
