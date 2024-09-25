
# Find spark

PySpark isn't on sys.path by default, but that doesn't mean it can't be used as a regular library.
You can address this by either symlinking pyspark into your site-packages,
or adding pyspark to sys.path at runtime. `findspark` does the latter.

To initialize PySpark, just call

```python
import findspark
findspark.init()

import pyspark
sc = pyspark.SparkContext(appName="myAppName")
```

Without any arguments, the SPARK_HOME environment variable will be used,
and if that isn't set, other possible install locations will be checked. If
you've installed spark with

    brew install apache-spark

on OS X, the location `/usr/local/opt/apache-spark/libexec` will be searched.

Alternatively, you can specify a location with the `spark_home` argument.

```python
findspark.init('/path/to/spark_home')
```

To verify the automatically detected location, call

```python
findspark.find()
```

Findspark can add a startup file to the current IPython profile so that the environment vaiables will be properly set and pyspark will be imported upon IPython startup. This file is created when `edit_profile` is set to true.

```
ipython --profile=myprofile
findspark.init('/path/to/spark_home', edit_profile=True)
```

Findspark can also add to the .bashrc configuration file if it is present so that the environment variables will be properly set whenever a new shell is opened. This is enabled by setting the optional argument `edit_rc` to true.

```python
findspark.init('/path/to/spark_home', edit_rc=True)
```

If changes are persisted, findspark will not need to be called again unless the spark installation is moved.

python setup.py sdist
conda install pyspark -y

# conda 打包
conda install --use-local findspark_msxf-1.0-0.tar.bz2

conda build --output-folder ./out/ conda/

conda-build findspark

tar -zcvf findspark-msxf.tar.gz ./conda-bld/

tar -tvjf /root/anaconda3/envs/myenv/conda-bld/linux-64/findspark_msxf-1.1.3-py38_0.tar.bz2


# pyspark 模板
<!-- 确保已安装 findspark_msxf (pip install findspark_msxf.1.tar.gz) -->

import argparse
import sys
import findspark

global spark
def main(args):
    print(f"接收到的参数 args: {args}")
    global spark
    spark = findspark.init(args=args)

    # python 依赖文件添加方式
    # spark.sparkContext.addPyFile("./subfile_1.py")
    # spark.sparkContext.addFile("./subfile_1.py")

    # 业务代码
    spark.sql("select 1").show()

    # spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process pySpark arguments.")

    # 添加参数
    parser.add_argument("--name", type=str, default="msxfFr")
    parser.add_argument("--master", type=str, default="yarn")
    parser.add_argument("--spark.yarn.dist.archives", type=str, default="./env7_2.tar.gz#environment")

    args, unknown = parser.parse_known_args()
    main(args)