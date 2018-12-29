#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-12-28 下午6:08
# @Author  : Gavin
# @Site    : 
# @File    : song_id.py
# @Software: PyCharm
import csv
import re
import time
import urllib

import requests, os, json, base64
from bs4 import BeautifulSoup
from scrapy.selector import Selector
from binascii import hexlify
from Crypto.Cipher import AES


class Encrypyed():

	"""
	传入歌曲的ID，加密生成'params'、'encSecKey 返回
	"""


	def __init__(self):
		self.pub_key = '010001'
		self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
		self.nonce = '0CoJUm6Qyw8W8jud'

	def create_secret_key(self, size):
		return hexlify(os.urandom(size))[:16].decode('utf-8')

	def aes_encrypt(self, text, key):
		key = key.encode('utf-8')
		iv = b'0102030405060708'
		pad = 16 - len(text) % 16

		text = text + pad * chr(pad)
		text = text.encode('utf-8')
		encryptor = AES.new(key, AES.MODE_CBC, iv)
		result = encryptor.encrypt(text)
		result_str = base64.b64encode(result).decode('utf-8')
		return result_str

	def rsa_encrpt(self, text, pubKey, modulus):

		text = text[::-1]
		rs = pow(int(hexlify(text.encode('utf-8')), 16), int(pubKey, 16), int(modulus, 16))
		return format(rs, 'x').zfill(256)

	def work(self, ids, br=128000):

		text = {'ids': [ids], 'br': br, 'csrf_token': ''}
		text = json.dumps(text)
		i = self.create_secret_key(16)
		encText = self.aes_encrypt(text, self.nonce)
		encText = self.aes_encrypt(encText, i)
		encSecKey = self.rsa_encrpt(i, self.pub_key, self.modulus)
		data = {'params': encText, 'encSecKey': encSecKey}
		return data

	def search(self, text):

		text = json.dumps(text)
		i = self.create_secret_key(16)
		encText = self.aes_encrypt(text, self.nonce)
		encText = self.aes_encrypt(encText, i)
		encSecKey = self.rsa_encrpt(i, self.pub_key, self.modulus)
		data = {'params': encText, 'encSecKey': encSecKey}
		return data

class search():

	'''
	跟歌单直接下载的不同之处，1.就是headers的referer
							  2.加密的text内容不一样！
							  3.搜索的URL也是不一样的
		输入搜索内容，可以根据歌曲ID进行下载，大家可以看我根据跟单下载那章，自行组合
	'''

	def __init__(self):
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
			'Host': 'music.163.com', 'Referer': 'http://music.163.com/search/'}  ###!!注意，搜索跟歌单的不同之处！！
		self.main_url = 'http://music.163.com/'
		self.session = requests.Session()
		self.session.headers = self.headers
		self.ep = Encrypyed()

	def search_song(self, search_content, search_type=1, limit=1):

		"""
		:param search_content: 音乐名
		:param search_type: 不知
		:param limit: 返回结果数量
		:return: 可以得到id 再进去歌曲具体的url
		"""
		url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='

		song_id_li = []
		song_name_li = []
		singer_li = []
		alia_li = []


		text = {'s': search_content, 'type': search_type, 'offset': 0, 'sub': 'false', 'limit': limit}
		data = self.ep.search(text)
		resp = self.session.post(url, data=data)
		result = resp.json()

		if result.get('result') is None:
			print('搜不到！！')
		elif result.get('result').get('songCount') <= 0:
			print('搜不到！！')
		else:
			songs = result['result']['songs']

			for song in songs:
				song_id, song_name, singer, alia = song['id'], song['name'], song['ar'][0]['name'], song['al']['name']
				song_id_li.append(song_id)
				song_name_li.append(song_name)
				singer_li.append(singer)
				alia_li.append(alia)
		return zip(song_id_li,song_name_li,singer_li,alia_li)



class singer_songs():

	def __init__(self):

		self.singername = 'no'

		self.alia = '默认'
	def get_html(self,singerid):
		proxy_addr = {'http': '61.135.217.7:80'}
		# 用的代理 ip，如果被封或者失效，在http://www.xicidaili.com/换一个
		headers = {
			'User-Agent':
				'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

		url = 'https://music.163.com/artist?id={}'.format(singerid)
		try:
			html = requests.get(url, headers=headers, proxies=proxy_addr).text
			return html
		except BaseException:
			print('request error')
			pass

	def get_top50(self,singerid):
		"""
		根据歌手id获取歌曲id和歌曲名称
		:param singerid:
		:return:
		"""
		html = self.get_html(singerid)
		soup = BeautifulSoup(html, 'lxml')
		info = soup.select('.f-hide #song-list-pre-cache a')

		songname = []
		songids = []
		singer = []
		alia = []
		for sn in info:
			songnames = sn.getText()
			songname.append(songnames)

			singer.append(self.singername)
			alia.append(self.alia)
		for si in info:
			songid = str(re.findall('href="(.*?)"', str(si))).strip().split('=')[-1].split('\'')[
				0]  # 用re查找，查找对象一定要是str类型
			songids.append(songid)
		return zip(songids,songname,singer,alia)


class download():

	def __init__(self):
		self.headers = {
		'Referer': 'https://music.163.com/',
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 "
		              "Safari/537.36"
	}

	def get_data(self,result):
		data = []

		for songid, songname, singer, alia in result:
			info = {}

			info.setdefault('歌曲ID', songid)
			info.setdefault('歌曲名字', songname.replace('/',''))
			info.setdefault('歌手名字', singer)
			info.setdefault('alia', alia)
			data.append(info)
		return data

	def save_song_new(self,songurl, path, songname):

		with open(path, 'wb') as f:
			try:

				respo = requests.get(songurl, headers=self.headers)

				f.write(respo.content)
				print('歌曲下载完成：' + songname)
			except BaseException:
				print('下载失败：' + songname)
				pass

	def song_download(self,songid, songname,downloadpath):
		songurl = 'http://music.163.com/song/media/outer/url?id={}'.format(songid)
		path = '{}/{}.mp3'.format(downloadpath,songname)
		self.save_song_new(songurl, path, songname)
		time.sleep(5)


	def get_lyrics(self,songids):
		url = 'http://music.163.com/api/song/lyric?id={}&lv=-1&kv=-1&tv=-1'.format(
			songids)
		headers = {
			'User-Agent':
				'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
		html = requests.get(url, headers=headers).text
		json_obj = json.loads(html)
		initial_lyric = json_obj['lrc']['lyric']
		reg = re.compile(r'\[.*\]')
		lyric = re.sub(reg, '', initial_lyric).strip()
		return lyric

	def lyrics_download(self,songname,path, songids):
		lyric = self.get_lyrics(songids)
		songname = songname.replace('/', '')
		print('正在保存歌曲：{}'.format(songname))

		with open('{}/{}.txt'.format(path,songname), 'a', encoding='utf-8')as f:
			f.write(lyric)





#######根据歌曲名称下载

def songnamedown():

	song_name_path = '/zhangkun/PycharmProjects/wangyisong/songs'
	song_down_path = '/zhangkun/PycharmProjects/wangyisong/ss'

	lyric_path = '/zhangkun/PycharmProjects/wangyisong/lyrics'
	d = search()

	down = download()
	with open(song_name_path,'r') as p:
		songname_c = p.readlines()
		for i in songname_c:
			print(i)
			result = list(d.search_song(i))
			print((result))
			data = down.get_data(result)

			# save2csv(data)
			if data:
				alone_song = data[0]

				songid = alone_song.get('歌曲ID')
				songname = alone_song.get('歌曲名字')
				path = '/zhangkun/PycharmProjects/wangyisong/song'
				down.song_download(songid,songname,path)

				down.lyrics_download(songname,lyric_path,songid)
			with open(song_down_path,'a') as f:
				f.write(i + '\n')

########根据歌手id下载
def singerdown():
	lyric_path = '/zhangkun/PycharmProjects/wangyisong/lyrics/4721'
	singer_so = singer_songs()

	down = download()

	singer_id = '4721'####歌手的id在热门歌手信息new.csv中查看
	result = list(singer_so.get_top50(singer_id))
	data = down.get_data(result)
	print(data)
	if data:
		for alone_song in data:
			songid = alone_song.get('歌曲ID')
			songname = alone_song.get('歌曲名字')
			path = '/zhangkun/PycharmProjects/wangyisong/songss'
			down.song_download(songid, songname, path)
			down.lyrics_download(songname, lyric_path,songid)

if __name__ == '__main__':

	# songnamedown()

	singerdown()