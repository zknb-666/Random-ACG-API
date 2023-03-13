
import requests      #爬虫
import re            #正则表达式
import os            #文件操作
import shutil        #删除非空文件夹库


def get_url(base_url):
    #keyword=input("请输入英文关键词:(爬取排行榜请输入toplist)") 
    #if keyword=='toplist': 	#获取排行榜的url模板
     #   base_url=base_url+keyword+'?page='
    #else: 					#获取基于关键词的url模板
    #base_url=base_url+'search?q='+keyword+'&ratios=landscape'+'&sorting=random'+'&page='
    base_url=base_url+'search?categories=010&purity=100&ratios=landscape&topRange=1d&sorting=toplist&order=desc'
    return base_url         #返回模板


def get_img_url(base_url):
    header={ 
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'
    } 									 #模拟浏览器头部，伪装成用户
    img_url_list=[]		 				 #创建一个空列表
    print("开始为PC端爬取壁纸\n")
    page_num=1 #input("请输入下载页数:(一页24张)") 
    for num in range(1,int(page_num)+1): #循环遍历每页
        new_url=base_url+str(num)  		 #将模板进行拼接得到每页壁纸完整的url(实质:字符串的拼接)
        page_text=requests.get(url=new_url,headers=header).text #获取url源代码
        ex='<a class="preview" href="(.*?)"' 
        img_url_list+=re.findall(ex,page_text,re.S) 	#利用正则表达式从源代码中截取每张壁纸缩略图的url并全部存放在一个列表中 
    return img_url_list					 #返回列表


def download_img(img_url_list):
    header={ 
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'
    }           #模拟浏览器头部，伪装成用户
    if os.path.exists('pc'):
        shutil.rmtree('pc')
    os.mkdir('pc')
    filename="pc.txt"
    randimgs=open(filename,"w")	
    for i in range(len(img_url_list)): 			#循环遍历列表，对每张壁纸缩略图的url进行字符串的增删获得壁纸原图下载的url  注：jpg或png结尾
        x=img_url_list[i].split('/')[-1]  		#获取最后一个斜杠后面的字符串
        a=x[0]+x[1] 							#获取字符串的前两位
        img_url='https://w.wallhaven.cc/full/'+a+'/wallhaven-'+x+'.jpg'  #拼接字符串,先默认jpg结尾
        code=requests.get(url=img_url,headers=header).status_code 
        if code==404:						    #若网页返回值为404，则为png结尾
            img_url='https://w.wallhaven.cc/full/'+a+'/wallhaven-'+x+'.png'
            code=requests.get(url=img_url,headers=header).status_code
        elif code==403:
            continue
        img_data=requests.get(url=img_url,headers=header,timeout=20).content  #获取壁纸图片的二进制数据,加入timeout限制请求时间
        img_name=img_url.split('-')[-1] 		#生成图片名字
        img_path='pc'+'/'+img_name			    #生成图片存储路径
        with open(img_path,'wb') as fp:		    #('w':写入,'b':二进制格式)
            fp.write(img_data)
            print(img_name,'下载成功')     	
        randimgs.write('https://jihulab.com/zknb-666/wallhavenrequests/-/raw/main/pc/'+str(img_name)+'\n')
        print("链接:\n"+str(img_url)+"\n获取完成\n")
    randimgs.close()


def main(url):
    base_url=get_url(url) 
    img_url_list=get_img_url(base_url) 
    download_img(img_url_list)

main('https://wallhaven.cc/')