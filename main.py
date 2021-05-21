import os
from os.path import dirname, join
import praw, time, calendar
from praw import Reddit
from prettytable import PrettyTable
from praw.models import MoreComments
from colorama import init, Fore, Back, Style
from dotenv import load_dotenv

load_dotenv(join(dirname(__file__), '.env'))
reddit_app_client_id = os.environ.get("REDDIT_APP_CLIENT_ID")
reddit_app_secret = os.environ.get("REDDIT_APP_SECRET")

print(reddit_app_client_id)
print(reddit_app_secret)

init()
reddit = praw.Reddit(
    client_id=reddit_app_client_id,
    client_secret=reddit_app_secret,
    user_agent="Test searcher",
)

print(reddit.read_only)

localtime = calendar.timegm(time.gmtime())
commentTable = PrettyTable()
commentTable.field_names = ["Subreddit", "ScoreMin", "Body", "Link"]


def find_rising_posts(reddit: Reddit):
    comments_tree = []

    for submission in reddit.subreddit("all").hot(limit=20):
        submission.comment_sort = "top"
        submission.comment_limit = "10"
        top_level_comments = submission.comments.list()

        print("Got comment")

        for comment in top_level_comments:
            if not isinstance(comment, MoreComments):
                comments_tree.append(comment)

    while comments_tree:
        current_comment = comments_tree.pop(0)

        if isinstance(current_comment, MoreComments):
            continue

        # if current_comment.body == "[removed]":
        #     continue

        comment_time_since_creation_minutes = round((localtime - current_comment.created_utc) / 60, 2) + 1
        if comment_time_since_creation_minutes < 120 and current_comment.score > comment_time_since_creation_minutes:
            formatted_body_message = Back.YELLOW + current_comment.body + Style.RESET_ALL
            score_min = int(round(current_comment.score / comment_time_since_creation_minutes, 0))
            full_permalink = 'http://www.reddit.com' + current_comment.permalink
            commentTable.add_row([submission.subreddit, score_min, formatted_body_message[:36], full_permalink])
            print(Style.RESET_ALL)

        current_comment.reply_sort = "new"
        # current_comment.refresh()
        comment_replies = current_comment.replies.list()

        for reply in comment_replies:
            if not isinstance(reply, MoreComments):
                comments_tree.append(reply)


print(reddit.auth.limits)
find_rising_posts(reddit)
print(reddit.auth.limits)
# commentTable.sortby = "ScoreMin"
print(commentTable)
print("Finished!")
