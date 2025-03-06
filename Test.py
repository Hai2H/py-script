from api.KuaFu import KuaFu
from database import BBSInfo

if __name__ == '__main__':
    bbs_info = BBSInfo(
        title="小巷人家 2024洗版✨纯净 4K 超高码【无台标收藏版 280G】",
        body="""<div class="message break-all" isfirst="1">
<p><img alt="" src="https://ts1.cn.mm.bing.net/th/id/R-C.4ab704edfc6847b9c32e3f69864d7b9c?rik=apx77zb%2bUlsCKQ&riu=http%3a%2f%2fn.sinaimg.cn%2fsinakd20231011ac%2f160%2fw1024h1536%2f20231011%2fe8d5-6b9f11093d86d1524c379578ee256673.jpg&ehk=OaJ108ABfq6rfccvCicUASwnghecCGCRVttM57tmE2M%3d&risl=&pid=ImgRaw&r=0" width="322"/></p>
<p>资源简介：豆瓣 <span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><span style="color: #234cee;"></span><a href="https://movie.douban.com/subject/36534750/" rel="nofollow noopener" target="_blank"><span style="color: #234cee;"><a _href="https://movie.douban.com/subject/36534750/" href="https://movie.douban.com/subject/36534750/" rel="nofollow" target="_blank"><span style="color:#234cee">https://movie.douban.com/subject/36534750/</span></a></span></a></p>
<p>📁 大小：63.4GB</p>
<p> </p>[ttreply]https://pan.quark.cn/s/42f51665363c[/ttreply]
<p>🔍 关键词：#小巷人家 #剧情 #家庭 #华语剧</p>
</div> """,
        node="剧集区"
    )
    kuafu = KuaFu(bbs_info)
    kuafu.update_kuafu(id=1980)
