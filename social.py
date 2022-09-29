import datetime
import re
import requests

import feedparser

BLOG_START_COMMENT = '<!-- START_SECTION:blog -->'
BLOG_END_COMMENT = '<!-- END_SECTION:blog -->'

DOUBAN_START_COMMENT = '<!-- START_SECTION:douban -->'
DOUBAN_END_COMMENT = '<!-- END_SECTION:douban -->'

STEAM_GAME_START_COMMENT = '<!-- START_SECTION:steam_game -->'
STEAM_GAME_END_COMMENT = '<!-- END_SECTION:steam_game -->'


def generate_blog(rss_link, limit, readme) -> str:
    """Generate blog"""
    entries = feedparser.parse(rss_link)["entries"]
    arr = [
        {
            # "title": (entry["title"][0:20] + "...") if(len(entry["title"]) > 22) else entry["title"],
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries[:limit]
    ]

    print(arr)

    content = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in arr]
    )

    return generate_new_readme(BLOG_START_COMMENT, BLOG_END_COMMENT, content, readme)


def generate_douban(username, limit, readme) -> str:
    """Generate douban"""
    entries = feedparser.parse("https://www.douban.com/feed/people/" + username + "/interests")["entries"]
    arr = [
        {
            "title": item["title"],
            "url": item["link"].split("#")[0],
            "published": format_time(item["published"])
        }
        for item in entries[:limit]
    ]

    content = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in arr]
    )

    return generate_new_readme(DOUBAN_START_COMMENT, DOUBAN_END_COMMENT, content, readme)


def generate_steam_game(steam_api_key, steam_id, limit, readme) -> str:
    r = requests.get(
        "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={0}&steamid={1}".format(
            steam_api_key, steam_id
        )
    )
    print(steam_api_key)
    print(steam_id)
    print(r.text)
    recent_games = [
        {
            "url": "https://store.steampowered.com/app/" + str(item["appid"]),
            "name": item["name"],
            "playtime_2weeks": format(item["playtime_2weeks"] / 60, ".2f")
        }
        for item in r.json()["response"]["games"][:limit]
    ]

    content = "\n".join(
        ["* <a href='{url}' target='_blank'>{name}</a> - 最近游戏时长: {playtime_2weeks} h".format(**item) for item in recent_games]
    )

    return generate_new_readme(STEAM_GAME_START_COMMENT, STEAM_GAME_END_COMMENT, content, readme)


def generate_steam_icon_url() -> str:
    pass


def generate_new_readme(start_comment: str, end_comment: str, content: str, readme: str) -> str:
    """Generate a new Readme.md"""
    pattern = f"{start_comment}[\\s\\S]+{end_comment}"
    repl = f"{start_comment}\n{content}\n{end_comment}"
    if re.search(pattern, readme) is None:
        print(f"can not find section in your readme, please check it, it should be {start_comment} and {end_comment}")

    return re.sub(pattern, repl, readme)


def format_time(timestamp) -> datetime:
    gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
    date_str = datetime.datetime.strptime(timestamp, gmt_format) + datetime.timedelta(hours=8)
    return date_str.date()
