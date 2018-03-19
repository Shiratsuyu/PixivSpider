import math
import os
import sys
from collections import deque
from http import cookiejar

import requests
from lxml import etree

from PixivSpider.operate_db import conn, insert_picture_data, find_all_picture_id
from PixivSpider.setting import re_tuple, url_tuple, User_Agent, \
    form_data, COOKIE_FILE, work_num_of_each_page, save_folder, \
    pic_detail_page_mode, list_of_works_mode, after_str_mode

__all__ = ['Pixiv', 'get_work_of_painter']

already_download_picture = find_all_picture_id(conn)


def get_work_of_painter(username=None, password=None, *, painter_id):  # 强化参数调用.
    pixiv = Pixiv()
    pixiv.login(username, password)
    pixiv.get_work_of_painter(painter_id)


class Pixiv(requests.Session):
    def __init__(self):
        super(Pixiv, self).__init__()
        self._url_tuple = url_tuple
        self._re_tuple = re_tuple
        self.__form_data = form_data
        self.dir_name = save_folder
        self.work_num = None
        self.page_num = None
        self.work_num_of_each_page = work_num_of_each_page
        self.user_name = None
        self.work_deque = deque()
        # self.already_download_picture = find_all_picture_id(conn)
        self.pid = None
        self.file_type = 'png'
        self.artist_dir_exist = False
        self.headers.update({'User-Agent': User_Agent})
        self.cookies = cookiejar.LWPCookieJar(filename=COOKIE_FILE)

    def _get_post_key(self):
        login_content = self.get(self._url_tuple.login_url)
        try:
            post_key = self._re_tuple.post_key.findall(login_content.text)[0]
        except IndexError:
            print('Get post_key failure.')
            sys.exit(1)
        else:
            return post_key

    def login(self, pixiv_id=None, pixiv_passwd=None):
        if self.login_with_cookies():
            return True
        else:
            return self.login_with_account(pixiv_id, pixiv_passwd)

    def login_with_cookies(self):
        try:
            self.cookies.load(filename=COOKIE_FILE, ignore_discard=True)
        except FileNotFoundError:
            return False
        else:
            if self.already_login():
                return True
            return False

    def login_with_account(self, pixiv_id=None, pixiv_passwd=None):
        """login function"""
        self.__form_data['pixiv_id'] = pixiv_id
        self.__form_data['password'] = pixiv_passwd
        self.__form_data['post_key'] = self._get_post_key()
        result = self.post(self._url_tuple.post_url, data=self.__form_data)
        if result.status_code == 200:
            self.cookies.save(ignore_discard=True)
            return True
        return False

    def already_login(self):
        status = self.get(self._url_tuple.setting_url, allow_redirects=False).status_code
        return status == 200

    def get_work_of_painter(self, artist_id):
        self._parse_artist_page(artist_id)
        self._get_work_info()
        for item in self.work_deque:
            self._get_img_data(pid=item[0], date=item[1], filename=item[2])

    def _parse_artist_page(self, artist_id, number=10):
        self.pid = artist_id
        print(self.pid)
        list_of_works = self.get(list_of_works_mode.format(pid=artist_id))
        selector = etree.HTML(list_of_works.text)
        try:
            self.user_name = selector.xpath('//a[@class="user-name"]/text()')[0]
        except IndexError:
            print('Get user_name failure.')
            sys.exit(1)
        try:
            work_num = selector.xpath('//span[@class="count-badge"]/text()')[0]
        except IndexError:
            print('Get work_num failure.')
            sys.exit(1)
        else:
            self.work_num = int(self._re_tuple.num.findall(work_num)[0])
            self.page_num = math.ceil(self.work_num / self.work_num_of_each_page)
            print(self.work_num, self.page_num)

    def _parse_pic_detail_page(self, pic_id):
        url = pic_detail_page_mode.format(pid=pic_id)
        detail_result = self.get(url)
        selector = etree.HTML(detail_result.text)
        try:
            self.user_name = selector.xpath('//a[@class="user-name"]/text()')[0]
        except IndexError:
            print('Get user_name failure.')
            sys.exit(1)
        try:
            img_url = selector.xpath('//img[@class="original-image"]/@data-src')[0]
            print(img_url)
        except IndexError:
            print('Get real Pic url failure.')
            sys.exit(1)
        else:
            return img_url

    def _get_work_info(self):
        base_url = list_of_works_mode.format(pid=self.pid)
        if self.page_num >= 1:
            self._get_each_work_info(base_url)
        if self.page_num >= 2:
            for each_page in range(2, self.page_num + 1):
                # works_params = {'type': 'all', 'p': each_page}
                self._get_each_work_info(base_url + '&type=all&p={}'.format(each_page))

    def _get_each_work_info(self, url):
        result = self.get(url)
        selector = etree.HTML(result.text)
        original_img_url = selector.xpath('//img[@data-src]/@data-src')
        for item in original_img_url:
            # print(self.headers)
            date_str = self._re_tuple.date.findall(item)[0]  # 取出url中的日期部分
            id_str = self._re_tuple.pid.findall(item)[0]  # 取出url中的作品id部分
            filename = item.split('/')[-1].replace('_master1200.jpg', '')  # XXX_p0
            if int(id_str) not in already_download_picture:  # 将filename 替换成 ID + FENP
                self.work_deque.append((id_str, date_str, filename))
            else:
                print('图片{}已经存在了， 不再加入队列中....'.format(id_str))

    def _get_img_data(self, pid=None, date=None, filename=None, img_url=None):
        headers = self.headers
        headers['Host'] = 'www.pixiv.net'
        temp_file_type = self.file_type
        if img_url is None:
            if pid is not None and date is not None and filename is not None:
                headers['Referer'] = pic_detail_page_mode.format(pid=pid)

                img_url = self._get_real_url(pid, date, filename, temp_file_type)
                img_data = self.get(img_url, headers=headers)
                if img_data.status_code == 200:
                    insert_picture_data(conn, pid, self.pid, date, temp_file_type)
                    self._save_img_file(filename=self._get_complete_filename(filename, temp_file_type),
                                        img_data=img_data.content)
                elif img_data.status_code == 404:
                    print('转换图片格式')
                    self._type_conversion()  # 如果使用异步, 这个self.file_type 会害死我
                    temp_file_type = self.type_conversion(temp_file_type)
                    img_url = self._get_real_url(pid, date, filename, temp_file_type)
                    img_data = self.get(img_url, headers=headers)
                    if img_data.status_code == 200:
                        insert_picture_data(conn, pid, self.pid, date, temp_file_type)
                        self._save_img_file(filename=self._get_complete_filename(filename, temp_file_type),
                                            img_data=img_data.content)
                    else:
                        print('转换格式也救不了你...: {}'.format(img_url))
                else:  # get 403
                    print('访问图片具体页面出错: {}'.format(img_url))
            else:
                print('{}参数输入错误,无法构造url...'.format(self._get_img_data.__name__))
                sys.exit(1)
        else:
            filename = img_url.split('/')[-1]
            pic_id = filename.split('_')[0]
            headers['Referer'] = pic_detail_page_mode.format(pid=pic_id)
            img_data = self.get(img_url, headers=headers)
            if img_data.status_code == 200:
                self._save_img_file(filename=filename, img_data=img_data.content)
            else:
                print('直接访问{}失败...'.format(img_url))

    def _create_folder(self):
        dir_name = os.path.join(self.dir_name, self.user_name)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        self.artist_dir_exist = True

    def _save_img_file(self, filename, img_data):
        if not self.artist_dir_exist:
            self._create_folder()
        file_path = os.path.join(self.dir_name, self.user_name, filename)
        if not os.path.exists(file_path):
            with open(file=file_path, mode='wb') as f:
                f.write(img_data)
                print('成功...')
                # log -> log.txt
        else:
            print('{}文件已经存在....'.format(filename))

    def _type_conversion(self):
        """转换文件格式"""
        if self.file_type == 'png':
            self.file_type = 'jpg'
        elif self.file_type == 'jpg':
            self.file_type = 'png'

    @staticmethod
    def _get_complete_filename(filename, file_type):
        return filename + '.' + file_type

    @staticmethod
    def _get_real_url(pid, date, filename, file_type):
        work_img_url = after_str_mode.format(date=date, filename=filename, file_type=file_type)
        return work_img_url

    @staticmethod
    def type_conversion(file_type):
        if file_type == 'png':
            return 'jpg'
        elif file_type == 'jpg':
            return 'png'


if __name__ == '__main__':
    username = input('输入你的帐号:')
    password = input('输入你的密码:')
    painter_id = input('输入画师ID:')
    demo = Pixiv()
    demo.login(username, password)
    demo.get_work_of_painter(painter_id)

# x.parse_artist_page(27517)
# x.get_work_info()
# for temp in x.work_deque:
#     url = x.get_real_url(pid=temp[0], date=temp[1], filename=temp[2])
#     x.get_img_data(img_url=url, filename=temp[2], pid=temp[0])

# print(x.work_deque)


# Session class youhua...
# cookies caozuo...

# 还需要再操作文件格式的转换
# log
# db ?? ....emmm mongodb, sqlite
# GUI: sock5 代理...
# xiu gai can shu, you de can shu rongyu le
# 增量, 每次都将本地数据录入数据库, 合适不,
# 通过去重, 直接在队列里操作.
# 压缩...
# 命令行..
# 异步
# 将用户名密码写到setting中去???