-- 建立測試資料庫
create database [PartitionTest]
GO

-- 建立 4 個 FILEGROUP 
alter database [PartitionTest] add filegroup [PartitionTestFG201801];
alter database [PartitionTest] add filegroup [PartitionTestFG201802];
alter database [PartitionTest] add filegroup [PartitionTestFG201803];
alter database [PartitionTest] add filegroup [PartitionTestFG999999];

use [PartitionTest]
GO
declare @path nvarchar(128);
declare @PTR int ;
declare @ID  varchar(2)
declare @SQL VARCHAR(1000)

select @path=physical_name from sys.database_files where file_id =1

-- 每個 FileGroup 至少要指定一個檔案
set @PTR = 1
while @PTR < 4
begin
  set @ID = RIGHT('00'+LTRIM(STR(@PTR)),2 )
  set @SQL = 'alter database [PartitionTest] add file ( name=[PartitionTestFile2018'+@ID+'_1], filename="'+@path+'PartitionTestFile2018'+@ID+'_1.ndf", size=10MB ) to filegroup [PartitionTestFG2012'+@ID+']' ;
  exec( @SQL )
  set @PTR += 1
end 
set @SQL = 'alter database [PartitionTest] add file ( name=[PartitionTestFile999999_1], filename="'+@path+'PartitionTestFile'+@ID+'_1.ndf", size=10MB ) to filegroup [PartitionTestFG999999]' ;
exec( @SQL )