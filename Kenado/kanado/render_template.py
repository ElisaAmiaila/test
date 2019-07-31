import os
from jinja2 import Environment, FileSystemLoader


def render_template(template_name_or_list, **context):
    # 得到放置模板的目录

    path = '{}/temp/'.format(os.getcwd())

    # 创建一个加载器, jinja2 会从这个目录中加载模板
    loader = FileSystemLoader(path)

    # 用加载器创建一个环境, 有了它才能读取模板文件
    env = Environment(loader=loader)

    # 调用 get_template() 方法加载模板并返回
    template = env.get_template(template_name_or_list)

    html = template.render(**context)
    # print(html)
    return html
