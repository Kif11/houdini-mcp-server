from setuptools import setup, find_packages

setup(
    name="houdini-mcp-server",
    version="0.1.0",
    description="MCP Server for Houdini integration with OpenCode",
    author="",
    python_requires=">=3.9",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    install_requires=[
        "mcp>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "houdini-mcp-server=houdini_mcp_server:main",
        ],
    },
)
