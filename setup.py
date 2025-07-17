from setuptools import setup, find_packages

setup(
    name="cctv-supabase-sync",
    version="1.0.0",
    description="CCTV Google Sheets to Supabase AI 동기화 시스템",
    author="Shin Ja-dong",
    author_email="tlswk@example.com",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client==2.110.0",
        "google-auth==2.24.0",
        "google-auth-oauthlib==1.1.0",
        "google-auth-httplib2==0.2.0",
        "pandas==2.1.4",
        "openpyxl==3.1.2",
        "supabase==2.9.1",
        "schedule==1.2.0",
        "python-dotenv==1.0.0",
        "anthropic==0.25.0",
        "requests==2.31.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "cctv-sync=cctv_supabase_sync:main",
        ],
    },
) 