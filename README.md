# Loquacious SMTP Dispatcher

Loquacious SMTP Dispatcher is a small Python command-line tool that sends HTML
emails to contacts through an SMTP server. Contacts are loaded from CSV files,
email bodies are loaded from HTML files, and each outgoing message can include
custom headers.

## Features

- Load contacts from one CSV file or from every `.csv` file in a contacts
  directory.
- Load email templates from one HTML file or from every `.html` file in an
  emails directory.
- Send each HTML email to each contact through SMTP.
- Add custom headers with `--header "Header-Name=Header value"`.
- Override the default `From` and `Message-ID` headers with custom headers.
- Use CSV columns as placeholders in the subject, HTML body, and custom headers.
- Generate a valid `Message-ID` header for each message.
- Run in `--dry-run` mode to check what would be sent without connecting to SMTP.

## Project Layout

```text
loquacious/
  __main__.py        # CLI entry point
  smtp_app.py        # Application flow: load contacts/templates and send emails
  smtp_bridge.py     # SMTP delivery
  smtp_config.py     # Runtime configuration
  smtp_contact.py    # Contact model
  smtp_message.py    # Email message model
contacts/
  contacts.csv
emails/
  welcome.html
```

## Contacts CSV

At minimum, each contact row must contain an `email` column. A `name` column is
optional. Any additional column is kept and can be used as a template
placeholder.

```csv
contact_id,name,email,company
ada, Ada Lovelace,ada@example.com,Analytical Engines Ltd
grace, Grace Hopper,grace@example.com,Compiler Labs
```

## HTML Email Templates

Create one or more `.html` files in the emails directory. Template placeholders
use Python format syntax and match CSV column names.

```html
<h1>Hello {name}</h1>
<p>We are contacting you at {company}.</p>
```

If no subject is provided with `--subject`, the file name is used as the
subject. For example, `welcome_email.html` becomes `welcome email`.

## Usage

Run the project as a Python module:

```bash
python -m loquacious \
  --contacts-path contacts \
  --emails-path emails \
  --smtp-server smtp.example.com \
  --smtp-port 587 \
  --smtp-username user@example.com \
  --smtp-password "your-password" \
  --sender-email user@example.com \
  --sender-name "Example Team" \
  --subject "Hello {name}" \
  --header "X-Campaign=welcome" \
  --header "X-Company={company}" \
  --header "From=Custom Sender <custom@example.com>" \
  --header "Message-ID=<welcome-{contact_id}@example.com>"
```

Check the loaded contacts and templates without sending email:

```bash
python -m loquacious \
  --contacts-path contacts \
  --emails-path emails \
  --sender-email user@example.com \
  --dry-run
```

## Configuration With Environment Variables

Most options can also be provided through environment variables:

```bash
export LOQUACIOUS_CONTACTS_PATH=contacts
export LOQUACIOUS_EMAILS_PATH=emails
export LOQUACIOUS_SMTP_SERVER=smtp.example.com
export LOQUACIOUS_SMTP_PORT=587
export LOQUACIOUS_SMTP_USERNAME=user@example.com
export LOQUACIOUS_SMTP_PASSWORD=your-password
export LOQUACIOUS_SENDER_EMAIL=user@example.com
export LOQUACIOUS_SENDER_NAME="Example Team"
export LOQUACIOUS_SUBJECT="Hello {name}"
```

Command-line options override environment variables when both are provided.
