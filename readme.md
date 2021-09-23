This is a Python webserver built upon socket APIs, the server does not follow WSGI standard, and is only for personal practice.

The server lies in the folder `slow_serv/`

I got the prototype from this project: 
- https://github.com/littlefish12345/simpwebserv
- Original author: **little_fish12345**

Main changes of my project comparing to the prototype:
- Packet framing from tcp-packet to http-data;
- Multi-threading with non-blocking fd;
- Client-side-encrypted-session;
  - For communication over HTTP protocol, the streaming safety(defence for MITM attack, Replay Attacks) should be protected by HTTPS, CSRF safety should be protected by CSRF token.
  - Client-side storage is provided by JWT(eg: Auth2.0: access token + refresh token)
  
- Add before-route-hooks and after-route-hooks;

- Type Hints and test cases;
  - `app_slow_serv.py` demonstrates how to generate a website using slow_serv, and is used in integration test. Run `python test_with_server.py` for integration test.
  
- Stress test
    - See stress test comparison in locust_test.py.
    - `app_flask.py, app_sanic.py, app_slow_serv.py` are used in stress test


## Packet framing from tcp-packet to http-data
This is mainly for myself to practice framing data over raw TCP packet, and this can be useful when you want to practice your own protocols over TCP. 

Till now, framing over `Transfer-Encoding: chunked` has not been finished.

## Multi-threading with non-blocking fd
I do this for practicing socket programing upon Python socket API, which is a mere encapsulation over C socket API. I was always wondering if multi-threading should be coupled with blocking fd or non-blocking fd, so just give it a try.

Later, I will update this to multiplexing socket communication.

## Client-side-encrypted-session
IF you wanna store info on the client side, meanwhile hide the info from the user(and the hacker), client-side-encrypted-session can be an option. 

It can be stored in cookie or LocalStorage:
  - Store in cookie (**I choose for simplicity**)
    - pros: client request will take with it in the header automatically
    - cons: size limit to 4KB
  - store in LocalStorge
    - pros: unlimited size; flexibility to manipulate
    - cons: extra js to send the session, need work on both backend and frontend
  
Some safety concerns:
  - Since only the server needs to generate it and read it, we should choose a symmetric encrypting algorithm.
  - Do we need to worry about Replay Attack? I think no, because it is already guaranteed on HTTPS layer. Another point to consider is that if we want to defend Replay Attack on this layer, we need to introduce in an encrypting algorithm with **nonce**, and **nonce** must be maintained on the server side, which violates the original intention of using client-side-session(stateless). So considering both sides, there is no need and no good to use an encrypting algorithm with **nonce**.
  - For communication over HTTP protocol, the streaming safety(defence for MITM attack, Replay Attacks) should be protected by HTTPS, CSRF safety should be protected by CSRF token.
  - Client-side storage is provided by JWT(eg: Auth2.0: access token + refresh token), with the drawback of visible to the user.
