# cloudflare-dynamic-ip-updater

- [cloudflare-dynamic-ip-updater](#cloudflare-dynamic-ip-updater)
  - [Usage](#usage)
    - [How to get Cloudflare Credentials](#how-to-get-cloudflare-credentials)
    - [How to get Telegram Credentials](#how-to-get-telegram-credentials)
  - [Running the script](#running-the-script)
    - [Running with Python](#running-with-python)
    - [Running with Docker Compose](#running-with-docker-compose)

This is a simple script that updates a DNS record on Cloudflare with the current public IP address of the machine it is
running on.

## Usage

The script requires a `.env` file in the root directory with the following variables:

| Name              | Description            | Type   | Required |
|-------------------|------------------------|--------|----------|
| `BEARER_TOKEN`    | Cloudflare API token   | string | Yes      |
| `ZONE_ID`         | Cloudflare zone ID     | string | Yes      |
| `ACCOUNT_ID`      | Cloudflare account ID  | string | Yes      |
| `DNS_RECORD_ID`   | Cloudflare record ID   | string | Yes      |
| `DNS_RECORD_NAME` | Cloudflare record name | string | Yes      |
| `TL_API_KEY`      | Telegram bot API key   | string | Yes      |
| `TL_CHAT_ID`      | Telegram chat ID       | string | Yes      |

### How to get Cloudflare Credentials

To create a Cloudflare API token go to `Cloudflare Dashboard -> My Profile -> API Tokens -> Create Token -> Create Custom Token` and select the following: 

- Permissions:
  - `Zone -> Zone -> Read`
  - `Zone -> DNS -> Edit`
- Zone Resources:
  - `Include -> Specific Zone -> Select the zone you want to update`

And click `Continue to Summary` and `Create Token`.

To get the `ZONE_ID` and `ACCOUNT_ID` you can use the following command:

```bash
curl https://api.cloudflare.com/client/v4/zones \
-H "Authorization: Bearer $BEARER_TOKEN" \
-H "Content-Type: application/json"
```

From the response, you can get the `id` of the zone you want to update and from the `account` object you can get the `id` of the account.

To get the `DNS_RECORD_ID` and `DNS_RECORD_NAME` you can use the following command:

```bash
curl https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records \ 
-H "Authorization: Bearer $BEARER_TOKEN" \
-H "Content-Type: application/json"
```

From the response, you can get the `id` and `name` of the record you want to update.

### How to get Telegram Credentials

To create a Telegram bot and get the API key and chat ID follow the instructions [here](https://core.telegram.org/bots/tutorial).

## Running the script

To run the script you can choose between running it directly with Python or using Docker Compose.

### Running with Python

To run the script with Python you need to have Python 3.10 or higher installed. You can install the dependencies with the following command:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Run the script
python main.py
```

### Running with Docker Compose

To run the script with Docker Compose you need to have Docker and Docker Compose installed. You can run the script with the following command:

```bash
# Build and run the container
docker compose up --build -d

# Check the logs
docker compose logs -f

# Stop the container
docker compose down -v
```