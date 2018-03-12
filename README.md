# multi-selenium-in-scrapy

a middleware that try to make minimal changes to spider while implementing concurrency.

不少反爬虫做的比较复杂的网站，可能需要上selenium+无头浏览器才能爬取，但是selenium对并发并不友好，Scrapy一旦用上selenium，异步的优势就体现不出来了，效率会极大降低。multi-selenium中间件通过利用了浏览器本身的并发机制，通过js和scrapy原生的异步调度结合，实现了selenium的伪并发，大大提高了爬取复杂网站的效率。

Documentation
-------------

### Usage

1. set `CONCURRENT_REQUESTS` in settings and enable middleware

2. make a little bit change to your spider

if the page is not ready, instead of blocking the entire process it will return a status of 202 and wait for the opportunity to check again, so we need to add a condition like this:

    if response.status==200:
        do xxxx
    elif response.status==202:
        yield scrapy.Request(response.url, callback=self.parse, dont_filter=True)
    

remeber to add `dont_filter=True` to your Request, otherwise it will be filtered out.
   
