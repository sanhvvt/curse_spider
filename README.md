# curse_spider

一个魔兽插件spider  
如果需要requests模块, 安装pip install requests  
自适应python2，python3  
python2: 依赖urllib2  
python3: 依赖urllib.request  

插件列表在config.json中, 可自己在该列表中按格式添加。  
id字段：需要去curse上获取， 不然无法获取该插件。  
name字段：自己定义该插件名字。  

"Addons": [  
       {"name": "details",              "id": 61284,  "enable": true},  
       {"name": "deadly-boss-mods",     "id": 3358,   "enable": true},  
       {"name": "weakauras-2",          "id": 65387,  "enable": true},  
       {"name": "bagnon",               "id": 1592,   "enable": true},  
       {"name": "method-dungeon-tools", "id": 288981, "enable": true},  
       {"name": "angry-keystones",      "id": 102522, "enable": true},  
       {"name": "championcommander",    "id": 300882, "enable": true},  
       {"name": "lunataotao",           "id": 301866, "enable": true},  
       {"name": "tullarange",           "id": 26753,  "enable": true},  
       {"name": "pawn",                 "id": 4646,   "enable": true},  
       {"name": "CovenantMissionHelper", "id": 434671, "enable": true}  
    ]  
 
