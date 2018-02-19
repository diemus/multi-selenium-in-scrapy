# multi-selenium-in-scrapy

a middleware that try to make minimal changes to spider while implementing concurrency.

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
   
