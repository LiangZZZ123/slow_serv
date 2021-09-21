This is a Python webserver built on pure socket APIs, the server does not follow WSGI standard, and is only for personal practice.

I got the prototype from this project: 
- https://github.com/littlefish12345/simpwebserv
- Original author: **little_fish12345**

Main changes comparing to the prototype:
- Packet framing from tcp-packet to http-data;
- Non-blocking fd.recv();
- Add client-side-encrypted-cookie;
- Add before-route-hooks and after-route-hooks;

- Type Hints and test cases;
  - `app_slow_serv.py` demonstrates how to generate a website using slow_serv framework, and is used in integration test. Run `python test_with_server.py` for integration test.
  
- Stress test
    - See stress test comparison in locust_test.py.
    - `app_flask.py, app_sanic.py, app_slow_serv.py` are used in stress test
