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
