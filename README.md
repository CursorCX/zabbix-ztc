### 1. ztc 说明
    zabbix 第三方模板, 涵盖大量监控项
    官方网址:
        https://bitbucket.org/rvs/ztc

### 2. php 监控
    针对 php-fpm 慢日志, 错误日志, 活动队列, 空闲进程等状态进行监控
    通过抓取 http://localhost/fpm_status 获取当前fpm状态, 得到活动队列, 空间数等相关消息
    通过分析fpm的慢日志和错误日志可以有效分析当天网站运行状态, 稳定情况

### 3. nginx 监控
    ztc 自带对nginx 状态的监控, 通过抓取 http://localhost/nginx_status, 得到当前nginx状态信息
    通过分析nginx日志,得到http状态码,采用seek方式,快速高效分析日志
    nginx_status 配置以及 fpm_status 的配置
    server {
        listen 80 default_server;
        server_name localhost;
        allow           127.0.0.1;
        deny            all;
        location /nginx_status {
            stub_status     on;
        }
        location /fpm_status {
            fastcgi_pass    127.0.0.1:9000;
            include         fastcgi_params;
        }
        location /apc_status {
            root /etc/nginx/document/stats_apc.php;
            fastcgi_pass    127.0.0.1:9099;
            include         fastcgi_params;
        }
    }

这里特别感谢huxos同学提供的宝贵意见 ^_^
