from setuptools import setup, find_packages

from print_pro import __version__ as version

# NOTE: Do NOT add frappe/erpnext here.
# uv (used by newer bench) cannot resolve their git-URL sub-dependencies.
# Frappe-level app dependencies are declared in hooks.py → required_apps.
setup(
    name="print_pro",
    version=version,
    description="Print Pro - Advanced Printing Solution for ERPNext v15",
    author="Print Pro",
    author_email="support@printpro.io",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
)
