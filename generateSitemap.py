import os
import datetime

def create_sitemap(url, exclude_files=None):
    # 定义文件名和文件路径
    file_name = "sitemap1.xml"
    file_path = os.path.join("./", file_name)

    # 如果没有排除的文件列表，就设为空列表
    if exclude_files is None:
        exclude_files = []

    # 拼接xml字符串
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for file in os.listdir("./"):
        if file in exclude_files:
            continue
        if os.path.isdir(file):
            xml += f'<url>\n'
            xml += f'  <loc>{url}/{file}</loc>\n'
            # 获取文件的修改时间并转换成UTC格式
            lastmod = datetime.datetime.utcfromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%dT%H:%M:%S+00:00')
            xml += f'  <lastmod>{lastmod}</lastmod>\n'
            xml += f'  <changefreq>monthly</changefreq>\n'
            xml += f'  <priority>0.5</priority>\n'
            xml += f'</url>\n'
    xml += f'</urlset>\n'

    # 写入内容到文件
    with open(file_path, 'w') as f:
        f.write(xml)


# 测试代码
if __name__ == '__main__':
    exclude_files = ['1.md']
    url = f'https://studeyang.tech/technotes'
    create_sitemap(url, exclude_files)
