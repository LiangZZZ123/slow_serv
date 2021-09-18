See webpage's source code: 如果要把这个网页保存下来，可以使用`-o`参数，这就相当于使用wget命令了。
```
$ curl -o [文件名] www.sina.com
$ curl www.sina.com -i > sina.html    # override
$ curl www.sina.com -i >> sina.html   # append
```


五、发送表单信息
发送表单信息有GET和POST两种方法。GET方法相对简单，只要把数据附在网址后面就行。
```
$ curl example.com/form.cgi?data=xxx
```
POST方法必须把数据和网址分开，curl就要用到--data参数。
```
$ curl -X POST --data "data=xxx" example.com/form.cgi
```
如果你的数据没有经过表单编码，还可以让curl为你编码，参数是`--data-urlencode`。
```
$ curl (-X POST) --data-urlencode "date=April 1" example.com/form.cgi
```

六、HTTP动词
curl默认的HTTP动词是GET，使用`-X`参数可以支持其他动词。


十、cookie
使用`--cookie`参数，可以让curl发送cookie。
```
$ curl --cookie "name=xxx" www.example.com
```
至于具体的cookie的值，可以从http response头信息的`Set-Cookie`字段中得到。

`-c cookie-file`可以保存服务器返回的cookie到文件，`-b cookie-file`可以使用这个文件作为cookie信息，进行后续的请求。

　　$ curl -c cookies http://example.com
　　$ curl -b cookies http://example.com


十一、增加头信息

有时需要在http request之中，自行增加一个头信息。`-H/--header`参数就可以起到这个作用。
```
$ curl -H "Content-Type:application/json" http://example.com
```




使用-d参数以后，HTTP 请求会自动加上标头Content-Type : application/x-www-form-urlencoded。并且会自动将请求转为 POST 方法，因此可以省略-X POST。

-d参数可以读取本地文本文件的数据，向服务器发送。


$ curl -d '@data.txt' https://google.com/login
上面命令读取data.txt文件的内容，作为数据体向服务器发送。

--data-urlencode
--data-urlencode参数等同于-d，发送 POST 请求的数据体，区别在于会自动将发送的数据进行 URL 编码。

$ curl --data-urlencode 'comment=hello world' https://google.com/login
上面代码中，发送的数据hello world之间有一个空格，需要进行 URL 编码。




-G
-G参数用来构造 URL 的查询字符串。不过自己拼url查询字明显更快

$ curl -G -d 'q=kitties' -d 'count=20' https://google.com/search
上面命令会发出一个 GET 请求，实际请求的 URL 为https://google.com/search?q=kitties&count=20。如果省略-G，会发出一个 POST 请求。

如果数据需要 URL 编码，可以结合--data--urlencode参数。
```
$ curl -G --data-urlencode 'comment=hello world' https://www.example.com
```


Getting only response header from HTTP POST using cURL
```
$ curl -I -X POST http://www.baidu.com >> head.txt
```