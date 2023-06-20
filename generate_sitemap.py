import datetime
import os

url = 'https://studeyang.tech/technotes/#'
file_path = "./sitemap.xml"
exclude_files = [
    'coverpage', 'navbar', 'README', 'sidebar',
    'A类/README', 'A类/Python/README', 'A类/Python/sidebar',
    'B类/README', 'B类/sidebar',
    'C类/README', 'C类/sidebar',
    'D类/README', 'D类/sidebar', 'D类/D04-职业规划/20180808知识地图认定--整理', 'D类/D04-职业规划/202009月知识梳理计划', 'D类/D04-职业规划/202010月面试计划',
    'D类/D07-anki/知识转Anki进度', 'D类/D08-杂谈/一些idea', 'D类/D08-杂谈/面试题',
    '资源/学习资源'
]


def create_sitemap():
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, dirs, files in os.walk("./"):
        for file in files:
            if not file.endswith('.md'):
                continue
            try:
                if not path.endswith('/'):
                    path += '/'
                new_path = (path.replace('\\', '/') + file)[2:-3]
                if new_path in exclude_files:
                    continue
                print(new_path)
                xml += '  <url>\n'
                xml += f'    <loc>{url}/{new_path}</loc>\n'
                lastmod = datetime.datetime.utcfromtimestamp(os.path.getmtime(path + file)).strftime('%Y-%m-%d')
                xml += f'    <lastmod>{lastmod}</lastmod>\n'
                xml += '    <changefreq>monthly</changefreq>\n'
                xml += '    <priority>0.5</priority>\n'
                xml += '  </url>\n'
            except Exception as e:
                print(path, file, e)
                break
    xml += f'</urlset>\n'

    with open(file_path, 'w', encoding='utf-8') as sitemap:
        sitemap.write(xml)


if __name__ == '__main__':
    create_sitemap()
