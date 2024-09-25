import os
import subprocess
import hashlib
import glob

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
    
    print(f"yaml_content: {yaml_content}")

    # 计算MD5值
    md5_hash = hashlib.md5(yaml_content.encode('utf-8')).hexdigest()
    
    # 创建文件名并定义存放路径
    file_name = f"{envName}_{md5_hash}.tar.gz"
    output_path = os.path.join("/tmp/env", file_name)
    
    # 强制打包
    if forcePackage:
        print(f"是否强制打包: {forcePackage}")
        old_files = glob.glob(os.path.join("/tmp/env", f"{envName}_*.tar.gz"))
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
    old_files = glob.glob(os.path.join("/tmp/env", f"{envName}_*.tar.gz"))
    for old_file in old_files:
        os.remove(old_file)
        print(f"Deleted old file: {old_file}")

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 使用 conda pack 打包环境
    subprocess.run(["conda", "pack", "-n", envName, "-o", output_path], check=True)
    
    print(f"Packed conda environment stored at: {output_path}")

    return output_path

# 示例用法
env_name = "a"  # 替换为你的环境名
packed_file_path = export_conda_env_yaml_and_compute_md5(env_name, True)
print(f"Packed conda environment stored at: {packed_file_path}")
