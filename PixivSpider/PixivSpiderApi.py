# -*- coding:utf-8 -*-

# import sys, os
# sys.path.insert(0, os.path.abspath(os.pardir))  # only to test.

from PixivSpider.pixiv_spider import *
from PixivSpider.decorators import timethis


__all__ = ['get_a_picture', 'get_picture_info', 'get_painter_info', 'get_all_picture_of_painter', 'add_bookmark']


def init_class(cls, account=None, password=None, **kwargs):  # Initialize all classes that need to be logged in.
    instance = cls(**kwargs)
    instance.login(account, password)
    return instance


@timethis
def get_a_picture(picture_id, dirname=None, account=None, password=None):
    x = init_class(PixivDownload, account, password, picture_id=picture_id)  # 使用下载类
    if dirname is not None:
        save_path = x.download_picture(dirname)  # 用户自己特定路径
    else:
        save_path = x.download_picture()  # 下载图片，获取图片保存路径
    if save_path is not None:
        print('Download successful: {}'.format(picture_id))
        print('Picture save path: {}'.format(save_path))
    else:
        print('Download failed: {}...'.format(picture_id))
    return x.picture_base_info
    # picture base information:
    # five elements list: picture_id, painter_id, p, date, picture file type
    # note: painter_id is always None at this version.


@timethis
def get_picture_info(picture_id, account=None, password=None):
    x = init_class(PixivPictureInfo, account, password, picture_id=picture_id)  # 使用图片信息类
    return x.get_picture_info()
    # picture information:
    # four elements list: picture_id, title, introduction, sign of bookmark
    # note： sign of bookmark is always None at this version.


@timethis
def add_bookmark(picture_id, comment='', tag='', account=None, password=None):
    try:
        comment, tag = str(comment), str(tag)  # Detect whether tags and comments are strings.
    except Exception as e:
        print(e)
        comment = tag = ''  # If the conversion fails, it is '' by default.
    finally:
        x = init_class(PixivOperatePicture, account, password, picture_id=picture_id)  # 使用操作图片类
        return x.bookmark_add(comment, tag)
        # return whether to add a bookmark successfully via http status code.
        # code:200 -> success -> True, code: not 200 -> failure -> False


@timethis
def get_painter_info(painter_id=None, picture_id=None, account=None, password=None):
    x = init_class(PixivPainterInfo, account, password, painter_id=painter_id, picture_id=picture_id)
    # use painter information class.
    if painter_id is not None or picture_id is not None:
        if painter_id is None:
            x.get_painter_info_from_work_detail_page()  # get painter id via picture id
        return x.get_painter_info()  # get painter information via painter id
        # The data returned is a dictionary.
    else:
        print('painter id and picture id have at least one.')
        return None  # When the parameter is wrong, return None


@timethis
def get_all_picture_of_painter(painter_id=None, picture_id=None, account=None, password=None):
    if painter_id is not None or picture_id is not None:
        if painter_id is None:
            x = init_class(PixivPainterInfo, account, password, picture_id=picture_id)
            # get painter id via picture id.
            painter_id = x.get_painter_info_from_work_detail_page()
        x = init_class(PixivAllPictureOfPainter, account, password, painter_id=painter_id)
        x.get_work_of_painter()  # download all picture of the painter.
    else:
        print('painter id and picture id have at least one.')
        return None


if __name__ == '__main__':
    # get_a_picture(58501385)
    # print(get_picture_info(58501385))
    # print(add_bookmark(58501385))
    # print(get_painter_info(picture_id=58501385))
    # get_all_picture_of_painter(picture_id=58501385)
    # print(get_a_picture.__module__, get_a_picture.__class__, get_a_picture.__name__)
    pass

    # 仰望高端操作，看看能不能把测试写进注释里

