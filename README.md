### 说明
一个以cmd风格运行的web网站，基于Flask框架。更多信息请参考 [https://imnicy.com/webcmd/document](https://imnicy.com)

### 在线示例
[https://cmd.imnicy.com](https://cmd.imnicy.com)

### 安装

```shell script
$ git clone git@github.com:imnicy/webcmd.git
$ pip install pipenv
$ pipenv --python python3
$ pipenv install
```

安装完虚拟环境之后设置Flask启动脚本。

Unix Bash（Linux，Mac等）：

```shell script
$ export FLASK_APP=app
$ flask run
```

Windows CMD：

```shell script
> set FLASK_APP=hello
> flask run
```

或者使用python-dotenv环境配置文件

在项目目录下创建 `.env` 文件然后写入：

```shell script
FLASK_APP=app
```

然后使用`flask run`启动项目

