import requests
import os
import re
from PIL import Image
import shutil

fid=input("请输入论文fid:")
jid=input("请输入JSESSIONID:")
if len(fid)!=32:
    print("fid格式错误")
    exit(0)
if len(jid)!=32 or jid!=jid.upper():
    print("JSESSIONID格式错误")
    exit(0)
try:
    int(fid,16)
except:
    print("fid格式错误")
    exit(0)
try:
    int(jid,16)
except:
    print("JSESSIONID格式错误")
    exit(0)


# 设置请求的 URL
url = "https://drm.fudan.edu.cn/read/jumpServlet"

# 设置请求参数（URL中的查询参数）
params = {
    "page": "0",
    "fid": fid,
    "userid": "",
    "visitid": ""
}
# 设置请求头
headers = {
    "Host": "drm.fudan.edu.cn",
    "Cookie": "JSESSIONID="+jid,
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Priority": "u=1, i"
}
pages={}
print("正在获取目录信息...")
while True:
    idx=str(len(pages))
    params["page"]=idx
    # 发送 GET 请求
    response = requests.get(url, params=params, headers=headers)

    # 输出响应内容
    if response.status_code!=200:
        break
    data=response.json()
    done=0
    for info in data["list"]:
        if info["id"]==idx:
            pages[idx]=info["src"]
            done=1
            break
    if not done:
        break

if len(pages)==0:
    print("请检查fid和JSESSIONID！")
    exit(0)

print(f"完成目录检索，论文共{idx}页，已找到{len(pages)}页")
filename=re.search(r'[?&]pdfname=([^&]+)', pages[list(pages.keys())[0]]).group(1).split(".")[0]

os.mkdir("./"+filename)
for idx in pages:
    print(f"正在获取论文内容：{idx}/{len(pages)}页",end="\r")
    page=pages[idx]
    response = requests.get(page)
    if response.status_code==200:
        open("./"+filename+"/"+idx.rjust(3,"0")+".jpeg",'wb').write(response.content)

print("\n已保存至"+filename+"文件夹！")

png_files=os.listdir("./"+filename+"/")

# 打开第一张图片作为 PDF 的基础
first_image = Image.open("./"+filename+"/"+png_files[0])

# 将后续图片打开，并存入一个列表
images = []
for png in png_files[1:]:
    img = Image.open("./"+filename+"/"+png)
    img = img.convert("RGB")  # 转换为 RGB 格式，因为 PDF 不支持透明通道
    images.append(img)

# 将所有图片保存为一个 PDF 文件
first_image.save(filename+".pdf", save_all=True, append_images=images)

shutil.rmtree("./" + filename + "/")

print(filename+".pdf文件已成功生成！")