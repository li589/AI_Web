from bs4 import BeautifulSoup
import json

# 假设你已经使用 BeautifulSoup 解析了 HTML
html = """
<html>
    <body>
        <div id="content">
            <h1 class="title">Hello, World!</h1>
            <p class="description">This is a paragraph.</p>
        </div>
    </body>
</html>
"""

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html, 'html.parser')

# 将解析后的 HTML 转换为字典
def html_to_dict(element):
    if element.name is None:
        return element
    return {element.name: [html_to_dict(child) for child in element.children]}

# 转换为字典
element_dict = html_to_dict(soup)

# 将字典转换为 JSON 字符串
json_string = json.dumps(element_dict, ensure_ascii=False, indent=4)

print(json_string)