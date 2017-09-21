# Standard library
import base64
import datetime as dt
import logging
import mimetypes
import os.path
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Third party imports
import click
import requests
# Custom imports
from google_auth import GoogleAuth


def create_message_with_attachment(to, subject, message_text, attachment):
    """Returns a RFC2387 formatted email message as base64url encoded byte string.

    Maximum file size:Returns an  35MB
    """

    # The body of the request is formatted as a multipart/related content type [RFC2387]
    # and contains exactly two parts. The parts are identified by a boundary string, and
    # the final boundary string is followed by two hyphens.

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
    """Returns a RFC2822 formatted email message as a base64url encoded  """
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')}


@click.command()
@click.argument('recipient')
@click.option('--message', '-m',
              default='',
              help='Message to send in email body.',
              )
@click.option('--subject', '-s',
              default='',
              help='Subject of the email to send.',
              )
@click.option('--attachment', '-a',
              type=click.Path(exists=True),
              help='Path to attachment.',
              )
@click.option('--config_path', '-c',
              default=os.path.expanduser('~/.config/gmail-oauth'),
              type=click.Path(exists=True),
              help='Path to directory containing config file.',
              )
@click.option('--dry-run', is_flag=True)
def main(config_path, recipient, message, subject, attachment, dry_run):
    """
    todo.
    """

    # TODO: make logging optional
    configure_logging(config_path)

    # TODO: import from Google provided json file
    # TODO: config from env vars
    # TODO: use XDG_CONFIG instead of hardcoded
    # Path to config file
    config_file = os.path.join(config_path, 'config.ini')
    logging.debug('Using config file: %s', config_file)

    # Setup Google OAUTH instance for accessing Gmail
    oauth2_scope = ('https://www.googleapis.com/auth/gmail.send '
                    'https://www.googleapis.com/auth/userinfo.email')
    oauth = GoogleAuth(config_file, oauth2_scope, service='Gmail')
    oauth.authenticate()

    # Create and send email
    # see https://developers.google.com/gmail/api/guides/uploads
    #     https://developers.google.com/gmail/api/v1/reference/users/messages/send
    if attachment:
        request_url = 'https://www.googleapis.com/upload/gmail/v1/users/me/messages/send?uploadType=multipart'
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
        resp = requests.post(request_url, headers=headers, data=message_body)
    else:
        request_url = 'https://www.googleapis.com/gmail/v1/users/me/messages/send'
        headers = {'Authorization': f'Bearer {oauth.access_token}'}
        message_body = create_message(
                to=recipient,
                subject=subject,
                message_text=message,
        )
        resp = requests.post(request_url, headers=headers, json=message_body)

    if dry_run:
        req = requests.Request('POST', request_url, headers=headers, data=message_body).prepare()
        print(req.headers)
        print(req.body)
    else:
        logging.debug(resp.status_code)
        logging.debug(resp.content)

        if resp.status_code == 200:
            logging.info('Successfully sent mail from %s.', oauth.get_email())
        else:
            logging.error('Something went wrong. Response from Google: %s', resp.content)


def configure_logging(config_path):
    # Configure root logger. Level 5 = verbose to catch mostly everything.
    logger = logging.getLogger()
    logger.setLevel(level=5)

    log_folder = os.path.join(config_path, 'logs')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder, exist_ok=True)

    log_filename = '{0}.log'.format(dt.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss'))
    log_filepath = os.path.join(log_folder, log_filename)
    log_handler = logging.FileHandler(log_filepath)

    log_format = logging.Formatter(
            fmt='%(asctime)s.%(msecs).03d %(name)-12s %(levelname)-8s %(message)s (%(filename)s:%(lineno)d)',
            datefmt='%Y-%m-%d %H:%M:%S')
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    # Lower requests module's log level so that OAUTH2 details aren't logged
    logging.getLogger('requests').setLevel(logging.WARNING)


if __name__ == '__main__':
    main()
