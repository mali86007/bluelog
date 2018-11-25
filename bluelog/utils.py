from urllib.parse import urlparse, urljoin
from flask import request, redirect, url_for


def is_safe_url(target):
    """对URL进行安全验证"""
    ref_url = urlparse(request.host_url)        # 获取程序内的主机URL
    test_url = urlparse(urljoin(request.host_url, target))      # 拼接target完整的绝对路径
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc   # 网络协议正确并且两者网络位置一致则True


def redirect_back(default='blog.index', **kwargs):
    """获取上个页面的URL"""
    for target in request.args.get('next'), request.referrer:   # 从request.referrer和查询参数next中查找上页面URL
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)     # 目标URL通过安全验证则重定向
    return redirect(url_for(default, **kwargs))     # 未找到或未通过安全验证，转默认URL
