"""
class NaverWebtoonCrawler생성
    초기화메서드
        webtoon_id
        episode_list (빈 list)
            를 할당
"""
import os
import pickle

import utils


class NaverWebtoonCrawler:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.episode_list = list()
        self.load()

    @property
    def total_episode_count(self):
        """
        webtoon_id에 해당하는 실제 웹툰의 총 episode수를 리턴
        requests를 사용
        :return: 총 episode수 (int)
        """
        el = utils.get_webtoon_episode_list(self.webtoon_id)
        return int(el[0].no)

    @property
    def up_to_date(self):
        """
        현재 가지고있는 episode_list가 웹상의 최신 episode까지 가지고 있는지
        :return: boolean값
        """
        return len(self.episode_list) == self.total_episode_count

    def update_episode_list(self, force_update=False):
        """
        self.episode_list에 존재하지 않는 episode들을 self.episode_list에 추가
        :param force_update: 이미 존재하는 episode도 강제로 업데이트
        :return: 추가된 episode의 수 (int)
        """
        recent_episode_no = self.episode_list[0].no
        print('- Update episode list start (Recent episode no: %s -' % recent_episode_no)
        page = 1
        while True:
            print(' Get webtoon episode list (Loop %s)' % page)
            el = utils.get_webtoon_episode_list(self.webtoon_id, page)
            for episode in el:
                if episode.no > recent_episode_no:
                    self.episode_list.insert(0, episode)
                else:
                    break
            else:
                page += 1
                continue
            break

    def get_last_page_episode_list(self):
        el = utils.get_webtoon_episode_list(self.webtoon_id, 99999)
        self.episode_list = el
        return len(self.episode_list)

    def save(self, path=None):
        """
        현재폴더를 기준으로 db/<webtoon_id>.txt 파일에
        pickle로 self.episode_list를 저장
        :return: 성공여부
        """
        if not os.path.isdir('db'):
            os.mkdir('db')
        pickle.dump(self.episode_list, open('db/%s.txt' % self.webtoon_id, 'wb'))

    def load(self, path=None):
        """
        현재폴더를 기준으로 db/<webtoon_id>.txt 파일의 내용을 불러와
        pickle로 self.episode_list를 복원
        :return:
        """
        if not os.path.exists('db/%s.txt' % self.webtoon_id):
            print('some')
        pickle.load(open('db/%s.txt' % self.webtoon_id, 'wb'))


nwc = NaverWebtoonCrawler(651673)
# print(nwc.total_episode_count)
# print(nwc.up_to_date)
nwc.save()