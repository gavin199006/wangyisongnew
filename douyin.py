#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-12-29 下午6:07
# @Author  : Gavin
# @Site    : 
# @File    : douyin.py
# @Software: PyCharm


import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

"""
下载文件参数url和文件的全路径
"""


def download_file(src, file_path):
	#   响应体工作流
	r = requests.get(src, stream=True)
	# 打开文件
	f = open(file_path, "wb")
	# for chunk in r.iter_content(chunk_size=512):
	#     if chunk:
	#         f.write(chunk)
	for data in tqdm(r.iter_content(chunk_size=512)):
		# tqdm进度条的使用,for data in tqdm(iterable)
		f.write(data)
	return file_path


headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}
# 保存路径
save_path = "/zhangkun/PycharmProjects/wangyisong/douyin/"
url = "https://kuaiyinshi.com/hot/music/?source=dou-yin&page=1"
# 获取响应
res = requests.get(url, headers=headers)
# 使用beautifulsoup解析
soup = BeautifulSoup(res.text, 'lxml')
# 选择标签获取最大页数
max_page = soup.select('li.page-item > a')[-2].text
# 循环请求

song_path = '/zhangkun/PycharmProjects/wangyisong/songs'

for page in range(int(max_page)):
	page_url = "https://kuaiyinshi.com/hot/music/?source=dou-yin&page={}".format(page + 1)
	page_res = requests.get(page_url, headers=headers)
	soup = BeautifulSoup(page_res.text, 'lxml')
	lis = soup.select('li.rankbox-item')
	singers = soup.select('div.meta')
	music_names = soup.select('h2.tit > a')
	for i in range(len(lis)):
		music_url = "http:" + lis[i].get('data-audio')
		print("歌名:" + music_names[i].text, singers[i].text, "链接:" + music_url)

		song_name = music_names[i].text
		try:
			download_file(music_url,
			              save_path + music_names[i].text + ' - ' + singers[i].text.replace('/', ' ') + ".mp3")
		except:
			pass

		with open(song_path,'a') as f:
			f.write(song_name + '\n')

	exit()
	print("第{}页完成~~~".format(page + 1))
	time.sleep(1)