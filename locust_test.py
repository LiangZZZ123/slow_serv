"""
I used "Locust" and "wrk" for stress test (slow_serv VS flask VS sanic)

------ Do stress test with Locust -----
Runing Locust on multiple cores(my CPU has 4 cores):
## Start master process
$ locust -f locust_test.py --headless -u 2000 -r 500 -t 60s --master --expect-workers=3
## open 3 terminals and start 3 worker processes
$ locust -f locust_test.py --worker

------ Do stress test with wrk ------
$ ./wrk -t 5 -c 300 -d 60 --latency http://localhost:5000

------ Results ------
|        |   | slow_serv            |   | Flask                 |   | Sanic                 |
|--------|---|----------------------|---|-----------------------|---|-----------------------|
|        |   | QPS                  |   | QPS                   |   | QPS                   |
| Locust |   | 1099.80(0.00% fails) |   | 1112.81(51.89% fails) |   | 1285.02(48.66% fails) |
| wrk    |   | 491.89               |   | 381.44                |   | 4520.67               |

It's very wired that when using Locust, slow_serv does not have any failed 
requests while the other two servers endure almost 50% of failures.

It's evident that Sanic should have better performance than the other two 
servers because it uses multiplexing for IO, while the other two use multi-
threads. 

The main drawback of multithreads lies in that when a thread call "data = fd.recv()",
the fd goes from userspace to kernelspace, invokes a syscall to visit the system-
tcp-cache, then return back to usperspace to assign the result to "data", this
can be followed by a lot of useless "while True" loop if a fd find that there
is no corresponding packet aviailable for him in system-tcp-cache.

I tried to add "time.sleep(0.5)" when a fd find that there
is no corresponding packet aviailable for him in system-tcp-cache, so that 
the current thread can stop useless loop and hand over CPU to other threads.
But this introduces in another problem: if the packet for this fd arrives
in system-tcp-cache right after the thread(of fd) doing sleep, the possibility
(of other fds getting their packets fro system-tcp-cache) decreases.

Eg: image system-tcp-cache as a length-fixed array:

[packet_for_fd1, packet_for_fd2, packet_for_fd3]

- fd4 checks the cache and finds that there's no packet for him, so thread_of_fd4
does sleep(0.5). But right after this, fd3 gets the packet from the cache, and 
packet_for_fd4 comes in the the cache. Now system-tcp-cache becomes:

[packet_for_fd1, packet_for_fd2, packet_for_fd4]

and packet_for_fd4 will not be read at least in the incoming 0.5s, which
decreases the possibility of other fds reading their packets.
"""

from locust import HttpUser, TaskSet, between, task


class Tasks(TaskSet):
    def on_start(self):
        # print("Start stress test")
        ...

    @task(2)
    def visit_main_get(self):
        self.client.get("/")

    @task(1)
    def visit_main_post(self):
        # self.client.post("/", {k: v for k, v in zip(range(1000), range(1000))})
        self.client.post("/", {k: v for k, v in zip(range(2), range(2))})

    def on_stop(self):
        # print("Stop stress test")
        ...


class User(HttpUser):
    tasks = [Tasks]
    # host = "https://www.baidu.com"
    host = "http://localhost:5000"
    # host = "http://192.168.1.1"
    wait_time = between(1, 2)

