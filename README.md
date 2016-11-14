# music
music acquisition and data analysis, especially music recommendation.

## Task
1. 基于作词/作曲的相似推荐
2. 同名音乐热度排行

## Process
1. 爬取框架建立，先遍历歌手（筛选华人歌手），再根据歌手热门TOP200爬取歌曲信息。
2. 遭遇防爬，把间隔调整到1s以上能解决，但是速度太慢了。

## Reading

### 怎样防爬

作者：董伟明
链接：https://www.zhihu.com/question/20899988/answer/124261539
来源：知乎
著作权归作者所有，转载请联系作者获得授权。

1. 不要用一个IP狂爬。所以要准备一堆可用的代理IP，如果公司有额外的比较闲的IP最好了，闲着也是闲着，在不影响正常业务的提前下，多换IP。否则就要想办法获取免费代理。我的书中这个地方有写。
2. 勤换UA。我看很多人喜欢在配置中列一些UA, 其实吧，可以使用 GitHub - hellysmile/fake-useragent: up to date simple useragent faker with real world database。其实我也推荐大家伪装成各大搜索网站的UA， 比如Google UA 有这样一些 Google 抓取工具，说到这里，有的网站，你添加referfer字段是搜索网站也是有用的，因为网站是希望被索引的，所以会放宽搜索引擎的爬取策略。
3. 爬取间隔自适应。就是已经限制了你这个IP的抓取，就不要傻傻重复试，怎么滴也得休息一会。网易云音乐操作起来比较简单，sleep一下就好了。其实sleep的间隔应该按情况累加，比如第一次sleep 10秒，发现还是被约束。那么久sleep 20秒... 这个间隔的设置已经自适应的最终效果是经验值。
4. 验证码识别。现在攻防让验证码技术层出不穷，其实好多都是自己写算法识别，并不开源，开源的就是tesseract，还可以借用百度识图平台试试。我个人还是倾其所有的做好其他的地方，不要让人家弹出验证码让我输入。