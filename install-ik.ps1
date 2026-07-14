# 1. 解压插件包到临时目录
Expand-Archive -Path opensearch-analysis-ik-2.11.1.zip -DestinationPath analysis-ik-temp -Force

# 2. 在容器中创建插件目录
docker exec career-opensearch mkdir -p /usr/share/opensearch/plugins/analysis-ik

# 3. 复制插件文件到容器（分步复制所有文件）
# 复制 JAR 文件
docker cp analysis-ik-temp/opensearch-analysis-ik-2.11.1.jar career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
docker cp analysis-ik-temp/plugin-descriptor.properties career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
docker cp analysis-ik-temp/plugin-security.policy career-opensearch:/usr/share/opensearch/plugins/analysis-ik/

# 复制依赖库
docker cp analysis-ik-temp/commons-codec-1.11.jar career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
docker cp analysis-ik-temp/commons-logging-1.2.jar career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
docker cp analysis-ik-temp/httpclient-4.5.13.jar career-opensearch:/usr/share/opensearch/plugins/analysis-ik/
docker cp analysis-ik-temp/httpcore-4.4.13.jar career-opensearch:/usr/share/opensearch/plugins/analysis-ik/

# 复制 config 目录
docker exec career-opensearch mkdir -p /usr/share/opensearch/plugins/analysis-ik/config
docker cp analysis-ik-temp/config/. career-opensearch:/usr/share/opensearch/plugins/analysis-ik/config/

# 4. 修复文件权限
docker exec -u root career-opensearch chown -R opensearch:opensearch /usr/share/opensearch/plugins/analysis-ik

# 5. 清理临时文件
Remove-Item -Recurse -Force analysis-ik-temp

# 6. 重启 OpenSearch 容器
docker-compose restart opensearch