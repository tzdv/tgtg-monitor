from tgtg import TgtgClient
import time
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhook, DiscordEmbed


# client = TgtgClient(email="")
# credentials = client.get_credentials()
# print(credentials)

discord_hook_url = ""

access_token = ""
refresh_token = ""
user_id = ""
cookie = ""
client = TgtgClient(access_token=access_token, refresh_token=refresh_token, user_id=user_id, cookie=cookie)

CHECK_INTERVAL = 180


def send_webhook(item, hook_url):
    hook = DiscordWebhook(url=hook_url)
    embed = DiscordEmbed()
    embed.set_color(7000000)
    embed.add_embed_field(name="Your favourite bag has restocked!", value=item['name'])
    embed.add_embed_field(name="Address", value=item['address'], inline=False)
    embed.add_embed_field(name="Pickup window", value=item['time'], inline=False)
    embed.set_image(url=item["picture"])
    hook.add_embed(embed)
    hook.execute()


def format_item(items):
    formatted_items = {}
    print(items)
    for item in items:
        try:
            start_time = item['pickup_interval']['start']
            end_time = item['pickup_interval']['end']
            start_date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=1)
            end_date = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=1)
            start = start_date.strftime("%H:%M")
            end = end_date.strftime("%H:%M")
            date = end_date.strftime("%d/%m/%Y")
            pickup_window = f"{start}-{end} {date}"
        except KeyError:
            pickup_window = "None"

        favourite_bag = {
            "name": item["display_name"],
            "address": ', '.join(item["store"]["store_location"]["address"]["address_line"].split(", ")[:2]),
            "stock": item["items_available"],
            "picture": item["store"]["cover_picture"]["current_url"],
            "time": pickup_window,
        }
        formatted_items[item["item"]["item_id"]] = favourite_bag

    return formatted_items


def compare(current_favourite_items, previous_favourite_items):
    for item_id in current_favourite_items:
        if item_id in previous_favourite_items:
            current_stock = current_favourite_items[item_id]['stock']
            previous_stock = previous_favourite_items[item_id]['stock']
            if previous_stock == 0 and current_stock > 0:
                send_webhook(current_favourite_items[item_id], hook_url=discord_hook_url)


previous_favourite_items = format_item(client.get_items())
print("Monitoring your bags...")
while True:
    current_favourite_items = format_item(client.get_items())
    compare(current_favourite_items, previous_favourite_items)
    previous_favourite_items = current_favourite_items
    time.sleep(CHECK_INTERVAL)
