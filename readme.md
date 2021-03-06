- [1. Abstract](#1-abstract)
- [2. What's new](#2-whats-new)
- [3. Details](#3-details)
  - [3.1. Packet framing from tcp-packet to http-data](#31-packet-framing-from-tcp-packet-to-http-data)
  - [3.2. Multi-threading without using globals](#32-multi-threading-without-using-globals)
  - [3.3. Client-side-encrypted-cookie](#33-client-side-encrypted-cookie)
    - [3.3.1. Some safety concerns](#331-some-safety-concerns)
    - [3.3.2. How to use Client-side-encrypted-cookie](#332-how-to-use-client-side-encrypted-cookie)
# 1. Abstract
This is a Python webserver built upon socket APIs, the server does not follow WSGI standard, and is only for personal practice.

The server lies in the folder `slow_serv/`

The basic way of creating an web application with slow_serv is:
```python
app = slow_serv.Server()
def main(request, response):
    response.body="BIG APP supported by slow_serv"
app.route("/", main)
app.run()
```

# 2. What's new
I got the prototype from this project: 
- https://github.com/littlefish12345/simpwebserv
- Original author: **little_fish12345**

Main changes of my project comparing to the prototype:
- Framing from TCP segment to HTTP message;
- Multi-threading without using globals;
- Client-side-encrypted-cookie;
- Add before-route-hooks and after-route-hooks;

- Type Hints and test cases;
  - The whole project is type hinted and type checked with `mypy`.
  - `app_slow_serv.py` demonstrates how to generate a website using slow_serv, and is used in integration test. Run `pytest test_with_server.py` for integration test.
  - Unit tests are distributed in package level, run `pytest` to do all tests.
  
- Load test
    - See load test comparison in locust_test.py.
    - `app_flask.py, app_sanic.py, app_slow_serv.py` are used in load test


# 3. Details
## 3.1. Packet framing from tcp-packet to http-data
This is mainly for myself to practice framing data from transport layer(raw TCP segments) to application layer protocols(HTTP message here), and this can be useful when you want to practice your own protocols over TCP. 

Till now, framing over `Transfer-Encoding: chunked` has not been finished.

## 3.2. Multi-threading without using globals
I don't really like the style of **global variable + local threads** for implementing multi-thread, my preference is encapsulating all info in a `Request` object and a `Response` object and pass these two parameters to every view function, just like `def main(request, response): ...`.

And of course, multi threads is kind of an old fashioned schema nowadays for an IO intensive application, and later I will try using `yield` primitives to build an asynchronous framework.

## 3.3. Client-side-encrypted-cookie
IF you wanna store info on the client side, meanwhile hide the info from the user(and the hacker), you may take **client-side-encrypted-cookie** as an option. 

It can be stored in cookie or LocalStorage:
  - Store in cookie (**I choose for simplicity**)
    - pros: client request will take with it in the header automatically
    - cons: size limit to 4KB
  - store in LocalStorage
    - pros: unlimited size; flexibility to manipulate
    - cons: extra js to send the data, need work on both backend and frontend

### 3.3.1. Some safety concerns
  - Q: Symmetric or asymmetric algorithm?
  - A: Since only the server needs to generate it and read it, we should choose a symmetric encrypting algorithm.
  
  - Q: Do we need to worry about Replay Attack? 
  - A: I think no, because it is already guaranteed on HTTPS layer. For communication over HTTP protocol, the streaming safety(defence for MITM attack, Replay Attack / Forbidden Attack) should be protected by HTTPS, CSRF safety should be protected by CSRF token.
   
  - Q: Do we need Authenticated Encryption with Associated Data (AEAD)?  
  - A: In most cases, we should do encryption and authentication together, and Modern symmetric cipher suits(eg: AES-GCM, ChaCha20-Poly1305) provide AEAD guarantees. It's absolutely good that we use then directly. But for this specific case, I think actually the authentication is not needed. The reason is if the ciphered_text_in_byte has been tampered, the deciphered_text_in_byte(deciphered from ciphered_text_in_byte) will become undecodable to plaintext.

  - Q: Why not JWT?
  - A: JWT does provide client-side storage(eg: Auth2.0: access token + refresh token), with the drawback of visible to the user. And the main usage of client-side-encrypted-cookie is storing data while hiding data from the user.

### 3.3.2. How to use Client-side-encrypted-cookie
1. Add hooks in `slow_serv/config.py`
```python
from slow_serv.hooks.hook_secret_cookie import secret_cookie_before, secret_cookie_after

HOOKS_BEFORE_VIEW_FUNC = [secret_cookie_before]
HOOKS_AFTER_VIEW_FUNC = [secret_cookie_after]
```
2. Use it directly in your view_function:
```python
app = slow_serv.Server()

def main(request, response):
    # This gives you a normal cookie, you will see one row added in your browser's cookie storage
    response.cookie["name"] = Leo

    # This gives you two secret cookies, they will be combined to one row in your browser's cookie storage
    response.secret_cookie["a"] = 1
    response.secret_cookie["b"] = 2
    response.secret_cookie["c"] = 3

    response.body="BIG APP supported by slow_serv"

app.route("/", main)
app.run()
```
You will see something like this in your browser's cookie storage:

![cookie_snippet](cookie_snippet.jpg)

You can see more intuitive examples by looking at `app_slow_serv.py` and `test_app_slow_serv.py`.