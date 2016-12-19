# pubuim-zabbix-Incoming
为 [pubu.im][1] 使用的 Zabbix 报警脚本  

------  

## 前置要求  
1. 需建立供外部访问的 Web 目录  
2. 了解 Zabbix 设置  
3. [阅读 Zabbix 自定义 alertscripts 文档][2]  
4. Python 编写能力 ( 你可能需要自行修复代码错误 )  
5. 创建 零信 团队以及频道，并阅读 零信 Incoming 应用文档  

## 安装  
1. 将 `pubuim.py` 放入 Zabbix Server `AlertScriptsPath` 目录中  
2. 在 `Administration -> Media type` 中创建 `Media types`：  
    `Name`： `PubuIM`  
    `Type`： `Script`  
    `Script name`： `pubuim.py`  
    `Script parameters`： `{ALERT.SENDTO}`、`{ALERT.SUBJECT}`、`{ALERT.MESSAGE}`  
3. 在 `Configuration -> Actions` 中创建 `Action`：  
    `Name`： `PubuIM`  
    `Subject`： `{TRIGGER.STATUS}: {TRIGGER.NAME}`  
    `operations -> New`： `Send message to users: Admin (Zabbix Administrator) via PubuIM`  
    `Message`：  
    Trigger: {TRIGGER.NAME}  
    Trigger status: {TRIGGER.STATUS}  
    Trigger severity: {TRIGGER.SEVERITY}  
      
    Hostname: {HOST.NAME}  
      
    Item value:  
    {ITEM.NAME1} ({ITEM.KEY1}): {ITEM.VALUE1}  
      
    Original event ID: {EVENT.ID}  
    ITEM ID: {ITEM.ID1}  

4. 转至 `零信` 添加 `Incoming`，并获取 `Token`  
    > https://hooks.pubu.im/services/[Token]  
5. 转至 `Zabbix` 添加用户 `Media`：  
    `Type`： `PubuIm`  
    `Send to`： `Token`  
5. 修改 `pubuim.py`  

## 屏幕截图  
![b8f7fac4e9f1341eb0e900e4eede6380.png](http://i.imgur.com/YxZh8Xk.png)  


  [1]: https://pubu.im/
  [2]: https://www.zabbix.com/documentation/3.0/manual/config/notifications/media/script
