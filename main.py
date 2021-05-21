import os
from os.path import dirname, join
import praw, time, calendar
from praw import Reddit
from prettytable import PrettyTable
from praw.models import MoreComments, Comment, Submission
from colorama import init, Fore, Back, Style
from dotenv import load_dotenv
from typing import List

load_dotenv(join(dirname(__file__), '.env'))
reddit_app_client_id = os.environ.get("REDDIT_APP_CLIENT_ID")
reddit_app_secret = os.environ.get("REDDIT_APP_SECRET")

init()
reddit = praw.Reddit(
    client_id=reddit_app_client_id,
    client_secret=reddit_app_secret,
    user_agent="Test searcher",
)

print(reddit.read_only)

commentTable = PrettyTable()
commentTable.field_names = ["Subreddit", "ScoreMin", "Body", "Link"]


def find_rising_posts(reddit: Reddit):
    comments_to_search: List[Comment] = []

    submission: Submission
    for submission in reddit.subreddit("all").hot(limit=10): # iterate over submissions in r/all (api call)
        submission.comment_sort = "best"
        submission.comment_limit = "40"
        submission_comments = submission.comments.list() # request for current submission's comments list (direct + nested) (api call)

        print("Got submission comments")
        number_of_comments = 0

        for comment in submission.comments:
            if isinstance(comment, Comment):
                number_of_comments += 1

        print(number_of_comments)

        comment: Comment
        for comment in submission_comments: # for each comment of current submission append into comments_to_search
            if isinstance(comment, Comment):
                comments_to_search.append(comment)

    localtime = calendar.timegm(time.gmtime())
    for comment in comments_to_search: # iterate over all comments gathered and do idiot checks
        comment_time_since_creation_minutes = round((localtime - comment.created_utc) / 60, 2) + 1
        if comment_time_since_creation_minutes < 60 and comment.score > comment_time_since_creation_minutes:
            formatted_body_message = Back.YELLOW + comment.body + Style.RESET_ALL
            score_min = round(comment.score / comment_time_since_creation_minutes, 2)
            full_permalink = 'http://www.reddit.com' + comment.permalink
            commentTable.add_row([comment.subreddit, score_min, formatted_body_message[:36], full_permalink])
            print(Style.RESET_ALL)



print(reddit.auth.limits)
find_rising_posts(reddit)
print(reddit.auth.limits)
# commentTable.sortby = "ScoreMin"
print(commentTable)
print("Finished!")
