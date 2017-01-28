#!/usr/bin/python

import pytumblr
import json
from secrets import consumer_key, secret_key, oauth_token, oauth_secret

client = pytumblr.TumblrRestClient(
        consumer_key,
        secret_key,
        oauth_token,
        oauth_secret
)

def get_info(blog):
    return client.blog_info(blog)

def get_posts(blog, offset=0, limit=20):
    return client.posts(blog, type="text", filter="text", offset=offset, limit=limit)["posts"]

if __name__ == "__main__":
    blog = "antlerscolorado"
    print get_info(blog)
    print get_posts(blog, limit=1)
