import base64
import os
import sys
from github import Github, GithubException

import social

REPOSITORY = os.getenv('INPUT_REPOSITORY')
GHTOKEN = os.getenv('INPUT_GH_TOKEN')

COMMIT_MESSAGE = os.getenv("INPUT_COMMIT_MESSAGE")

BLOG_RSS_LINK = os.getenv('INPUT_BLOG_RSS_LINK')
BLOG_LIMIT = int(os.getenv('INPUT_BLOG_LIMIT'))

DOUBAN_NAME = os.getenv('INPUT_DOUBAN_NAME')
DOUBAN_LIMIT = int(os.getenv('INPUT_DOUBAN_LIMIT'))

STEAM_API_KEY = os.getenv('INPUT_STEAM_API_KEY')
STEAM_GAME_LIMIT = int(os.getenv("INPUT_STEAM_GAME_LIMIT"))
STEAM_USER_ID64 = os.getenv("INPUT_STEAM_USER_ID64")


def decode_readme(data: str) -> str:
    """Decode the contents of old readme"""
    decoded_bytes = base64.b64decode(data)
    return str(decoded_bytes, 'utf-8')


if __name__ == "__main__":
    g = Github(GHTOKEN)
    try:
        repo = g.get_repo(REPOSITORY)
    except GithubException:
        print(
            "Authentication Error. Try saving a GitHub Token in your Repo Secrets or Use the GitHub Actions Token, which is automatically used by the action.")
        sys.exit(1)
    contents = repo.get_readme()

    old_readme = decode_readme(contents.content)
    new_readme = old_readme

    if BLOG_RSS_LINK is not None and BLOG_LIMIT > 0:
        print("BLOG_RSS_LINK:" + BLOG_RSS_LINK)
        print("BLOG_LIMIT:" + str(BLOG_LIMIT))
        new_readme = social.generate_blog(BLOG_RSS_LINK, BLOG_LIMIT, new_readme)

    if DOUBAN_NAME is not None and DOUBAN_LIMIT > 0:
        print("DOUBAN_NAME:" + DOUBAN_NAME)
        print("DOUBAN_LIMIT:" + str(DOUBAN_LIMIT))
        new_readme = social.generate_douban(DOUBAN_NAME, DOUBAN_LIMIT, new_readme)

    if STEAM_API_KEY is not None and STEAM_USER_ID64 is not None and STEAM_GAME_LIMIT > 0:
        print("STEAM_GAME_LIMIT: " + str(STEAM_GAME_LIMIT))
        new_readme = social.generate_steam_game(STEAM_API_KEY, STEAM_USER_ID64, STEAM_GAME_LIMIT, new_readme)
        new_readme = social.generate_steam_icon_url(STEAM_API_KEY, STEAM_USER_ID64, new_readme)

    if new_readme == old_readme:
        print("nothing changed")
    else:
        print("readme change, start update...")
        repo.update_file(path=contents.path, message=COMMIT_MESSAGE,
                         content=new_readme, sha=contents.sha)
        print("your readme update completed!")
