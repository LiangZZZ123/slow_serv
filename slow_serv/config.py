CODING = "utf-8"
BUFFER_SIZE = 4096

SECRET_KEY = "verysecret"

DO_SECRET_COOKIE = False

DEBUG = False

from slow_serv.hooks.hook_secret_cookie import secret_cookie_before, secret_cookie_after

HOOKS_BEFORE_VIEW_FUNC = [secret_cookie_before]
HOOKS_AFTER_VIEW_FUNC = [secret_cookie_after]
