# redis_db_bak
脚本简介：redis主从架构，主redis用来提供服务，备reids用来进行持久化以及备点。但是此种模式有一个bug，当主redis服务重启或者主redis服务器重启，会导致备redis的持久化文件丢失。
