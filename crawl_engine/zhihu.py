import json
from bs4 import BeautifulSoup
import requests
import time
import subprocess
class zhihu_crawl_engine:
    headers = {
        'Cookie': '__snaker__id=Bkkx6NCOxYwMJvaD; SESSIONID=gW7B1eMefotBVCom3KBpNGFMuJcGnEQpSGc9wEwyI9E; _zap=bef0e54c-b1c6-457c-a7ac-30d70d43e5b2; d_c0=AWDcShggVBiPTvM_fKm83LF3-1Q1_AK0HWM=|1710742418; __snaker__id=wvL4NAI39W7P97hz; q_c1=e8d57f2b68234efd910c58fcbc5c27da|1713492364000|1713492364000; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1715321726,1715578292,1715672148,1715764879; _xsrf=e4878873-ae70-4105-b4ba-adc8a1241574; z_c0=2|1:0|10:1716124251|4:z_c0|80:MS4xcWlNYkJBQUFBQUFtQUFBQVlBSlZUZGxFTjJka1oxLTQ4emRZak5XYmltVnZRUWhWMGJYR0l3PT0=|911f7b0625e454d66067c36849285cd313d86f57ce7265fb5bc3d5b9f8c76dcf; __zse_ck=001_NTWcPx66mfbiV7/lcbP2XZNPTYCk5HhzW6S997Q7YSVEkCLq=IdptdBq0+i2jx6pA1Fsl2m4zOSNAJdhTXtiJNw4wgQ/B70txw/d5MSEXLhH+0MaNE8hkEfKUirNdbdM; tst=h; SESSIONID=94BmlbCUmkXvndQ06pScnEWH9CxgsY51Pg20vgDcbw8; BEC=dcf48dc6658a759143059988141e93bc; KLBRSID=cdfcc1d45d024a211bb7144f66bda2cf|1716620365|1716606345'
        ,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }


    def __init__(self, question_url):
        self.question_url = question_url
        return


    def set_cookie(self, cookie):
        self.headers['Cookie'] = cookie
        return

    def initial_request(self, url):
        """
        从问题url中获取第一页内容和请求
        :param url: 问题url
        :return: {}
        """
        headers = self.headers
        response = requests.get(url=url, headers=headers)
        page_text = response.text
        soup = BeautifulSoup(page_text, 'html.parser')
        # <script id="js-initialData" type="text/json">
        page_json_string = soup.find('script', id='js-initialData').string
        page_json = json.loads(page_json_string)
        return_data = {}
        id = url.split('/')[-1]
        return_data['id'] = id
        questions_text = BeautifulSoup(page_json['initialState']['entities']['questions'][id]['detail'],
                                       'html.parser').get_text()
        return_data['question_text'] = questions_text
        questions_title = page_json['initialState']['entities']['questions'][id]['title']
        return_data['question_title'] = questions_title
        next_url = page_json['initialState']['question']['answers'][id]['next']
        return_data['next_url'] = next_url
        content_list = []
        answers = page_json['initialState']['entities']['answers']
        for answerid in answers:
            content_html = answers[answerid]['content']
            soup_answer = BeautifulSoup(content_html, 'html.parser')
            content = soup_answer.get_text()
            content_list.append(content)
        return_data['content_list'] = content_list
        return return_data

    def fetch_single_page(self, url):
        """
        获取一页的数据
        :param url: 这一页的url
        :return: 1.[]answer文本的list 2.是否还有下一页 3.下一页URL
        """
        headers = self.headers
        return_data = {}
        response = requests.get(url=url, headers=headers).json()
        is_end = response['paging']['is_end']
        try:
            next_url = response['paging']['next']
        except KeyError:
            next_url = None
        return_data['is_end'] = is_end
        return_data['next_url'] = next_url
        answers = response['data']
        content_list = []
        for ans in answers:
            html_content = ans['target']['content']
            soup = BeautifulSoup(html_content, 'html.parser')
            content = soup.get_text()
            content_list.append(content)
        return_data['content_list'] = content_list
        return return_data

    def get_qa(self, question_url):
        """
        返回一个问题URL中我们所需的所有信息
        :param question_url: 问题URL
        :return:1. 问题标题
                2. 问题文本描述
                3. 回答list
        """
        return_data = {}
        answer_list = []
        initial_response = self.initial_request(question_url)
        question_id = question_url.split('/')[-1]
        return_data['question_title'] = initial_response['question_title']
        return_data['question_text'] = initial_response['question_text']
        message = f'开始爬取"{return_data["question_title"]}"的回答'
        print(message)
        print('page1')
        next_url = initial_response['next_url']
        is_end = False
        time.sleep(1)
        page = 1
        while not is_end:
            time.sleep(1)
            if page > 199:
                break
            page += 1
            print(f'page{page}')
            current_page = self.fetch_single_page(next_url)
            is_end = current_page['is_end']
            next_url = current_page['next_url']
            answer_list += current_page['content_list']
        return_data['answer_list'] = answer_list
        path = f'./questions/{question_id}'
        subprocess.run(['mkdir', path])
        with open(f'questions/{question_id}/{question_id}.json', 'w') as file:
            json.dump(return_data, file, indent=4, ensure_ascii=False)
        return return_data

    def start_crawl(self):
        """
        对外接口，返回的结构是
        {"question_title":""
        "question_text":""
        "answer_list":["",""]
        }
        :return:
        """
        questions_url = self.question_url
        all_info = self.get_qa(questions_url)
        return all_info






