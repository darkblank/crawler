import requests

from collections import namedtuple
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

Episode = namedtuple('Episode', ['no', 'img_url', 'title', 'rating', 'created_date'])


def get_webtoon_episode_list(webtoon_id, page=1):
    """
    특정 page의 episode 리스트를 리턴하도록 리팩토링
    :param webtoon_id: 웹툰 고유 ID
    :param page: 가져오려는 Episode list 페이지
    :return: list(Episode)
    """
    # webtoon_url을 기반으로 특정 웹툰의 리스트페이지 내용을 가져와 soup객체에 할당
    webtoon_list_url = 'http://comic.naver.com/webtoon/list.nhn'
    params = {
        'titleId': webtoon_id,
        'page': page,
    }
    response = requests.get(webtoon_list_url, params=params)
    soup = BeautifulSoup(response.text, 'lxml')

    # 필요한 데이터들 (img_url, title, rating, created_date)추출
    episode_list = list()
    webtoon_table = soup.select_one('table.viewList')
    tr_list = webtoon_table.find_all('tr', recursive=False)
    for tr in tr_list:
        td_list = tr.find_all('td')
        if len(td_list) < 4:
            continue
        td_thumbnail = td_list[0]
        td_title = td_list[1]
        td_rating = td_list[2]
        td_created_date = td_list[3]

        # Episode고유의 no
        url_episode = td_thumbnail.a.get('href')
        parse_result = urlparse(url_episode)
        queryset = parse_qs(parse_result.query)
        no = queryset['no'][0]
        # td_thumbnail에 해당하는 Tag의 첫 번째 a tag의 첫 번째 img태그의 'src'속성값
        img_url = td_thumbnail.a.img.get('src')
        # td_title tag의 내용을 좌우여백 잘라냄
        title = td_title.get_text(strip=True)
        # td_rating내의 strong태그내의 내용을 좌우여백 잘라냄
        rating = td_rating.strong.get_text(strip=True)
        # td_title과 같음
        created_date = td_created_date.get_text(strip=True)

        # Episode형 namedtuple객체 생성, episode_list에 추가
        episode = Episode(
            no=no,
            img_url=img_url,
            title=title,
            rating=rating,
            created_date=created_date
        )
        episode_list.append(episode)

    return episode_list
