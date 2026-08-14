@echo off
echo Cleaning stale Kafka broker nodes from ZooKeeper...

REM Delete the old broker registration node (safe, won't affect logs)
"C:\kafka\kafka\bin\windows\zookeeper-shell.bat" localhost:2181 deleteall /brokers/ids/0

echo ZooKeeper cleanup complete.
