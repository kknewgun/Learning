## day1
* 列出目錄內容
```bash
ls -l
ls -a
```
* 	顯示目前所在路徑
```bash
pwd
```
* 建立資料夾與檔案
```bash
mkdir mytest
cd mytest
touch file1.txt file2.txt
```
* 複製與重新命名檔案
```bash
cp file1.txt copy_file1.txt
mv file2.txt renamed_file2.txt
```
* 刪除檔案與資料夾
```bash
rm copy_file1.txt
cd ..
rm -r mytest
```
* 一次顯示整個檔案內容
```bash
cat fruits.txt
```
* 分頁顯示，可上下捲動（q 退出）
```bash
less fruits.txt
```
* 顯示前 N 行（預設 10）
```bash
head fruits.txt
head -3 fruits.txt
```
* 顯示最後 N 行
```bash
tail fruits.txt
tail -2 fruits.txt
```
* 找出所有有 banana 的行
```bash
grep banana fruits.txt
```
* 搜尋不分大小寫
```bash
grep -i Banana fruits.txt
```
* 顯示行號
```bash
grep -n banana fruits.txt
```
* 在目前目錄找出所有 .txt 檔
```bash
find . -name "*.txt"
```
* 找出所有檔案名含 banana
```bash
find . -name "*banana*"
```
*  pipe (|) 與 xargs
```bash
# 會對 ids.txt 中的每一行內容，印出 User ID is xxx
cat ids.txt | xargs -I {} echo "User ID is {}"
# 新增 3個檔案
touch file1.log file2.log file3.log  
# 找到目錄下副檔名是log的放到{} sh-c 對{}內的執行命令echo -e "apple\nbanana"
find . -name "*.log" | xargs -I{} sh -c 'echo -e "apple\nbanana" > "{}"'
```
* 壓縮備份
```bash
# 將log資料夾壓縮成gzip 格式的 tar 檔 檔名logs_backup.tar.gz
tar -czvf  logs_backup.tar.gz logs
# 解壓gzip 壓縮的 tar data.tar.gz
tar -xzvf data.tar.gz
# error.log 壓縮成 gzip 格式
gzip error.log
# 解壓 report.zip
unzip report.zip
# tar 壓縮參數
# -c 壓縮, (-j 用bzip2壓縮 -z 用gz壓縮), -v 顯示過程, -f name 輸出檔名
tar -cjvf project.tar.bz2 project
# 壓縮多檔 (gzip是單檔、zip多檔)
zip files.zip a.txt b.txt c.txt
# 把資料夾 source/ 備份到 /backup/source/，並保留檔案權限和時間
rsync -av source/ /backup/source/
# 只備份檔案大小有異動的
rsync -r --size-only docs/ /backup/docs/
# 備份時排除 .git 資料夾
rsync -av --exclude='.git' source/ destination/
# 備份時排除 .git .vs .bin 資料夾
rsync -av --exclude='.git' --exclude='.vs' --exclude='.bin' source/ destination/
# 備份時排除 .git .vs .bin 資料夾(使用排除清單)
echo -e  '.bin/\n.vs/\n.git/' > filter.txt
rsync -av --exclude-from=filter.txt source/ backup/docs/
```
* 基礎網路排查
```bash
ping
traceroute
netstat
nslookup
ss
mtr 
```