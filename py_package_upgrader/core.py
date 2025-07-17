import subprocess
import re
import requests
import logging
import os

class PyPackageUpgrader:
    def __init__(self, requirements_txt='requirements.txt', project_path='.',only=None,exclude=None,dry_run=False,clean_only=False):
        self.requirements_file =  requirements_txt
        self.project_path = project_path
        self.only = only
        self.exclude = exclude
        self.dry_run = dry_run
        self.clean_only = clean_only
        self.package_name = 'py-package-upgrader'
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_current_version(self,package=None):
        self.package_name = package if package else self.package_name
        try:
            result = subprocess.run(
                [self.package_name, '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            self.logger.info(f"Current version of {self.package_name}: {version}")
            return version
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error getting current version: {e.stderr.strip()}")
            return None

    def get_latest_version(self,package=None):
        self.package_name = package if package else self.package_name
        try:
            response = requests.get(f'https://pypi.org/pypi/{self.package_name}/json')
            response.raise_for_status()
            data = response.json()
            latest_version = data['info']['version']
            self.logger.info(f"Latest version of {self.package_name}: {latest_version}")
            return latest_version
        except requests.RequestException as e:
            self.logger.error(f"Error fetching latest version: {e}")
            return None

    def upgrade_package(self,package=None):
        self.package_name = package if package else self.package_name
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()

        if not current_version or not latest_version:
            return

        if current_version == latest_version:
            self.logger.info(f"{self.package_name} is already up to date.")
            return

        try:
            subprocess.run(
                [f'pip install --upgrade {self.package_name}'],
                shell=True,
                check=True
            )
            self.logger.info(f"{self.package_name} upgraded to version {latest_version}.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error upgrading package: {e.stderr.strip()}")

    def clean_requirements(self,package=None):
        self.package_name = package if package else self.package_name
        try:
            subprocess.run(
                ['pip-autoremove', self.package_name, '-y'],
                check=True
            )
            self.logger.info(f"Cleaned up unused packages related to {self.package_name}.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error cleaning requirements: {e.stderr.strip()}")

    def check_installed_packages(self, project_path):
        try:
            temp_file = 'installed_packages.txt'
            subprocess.run([
                'pipreqs',
                project_path,
                '--savepath', temp_file,
                '--force'
            ], check=True)
            installed_packages = []
            with open(temp_file, 'r') as file:
                for line in file:
                    if line.strip() and not line.startswith('#'):
                        package = line.strip().split('==')[0]
                        installed_packages.append(package)
            self.logger.info(f"Installed packages in {project_path}: {installed_packages}")
            return installed_packages
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error checking installed packages: {e.stderr.strip()}")
            return []
        finally:
            try:
                subprocess.run(['rm', temp_file], check=True)
            except Exception as e:
                self.logger.warning(f"Error removing temporary file: {e}")
    

    def dry_run_upgrade(self, package=None):
        self.package_name = package if package else self.package_name
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()

        if not current_version or not latest_version:
            return

        if current_version == latest_version:
            self.logger.info(f"{self.package_name} is already up to date.")
            return

        self.logger.info(f"Dry run: {self.package_name} would be upgraded from {current_version} to {latest_version}.") 
    

    def check_requirements(self, requirements_file, installed_packages= None):
        packages = []
        if installed_packages is None:
            installed_packages = self.check_installed_packages('.')
        try:
            with open(requirements_file, 'r') as file:
                requirements = file.readlines()
            for line in requirements:
                package = line.strip().split('==')[0]
                if installed_packages and package not in installed_packages:
                    self.logger.warning(f"Package {package} in requirements not installed.")
                    self.clean_requirements(package)
                else:
                    self.logger.info(f"Package {package} is in requirements.")
                if self.get_latest_version() != self.get_current_version():
                    self.logger.info(f"Package {package} is not up to date.")
                    packages.append(package)
                else:
                    self.logger.info(f"Package {package} is up to date.")
            return packages
        except FileNotFoundError:
            self.logger.error(f"Requirements file {requirements_file} not found.")
        except Exception as e:
            self.logger.error(f"Error checking requirements: {e}")

    def check_requirements_in_project(self, project_path):
        requirements_file = f"{project_path}/requirements.txt"
        if not os.path.exists(requirements_file):
            self.logger.error(f"Requirements file {requirements_file} does not exist.")
            return []
        return self.check_requirements(requirements_file)
        
    def main(self):
        try:
            packages = self.check_installed_packages(self.project_path)
            if self.only:
                used_packages = [pkg for pkg in packages if pkg in self.only]
            elif self.exclude:
                used_packages = [pkg for pkg in packages if pkg not in self.exclude]
            else:
                used_packages = packages
            self.logger.info(f"Used packages: {used_packages}")
            if self.dry_run:
                for package in used_packages:
                    if package == self.package_name:
                        continue
                    self.logger.info(f"Dry run for package: {package}")
                    self.dry_run_upgrade(package)
        
            if not self.clean_only:
                for package in used_packages:
                    if package == self.package_name:
                        continue
                    self.logger.info(f"Checking package: {package}")
                    if self.get_latest_version(package) != self.get_current_version(package):
                        self.logger.info(f"Upgrading package: {package}")
                        self.upgrade_package(package)
                    else:
                        self.logger.info(f"Package {package} is already up to date.")
            else:
                self.check_requirements(self.requirements_file)
            # Fetch latest versions and create a new requirements.txt
            new_requirements = []
            for package in used_packages:
                latest_version = self.get_latest_version(package)
                if latest_version:
                    new_requirements.append(f"{package}=={latest_version}\n")
                else:
                    new_requirements.append(f"{package}\n")
            new_requirements_file = os.path.join(self.project_path, 'requirements.new.txt')
            with open(new_requirements_file, 'w') as f:
                f.writelines(new_requirements)
            self.logger.info(f"New requirements file created at {new_requirements_file}")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None
