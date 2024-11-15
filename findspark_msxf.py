
"""Find spark home, and initialize by adding pyspark to sys.path.

If SPARK_HOME is defined, it will be used to put pyspark on sys.path.
Otherwise, common locations for spark will be searched.
"""

from glob import glob
import os
import sys
import argparse
import subprocess
import hashlib

__version__ = "2.0.1"


def find():
    """Find a local spark installation.

    Will first check the SPARK_HOME env variable, and otherwise
    search common installation locations, e.g. from homebrew
    """
    spark_home = os.environ.get("SPARK_HOME", None)

    if not spark_home:
        if "pyspark" in sys.modules:
            return os.path.dirname(sys.modules["pyspark"].__file__)
        for path in [
            "/usr/local/opt/apache-spark/libexec",  # macOS Homebrew
            "/usr/lib/spark/",  # AWS Amazon EMR
            "/usr/local/spark/",  # common linux path for spark
            "/opt/spark/",  # other common linux path for spark
            # Any other common places to look?
        ]:
            if os.path.exists(path):
                spark_home = path
                break

    if not spark_home:
        # last resort: try importing pyspark (pip-installed, already on sys.path)
        try:
            import pyspark
        except ImportError:
            pass
        else:
            spark_home = os.path.dirname(pyspark.__file__)

    if not spark_home:
        raise ValueError(
            "Couldn't find Spark, make sure SPARK_HOME env is set"
            " or Spark is in an expected location (e.g. from homebrew installation)."
        )

    return spark_home


def _edit_rc(spark_home, sys_path=None):
    """Persists changes to environment by changing shell config.

    Adds lines to .bashrc to set environment variables
    including the adding of dependencies to the system path. Will only
    edit this file if they already exist. Currently only works for bash.

    Parameters
    ----------
    spark_home : str
        Path to Spark installation.
    sys_path: list(str)
        Paths (if any) to be added to $PYTHONPATH.
        Should include python subdirectory of Spark installation, py4j
    """

    bashrc_location = os.path.expanduser("~/.bashrc")

    if os.path.isfile(bashrc_location):
        with open(bashrc_location, "a") as bashrc:
            bashrc.write("\n# Added by findspark\n")
            bashrc.write("export SPARK_HOME={}\n".format(spark_home))
            if sys_path:
                bashrc.write(
                    "export PYTHONPATH={}\n".format(
                        os.pathsep.join(sys_path + ["$PYTHONPATH"])
                    )
                )
            bashrc.write("\n")


def _edit_ipython_profile(spark_home, sys_path=None):
    """Adds a startup file to the current IPython profile to import pyspark.

    The startup file sets the required environment variables and imports pyspark.

    Parameters
    ----------
    spark_home : str
        Path to Spark installation.
    sys_path : list(str)
        Paths to be added to sys.path.
        Should include python subdirectory of Spark installation, py4j
    """
    from IPython import get_ipython

    ip = get_ipython()

    if ip:
        profile_dir = ip.profile_dir.location
    else:
        from IPython.utils.path import locate_profile

        profile_dir = locate_profile()

    startup_file_loc = os.path.join(profile_dir, "startup", "findspark_msxf.py")

    with open(startup_file_loc, "w") as startup_file:
        # Lines of code to be run when IPython starts
        startup_file.write("import sys, os\n")
        startup_file.write("os.environ['SPARK_HOME'] = {}\n".format(repr(spark_home)))
        if sys_path:
            startup_file.write("sys.path[:0] = {}\n".format(repr(sys_path)))
        startup_file.write("import pyspark\n")


# def init(spark_home=None, python_path=None, edit_rc=False, edit_profile=False):
#     """Make pyspark importable.
#
#     Sets environment variables and adds dependencies to sys.path.
#     If no Spark location is provided, will try to find an installation.
#
#     Parameters
#     ----------
#     spark_home : str, optional, default = None
#         Path to Spark installation, will try to find automatically
#         if not provided.
#     python_path : str, optional, default = None
#         Path to Python for Spark workers (PYSPARK_PYTHON),
#         will use the currently running Python if not provided.
#     edit_rc : bool, optional, default = False
#         Whether to attempt to persist changes by appending to shell
#         config.
#     edit_profile : bool, optional, default = False
#         Whether to create an IPython startup file to automatically
#         configure and import pyspark.
#     """
#
#     if not spark_home:
#         spark_home = find()
#
#     if not python_path:
#         python_path = os.environ.get("PYSPARK_PYTHON", sys.executable)
#
#     # ensure SPARK_HOME is defined
#     os.environ["SPARK_HOME"] = spark_home
#
#     # ensure PYSPARK_PYTHON is defined
#     os.environ["PYSPARK_PYTHON"] = python_path
#
#     # add pyspark to sys.path
#
#     if "pyspark" not in sys.modules:
#         spark_python = os.path.join(spark_home, "python")
#         try:
#             py4j = glob(os.path.join(spark_python, "lib", "py4j-*.zip"))[0]
#         except IndexError:
#             raise Exception(
#                 "Unable to find py4j in {}, your SPARK_HOME may not be configured correctly".format(
#                     spark_python
#                 )
#             )
#         sys.path[:0] = sys_path = [spark_python, py4j]
#     else:
#         # already imported, no need to patch sys.path
#         sys_path = None
#
#     if edit_rc:
#         _edit_rc(spark_home, sys_path)
#
#     if edit_profile:
#         _edit_ipython_profile(spark_home, sys_path)

# 假设其他函数如 find, _edit_rc, _edit_ipython_profile 等已经定义好
def init(spark_home="/opt/spark-msxf-3.2.1", 
         python_path=None, 
         edit_rc=False, 
         edit_profile=False, 
         args=None, 
         envName=None, 
         forcePackage=False,
         appName=None):
    """Make pyspark importable and initializes a SparkSession.

    Sets environment variables and adds dependencies to sys.path.
    If no Spark location is provided, will try to find an installation.
    Optionally parses command line arguments and initializes a SparkSession.

    Parameters
    ----------
    spark_home : str, optional, default = None
        Path to Spark installation, will try to find automatically
        if not provided.
    python_path : str, optional, default = None
        Path to Python for Spark workers (PYSPARK_PYTHON),
        will use the currently running Python if not provided.
    edit_rc : bool, optional, default = False
        Whether to attempt to persist changes by appending to shell
        config.
    edit_profile : bool, optional, default = False
        Whether to create an IPython startup file to automatically
        configure and import pyspark.
    args : argparse.Namespace, optional, default = None
        Parsed command line arguments to be used for initializing SparkSession.

    Returns
    -------
    SparkSession
        A SparkSession instance initialized with given parameters.
    """

    if not spark_home:
        spark_home = find()

    if not python_path:
        python_path = os.environ.get("PYSPARK_PYTHON", sys.executable)

    # 确保 SPARK_HOME 和 PYSPARK_PYTHON 被设置
    os.environ["SPARK_HOME"] = spark_home
    # os.environ["PYSPARK_PYTHON"] = python_path

    # 获取环境变量 PYSPARK_PYTHON 的值
    py_spark_python = os.environ.get('PYSPARK_PYTHON')

    # 如果 PYSPARK_PYTHON 不存在，则设置一个默认值
    if py_spark_python is None:
        default_python_path = './environment/bin/python'
        os.environ['PYSPARK_PYTHON'] = default_python_path
        print(f"Set PYSPARK_PYTHON to {default_python_path}")
    else:
        print(f"PYSPARK_PYTHON is already set to {py_spark_python}, no action needed.")

    # 将 pyspark 添加到 sys.path
    if "pyspark" not in sys.modules:
        spark_python = os.path.join(spark_home, "python")
        try:
            py4j = glob(os.path.join(spark_python, "lib", "py4j-*.zip"))[0]
        except IndexError:
            raise Exception(
                "Unable to find py4j in {}, your SPARK_HOME may not be configured correctly".format(
                    spark_python
                )
            )
        sys.path[:0] = sys_path = [spark_python, py4j]
    else:
        # 如果已经导入 pyspark，就不需要再修改 sys.path
        sys_path = None

    if edit_rc:
        _edit_rc(spark_home, sys_path)

    if edit_profile:
        _edit_ipython_profile(spark_home, sys_path)
        
    # 打包conda环境
    if envName and os.getenv('JUPYTER_TOKEN'):
        package_path = export_conda_env_yaml_and_compute_md5(envName, forcePackage)
    else:
        package_path = None

    # 根据 args 参数初始化 SparkSession
    from pyspark.sql import SparkSession
    builder = SparkSession.builder

    if args:
        assert isinstance(args, argparse.Namespace), "args must be an instance of argparse.Namespace"

        # 构建 SparkSession 配置
        if appName is None:
            appName = 'pyspark_app'

        builder = builder.appName(appName)
        # builder = builder.appName(getattr(args, 'appName', "pyspark_app"))
        builder = builder.master(getattr(args, 'master', "local[*]"))

        # 添加其他配置参数
        for arg in vars(args):
            if arg.startswith("spark."):
                value = getattr(args, arg)
                if value is not None:
                    builder = builder.config(arg, value)
    
    yarn_queue_name = get_yarn_queue_name('/tmp/pySparkParam.txt')
    if yarn_queue_name:
        print(f"spark.yarn.queue: {yarn_queue_name}")
        builder = builder.config("spark.yarn.queue", yarn_queue_name)
    
    if package_path:
        builder.config("spark.yarn.dist.archives", f"{package_path}#environment")
    # 创建 SparkSession
    spark_session = builder.getOrCreate()

    return spark_session


def _add_to_submit_args(to_add):
    """Add string s to the PYSPARK_SUBMIT_ARGS env var"""
    existing_args = os.environ.get("PYSPARK_SUBMIT_ARGS", "")
    if not existing_args:
        # if empty, start with default pyspark-shell
        # ref: pyspark.java_gateway.launch_gateway
        existing_args = "pyspark-shell"
    # add new args to front to avoid insert after executable
    submit_args = "{} {}".format(to_add, existing_args)
    os.environ["PYSPARK_SUBMIT_ARGS"] = submit_args
    return submit_args


def add_packages(packages):
    """Add external packages to the pyspark interpreter.

    Set the PYSPARK_SUBMIT_ARGS properly.

    Parameters
    ----------
    packages: list of package names in string format
    """

    # if the parameter is a string, convert to a single element list
    if isinstance(packages, str):
        packages = [packages]

    _add_to_submit_args("--packages " + ",".join(packages))


def add_jars(jars):
    """Add external jars to the pyspark interpreter.

    Set the PYSPARK_SUBMIT_ARGS properly.

    Parameters
    ----------
    jars: list of path to jars in string format
    """

    # if the parameter is a string, convert to a single element list
    if isinstance(jars, str):
        jars = [jars]

    _add_to_submit_args("--jars " + ",".join(jars))



def export_conda_env_yaml_and_compute_md5(envName, forcePackage=False):
    """Export conda environment to YAML and compute its MD5 hash without saving to a file.

    Parameters
    ----------
    envName : str
        The name of the conda environment to export.

    Returns
    -------
    str
        Path to the created tar.gz file for the packed environment.
    """
    # 导出环境为YAML内容
    result = subprocess.run(
        ["conda", "env", "export", "-n", envName],
        capture_output=True,
        text=True,
        check=True
    )
    
    yaml_content = result.stdout
    
    # print(f"yaml_content: {yaml_content}")

    # 计算MD5值
    md5_hash = hashlib.md5(yaml_content.encode('utf-8')).hexdigest()
    
    # 创建文件名并定义存放路径
    file_name = f"{envName}_{md5_hash}.tar.gz"
    output_path = os.path.join("/tmp/env", file_name)
    
    # 强制打包
    if forcePackage:
        print(f"是否强制打包: {forcePackage}")
        old_files = glob(os.path.join("/tmp/env", f"{envName}_*.tar.gz"))
        for old_file in old_files:
            os.remove(old_file)
            print(f"Deleted old file: {old_file}")
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 使用 conda pack 打包环境
        subprocess.run(["conda", "pack", "-n", envName, "-o", output_path], check=True)
        
        print(f"Packed conda environment stored at: {output_path}")

        return output_path

    # 检查是否存在同名的gz包
    if os.path.exists(output_path):
        print(f"Using existing packed file: {output_path}")
        return output_path

    # 删除同一环境下的旧包
    old_files = glob(os.path.join("/tmp/env", f"{envName}_*.tar.gz"))
    for old_file in old_files:
        os.remove(old_file)
        print(f"Deleted old file: {old_file}")

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 使用 conda pack 打包环境
    subprocess.run(["conda", "pack", "-n", envName, "-o", output_path], check=True)
    
    print(f"Packed conda environment stored at: {output_path}")

    return output_path

def get_yarn_queue_name(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('yarnQueueName'):
                    # 分割字符串并获取值
                    return line.split('=')[1].strip().strip(',')
    except Exception:
        print(f"get queue error.")
        return None


