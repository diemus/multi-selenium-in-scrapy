from selenium import webdriver
from scrapy.http import HtmlResponse
from scrapy.exceptions import IgnoreRequest
from queue import Queue
from scrapy.utils.project import get_project_settings
import time

class SeleniumMiddleware(object):
    def __init__(self):
        # Initialize browser
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        self.browser = webdriver.Firefox(executable_path=r'C:\Users\su\Desktop\geckodriver-v0.19.1-win64\geckodriver.exe',firefox_options=options)

        # get project settings
        settings=get_project_settings()
        concurrent_requests=settings.get('CONCURRENT_REQUESTS')

        # Initialize tabs
        while len(self.browser.window_handles) < concurrent_requests:
            self.browser.execute_script('''window.open("","_blank");''')

        # Initialize window handles queue
        self.handle_queue=Queue(maxsize=concurrent_requests)
        for handle in self.browser.window_handles:
            self.handle_queue.put(handle)

        # Initialize requests dict
        self.requests={}

    def process_request(self, request, spider):
        result=self.requests.get(request.url)
        if result is None:
            # get a free window_handle from queue
            if self.handle_queue.empty():
                return HtmlResponse(url=request.url,request=request, encoding='utf-8', status=202)
            handle = self.handle_queue.get()

            # open url by js
            self.browser.switch_to.window(handle)
            js = r"location.href='%s';" % request.url
            self.browser.execute_script(js)

            # wait for 1s to avoid some bug ("document.readyState" will return a "complete" at the first)
            time.sleep(1)

            # mark url
            self.requests[request.url]={'status':'waiting','handle':handle}

            return HtmlResponse(url=request.url,request=request, encoding='utf-8', status=202)

        elif result['status']=='waiting':

            # switch to the tab to check page status using javascript
            handle = result['handle']
            self.browser.switch_to.window(handle)
            document_status=self.browser.execute_script("return document.readyState;")

            if document_status=='complete':
                self.requests[request.url]['status'] = 'done'
                self.handle_queue.put(handle)
                return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                    status=200)
            else:
                return HtmlResponse(url=request.url, request=request, encoding='utf-8', status=202)

        elif result['status']=="done":
            # Filter repeat URL
            raise IgnoreRequest

    def __del__(self):
        self.browser.quit()
