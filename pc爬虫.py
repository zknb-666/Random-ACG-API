
import requests      #爬虫
import re            #正则表达式
import urllib3

header={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'}#模拟浏览器头部，伪装成用户
urllib3.disable_warnings() #关闭证书警告

def get_url(base_url):
    # keyword=input("请输入英文关键词:(爬取排行榜请输入toplist)") 
    # if keyword=='toplist': 	#获取排行榜的url模板
    #    base_url=base_url+keyword+'?page='
    # else: 					#获取基于关键词的url模板
    # base_url=base_url+'search?q='+keyword+'&ratios=landscape'+'&sorting=random'+'&page='
    base_url=base_url+'search'
    return base_url         #返回模板


def get_img_url(base_url):
    params={'categories':'010','purity':'100','ratios':'landscape','topRange':'1w','sorting':'toplist','order':'desc','page':0}#参数字典
    img_url_list=[]#创建一个空列表
    print("开始为PC端爬取壁纸\n")
    page_num=1 #下载页数:(一页24张) 
    for num in range(1,int(page_num)+1): #循环遍历每页
        params['page']=	num	 #设置页数
        page_text=requests.get(url=base_url,headers=header,params=params,timeout=60,verify=False).content.decode() #获取url源代码
        ex='<a class="preview" href="(.*?)"' 
        img_url_list+=re.findall(ex,page_text,re.S) 	#利用正则表达式从源代码中截取每张壁纸缩略图的url并全部存放在一个列表中 
    return img_url_list					 #返回列表


def get_img_url_to_txt(img_url_list):
    filename="pc.txt"
    randimgs=open(filename,"w")	
    for i in range(len(img_url_list)): 			#循环遍历列表，对每张壁纸缩略图的url进行字符串的增删获得壁纸原图下载的url  注：jpg或png结尾
        x=img_url_list[i].split('/')[-1]  		#获取最后一个斜杠后面的字符串
        a=x[0]+x[1] 							#获取字符串的前两位
        img_url='https://w.wallhaven.cc/full/'+a+'/wallhaven-'+x  #拼接字符串,先默认jpg结尾
        format='.jpg'
        if not requests.get(url=img_url+''+format,headers=header).ok:						    #若网页返回值为404，则为png结尾
            format='.png'
        randimgs.write(img_url+''+format+"\n")
        print("链接:\n"+str(img_url+''+format)+"\n获取完成\n")
    randimgs.close()


def main(url):
    base_url=get_url(url) 
    img_url_list=get_img_url(base_url) 
    get_img_url_to_txt(img_url_list)

main('https://wallhaven.cc/')