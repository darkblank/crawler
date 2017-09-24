# Episode = namedtuple('Episode', ['no', 'img_url', 'title', 'rating', 'created_date'])
import os
from urllib.parse import urlencode

import pickle
import requests
from bs4 import BeautifulSoup


class Episode:
    """
    namedtuple 'Episode'와 같은 역할을 할 수 있도록 생성
    """
    def __init__(self, webtoon, no, url_thumbnail, title, rating, created_date):
        self.webtoon = webtoon
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date

        self.thumbnail_dir = f'webtoon/{self.webtoon.title}/{self.webtoon.title_id}_thumbnail'
        self.image_dir = 'webtoon/%s/%s_images/%s' % (self.webtoon.title, self.webtoon.title_id, self.no)
        self.episode_dir = f'webtoon/{self.webtoon.title}/{self.webtoon.title_id}_main'
        # ex) webtoon/669233_images/1/01.jpg
        # ex) webtoon/669233_images/1/02.jpg
        # ex) webtoon/669233_images/1/03.jpg
        self.save_thumbnail()

    # @property
    # def webtoon(self):
    #     return self.webtoon
    #
    # @property
    # def no(self):
    #     return self.no
    #
    # @property
    # def url_thumbnail(self):
    #     return self.url_thumbnail
    #
    # @property
    # def title(self):
    #     return self.title
    #
    # @property
    # def rating(self):
    #     return self.rating
    #
    # @property
    # def created_date(self):
    #     return self.created_date

    @property
    def has_thumbnail(self):
        """
        현재경로/webtoon/{self.webtoon.title_id}_thumbnail/{self.no}.jpg
          파일이 있는지 검사 후 리턴
        :return:
        """
        path = f'{self.thumbnail_dir}/{self.no}.jpg'
        return os.path.exists(path)

    def save_thumbnail(self, force_update=False):
        """
        Episode자신의 img_url에 있는 이미지를 저장한다
        :param force_update:
        :return:
        """
        if not self.has_thumbnail or force_update:
            # webtoon/{self.webtoon.title_id}에 해당하는 폴더 생성
            os.makedirs(self.thumbnail_dir, exist_ok=True)
            response = requests.get(self.url_thumbnail)
            filepath = f'{self.thumbnail_dir}/{self.no}.jpg'
            if not os.path.exists(filepath):
                with open(filepath, 'wb') as f:
                    f.write(response.content)

    def save_contents(self):
        """

        :return:
        """
        self._save_images()
        self._make_html()

    def _save_images(self):
        """
        자기자신 페이지 (각 episode페이지)의 img들을 다운로드
        webtoon
            /{self.webtoon.title_id}_images
                /{self.episode.no}
                    /{각 loop index}.jpg
        :return:
        """
        os.makedirs(self.image_dir, exist_ok=True)

        # 웹툰 본문 페이지 (url_contents)
        params = {
            'titleId': self.webtoon.title_id,
            'no': self.no
        }
        url_contents = 'http://comic.naver.com/webtoon/detail.nhn?'\
                       + urlencode(params)
        # 본문 페이지에 대한 HTTP요청 응답
        response = requests.get(url_contents)
        # 응답의 text를 이용해 Soup객체 생성
        soup = BeautifulSoup(response.text)
        # soup객체에서 img tag들의 목록을 찾아내기
        img_list = soup.select_one('.wt_viewer').find_all('img')
        # img tag들에서 'src'속성만 가져와 url_img_list리스트를 생성
        url_img_list = [img['src'] for img in img_list]

        # 리스트를 순회하며 (각 item은 img의 src가 된다)
        for index, url in enumerate(url_img_list):
            # img에 대한 각 requests.get에는 url_contents가 Referer인 header가 필요
            headers = {
                'Referer': url_contents
            }
            # requests.get요청을 보냄
            response = requests.get(url, headers=headers)
            # 파일을 저장
            with open(f'{self.image_dir}/{index + 1}.jpg', 'wb') as f:
                f.write(response.content)

    def _make_html(self):
        os.makedirs(self.episode_dir, exist_ok=True)
        detail_html = open('html/detail_html.html', 'rt').read()
        detail_html = detail_html.replace(
            '*title*', '%s - %s' % (self.webtoon.title, self.title)
        )
        img_list_html = ''
        for file in os.listdir(self.image_dir):
            cur_img_tag = '<img src="../../../%s/%s">' % (self.image_dir, file)
            img_list_html += cur_img_tag

        detail_html = detail_html.replace('*contents*', img_list_html)
        with open(f'{self.episode_dir}/{self.no}.html', 'wt') as f:
            f.write(detail_html)


# if __name__ == '__main__':
#     el = pickle.load(open('db/697680.txt', 'rb'))
#     e = el[0]
#     e._save_images()