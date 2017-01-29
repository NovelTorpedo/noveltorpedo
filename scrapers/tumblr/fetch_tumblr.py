#!/usr/bin/python

import pytumblr
from secrets import consumer_key, secret_key, oauth_token, oauth_secret

client = pytumblr.TumblrRestClient(
        consumer_key,
        secret_key,
        oauth_token,
        oauth_secret
)

def get_info(blog):
    """
    Fetch general information about the blog being tracked. Returns a
    dictionary.  Keys which are likely to be useful:
        title
        url
        description
        is_nsfw (boolean)
        updated (most recent post's timestamp, in integer seconds since epoch)
    """
    return client.blog_info(blog)["blog"]

def get_posts(blog, offset=0, limit=20):
    """
    Fetch post contents and metadata. Parameters:
        offset (how many posts back to begin)
        limit (how many posts to return; 20 is the max allowed by the API)
    Returns a list of dictionaries. Keys which are likely to be useful:
        blog_name
        body
        post_url
        short_url
        timestamp
        title
    """
    return client.posts(blog, type="text", filter="text",
                        offset=offset, limit=limit)["posts"]

if __name__ == "__main__":
    """
    This allows you to pass the short name of a tumblr on the command line to
    get a summary of recent text posts. A couple examples to test on:
        antlerscolorado
        docfuture
    """
    import sys
    try:
        blog = sys.argv[1]
        print("{title} ({url})".format(**get_info(blog)))
        for post in get_posts(blog):
            print("\t{timestamp} - {title} ({short_url})".format(**post))
    except IndexError:
        print("Please supply a tumblr name.")
    except KeyError:
        print("Tumblr not found.")
