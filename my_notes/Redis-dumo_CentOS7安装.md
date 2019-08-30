#### 关于redis-dump 安装遇到的问题以及解决方案

<hr>

##### 安装平台: centos7

```bash
[root@VM_16_15_centos ~]# redis-dump
-bash: redis-dump: command not found
```

没有安装这个管理工具[不想看过程的可以看末尾精华版]

因为这个工具是基于`Ruby`实现的，首先要安装`Ruby`

##### 一：安装Ruby

参考：[Ruby官方](http://www.ruby-lang.org/zh_cn/documentation/installation)

示例：centos (模拟输入和部分输出, 可以在 `install `前面添加 `-y` 把后面的手动选择`y`自动化)

```bash
[root@VM_16_15_centos ~]# yum install ruby  
Loaded plugins: fastestmirror, langpacks
Repository epel is listed more than once in the configuration
Loading mirror speeds from cached hostfile
```

##### 二：尝试安装 redis-dump

```bash
[root@VM_16_15_centos ~]# gem install redis-dump
Fetching: yajl-ruby-1.4.1.gem (100%)
Building native extensions.  This could take a while...
ERROR:  Error installing redis-dump:
	ERROR: Failed to build gem native extension.

    /usr/bin/ruby extconf.rb
mkmf.rb can't find header files for ruby at /usr/share/include/ruby.h
```

这里还是报错

我就不说什么原因了，直接开始解决。先安装这个

```bash
[root@VM_16_15_centos ~]# yum -y install ruby ruby-devel
Loaded plugins: fastestmirror, langpacks
Repository epel is listed more than once in the configuration
Loading mirror speeds from cached hostfile
Package ruby-2.0.0.648-35.el7_6.x86_64 already installed and latest version
Package ruby-devel-2.0.0.648-35.el7_6.x86_64 already installed and latest version
```

然后安装这个

```bash
[root@VM_16_15_centos ~]# yum -y install rubygems
Loaded plugins: fastestmirror, langpacks
Repository epel is listed more than once in the configuration
Loading mirror speeds from cached hostfile
Package rubygems-2.0.14.1-35.el7_6.noarch already installed and latest version
```

```bash
...暂时先别动，替换下国内源，加个速度，然后再复制它的提示指令继续操作...
```

替换的指令为

```bash
[root@VM_16_15_centos ~]# gem sources --add https://gems.ruby-china.com/ --remove https://rubygems.org/
查询状态指令
[root@VM_16_15_centos ~]# gem sources -l
*** CURRENT SOURCES ***

https://gems.ruby-china.com/
```

###### 然后继续尝试安装

```bash
[root@VM_16_15_centos ~]# gem install redis-dump
Fetching: yajl-ruby-1.4.0.gem (100%)
Building native extensions.  This could take a while...
Successfully installed yajl-ruby-1.4.0
Fetching: redis-4.0.1.gem (100%)
ERROR:  Error installing redis-dump:
	redis requires Ruby version >= 2.2.2.
```

```bash
[root@VM_16_15_centos ~]# yum install curl
Loaded plugins: fastestmirror, langpacks
Repository epel is listed more than once in the configuration
Loading mirror speeds from cached hostfile
Package curl-7.29.0-51.el7_6.3.x86_64 already installed and latest version
```

然后通过上一步安装好的 curl安装下面的这个, 部分提示如下

```bash
[root@VM_16_15_centos ~]# [root@VM_16_15_centos ~]# curl -L get.rvm.io | bash -s stable
····部分提示如下····
gpg2 --keyserver hkp://pool.sks-keyservers.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB

or if it fails:

    command curl -sSL https://rvm.io/mpapis.asc | gpg2 --import -
    command curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import -

In case of further problems with validation please refer to https://rvm.io/rvm/security
```

复制它的指令，再继续

```bash
[root@VM_16_15_centos ~]# curl -sSL https://rvm.io/mpapis.asc | gpg2 --import -
[root@VM_16_15_centos ~]# curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import -
```

然后重试，这一步会等比较久

```bash
[root@VM_16_15_centos ~]# curl -L get.rvm.io | bash -s stable
```

##### 这里之后需要使 rvm指令生效

```bash
[root@VM_16_15_centos local]# cd /etc/profile.d
[root@VM_16_15_centos local]# ls
这里会看到有个 `rvm.sh` 的文件,然后
[root@VM_16_15_centos profile.d]# source rvm.sh
```

然后使用一下`rvm -v`检测 `rvm` 是否可用

可用的话查看 `rvm` 里面的支持的东西

```bash
[root@VM_16_15_centos ~]# rvm list known
```

##### 因为安装 那个需要 Ruby 等级大于2.2.2.

我直接安装了 2.3

```bash
[root@VM_16_15_centos ~]# rvm install 2.3
```

安装好了之后就可以安装 redis-dump了

```bash
[root@VM_16_15_centos ~]# gem install redis-dump
```

##### 然后检测成功了吗

```bash
[root@VM_16_15_centos ~]# redis-dump
[root@VM_16_15_centos ~]# redis-load
Usage: cat dumpfile_db15.json | redis-load -d 15
```

看来是成功了,读取一下我存在内存中的 redis内容看看情况

```bash
[root@VM_16_15_centos ~]# redis-dump -u localhost:6379
{"db":0,"key":"hello","ttl":-1,"type":"string","value":"nihao","size":5}
{"db":0,"key":"funny","ttl":-1,"type":"string","value":"kaixin","size":6}
{"db":0,"key":"school","ttl":-1,"type":"string","value":"xuexiao","size":7}
```

### 大功告成

### 精华版

```bash
[root@VM_16_15_centos ~]# yum install ruby 
[root@VM_16_15_centos ~]# yum -y install ruby ruby-devel
[root@VM_16_15_centos ~]# yum -y install rubygems
[root@VM_16_15_centos ~]# gem sources --add https://gems.ruby-china.com/ --remove https://rubygems.org/
[root@VM_16_15_centos ~]# yum install curl
[root@VM_16_15_centos ~]# curl -sSL https://rvm.io/mpapis.asc | gpg2 --import -
[root@VM_16_15_centos ~]# curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import -
[root@VM_16_15_centos ~]# curl -L get.rvm.io | bash -s stable
[root@VM_16_15_centos local]# cd /etc/profile.d
[root@VM_16_15_centos profile.d]# source rvm.sh
[root@VM_16_15_centos ~]# rvm install 2.3
[root@VM_16_15_centos ~]# gem install redis-dump
```

