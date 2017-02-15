# -*- coding: utf-8 -*-

from gitlab import Gitlab
from django.conf import settings
from django import forms
from django.db.models.query_utils import Q
from datetime import datetime
from api import models
import os, platform, tarfile, platform, codecs, string, zipfile, shutil, ftplib, re, md5, filecmp, ghdiff, subprocess, stat


class ConfigurationHelper():
    
    git = None

    def __init__(self):
        # connect to gitlab with token
        try:
            self.git = Gitlab(settings.GITLAB_SERVER, settings.GITLAB_ACCOUNT_TOKEN)
        except:
            raise Exception(u'无法和Gitlab服务器建立连接')
    
    def _del_rw(self, action, name, exc):
        # REF:
        # http://stackoverflow.com/questions/21261132/python-shutil-rmtree-to-remove-readonly-files
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)

    def download_file(self, package):
        try:
            projects = self.git.getall(self.git.getprojects)
            project = [x for x in projects if x['namespace']['name'] == package.application.department_set.first().name if x['name'] == package.application.name]

            if not project:
                raise Exception(u'无法在Gitlab中找到项目，{0}'.format(name))

            # create temp folder
            if not os.path.exists(settings.PACKAGE_TEMP_PATH):
                os.mkdir(settings.PACKAGE_TEMP_PATH)

            # package.name = '{0}_{1}'.format(package.application.name, datetime.now().strftime('%Y%m%d%H%M%S'))
            package.name = package.name
            folder_path = os.path.join(settings.PACKAGE_TEMP_PATH, package.name)
        
            # Using git client to get files from different branch. git should be added ENVIRONMENT VARIABLES.
            repo_url = string.replace(project[0]['http_url_to_repo'], 'http://', 'http://{0}:{1}@'.format(settings.GITLAB_USERNAME, settings.GITLAB_PASSWORD))
            if package.branch_name:
                pipe = subprocess.Popen(['git', 'clone', '--depth=1', '-b', package.branch_name, repo_url, 
                                         '--single-branch', folder_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                pipe = subprocess.Popen(['git', 'clone', '--depth=1', repo_url, '--single-branch', folder_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = pipe.communicate()
            if pipe.returncode != 0:
                raise Exception(u'git clone 运行失败，通常由于分支名称不正确照成。')

            # remove .git folder, we will never push changes to gitlab from CMC.
            # meanwhile, .git folder should never be packaged.
            git_folder = os.path.join(folder_path, '.git')
            shutil.rmtree(git_folder, onerror=self._del_rw)
        except Exception as e:
            print(e)
            raise Exception(u'无法下载文件, ' + e.message)

    def parse_file(self, package):
        try:
            dirPath = os.path.join(settings.PACKAGE_TEMP_PATH, package.name)
            
            # If we don't find application tags for one application,
            # The configuration files should be also generated.
            applicationTags = models.ApplicationTag.objects.filter(application=package.application.id)
            if not applicationTags:
                return None
        
            # Must use application=application.id here! Please search 'django filter foreign key'
            tagValues = models.TagValue.objects.filter(environment=package.environment.id)
            if not tagValues:
                raise Exception(u'无法找到与环境适配的模板值')

            # iterate each application tags since we may have different template tags for each config file.        
            for applicationTag in applicationTags:
                relativePath = None
                content = None
                if package.target_platform.lower().startswith('windows'):
                    relativePath = applicationTag.file_path.strip('/').replace('/', '\\')
                else:
                    relativePath = applicationTag.file_path.strip('/')

                if not platform.platform().lower().startswith('windows'):
                    relativePath = relativePath.replace('\\', '/')
                    
                filePath = os.path.join(dirPath, relativePath)

                if not os.path.exists(filePath):
                    raise Exception(u'无法打开文件{0}! 请确认应用标签中的配置文件相对路径是否正确。（路径区分大小写）'.format(applicationTag.file_path))

                with codecs.open(filePath, mode='rb+', encoding='utf-8') as f:
                    content = f.read()

                    # search template tags in content, if we find one or more template tags are missing,
                    # then raise error.
                    for tag in applicationTag.tags.all():
                        position = string.find(content, tag.name)
                        if position == -1:
                            raise Exception(u'无法在配置文件中找到{0}! 请检查是否需要继续在配置文件中使用该模板标签。'.format(tag.name))

                    for tag in applicationTag.tags.all():
                        filters = Q(tag=tag, environment=package.environment)
                        tagName = tag.name
                        if not models.TagValue.objects.filter(filters).first():
                            raise Exception(u'无法找到和环境对应的模板标签值，请添加！ 模板标签为: {0}'.format(tagName))
                        tagValue = models.TagValue.objects.filter(filters).first().value
                        content = string.replace(content, tagName, tagValue)

                    # if we find one or more template tags after replacing 'all' template tags,
                    # then raise error.
                    if re.search(r'\$\{\w+\}\$', content):
                        raise Exception(u'在配置文件中找到未经替换的模板标签，请检查该应用的应用标签设置！')

                with codecs.open(filePath, mode='wb+', encoding='utf-8') as f:
                    f.write(content)

        except Exception as e:
            shutil.rmtree(dirPath)
            raise Exception(u'无法处理文件, ' + e.message)
    
    def package_file(self, package):
        try:
            dirPath = os.path.join(settings.PACKAGE_TEMP_PATH, package.name)
            zipFilePath = os.path.join(settings.PACKAGE_TEMP_PATH, ('{0}.zip'.format(package.name)))
            md5FilePath = os.path.join(settings.PACKAGE_TEMP_PATH, ('{0}.md5'.format(package.name)))

            # package files
            zip = zipfile.ZipFile(zipFilePath, 'w', zipfile.ZIP_DEFLATED)
            for dirname, subdirs, files in os.walk(dirPath):
                for filename in files:
                    absname = os.path.abspath(os.path.join(dirname, filename))
                    arcname = absname[len(dirPath) + 1:]
                    zip.write(absname, arcname)
            zip.close()

            # generate md5 checksum for zip file
            # http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
            m = md5.new()
            with open(zipFilePath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), ''):
                    m.update(chunk)
            with codecs.open(md5FilePath, mode='wb', encoding='utf-8') as f:
                f.write(m.hexdigest())

            # remove configuration folder
            shutil.rmtree(dirPath, True)
        except Exception as e:
            shutil.rmtree(dirPath, True)
            raise Exception(u'无法打包配置文件, ' + e.message)

    def upload_file(self, package):
        try:
            dirPath = os.path.join(settings.PACKAGE_TEMP_PATH, package.name)
            zipFilePath = os.path.join(settings.PACKAGE_TEMP_PATH, ('{0}.zip'.format(package.name)))
            md5FilePath = os.path.join(settings.PACKAGE_TEMP_PATH, ('{0}.md5'.format(package.name)))
            zipFileName = '{0}.zip'.format(package.name)
            md5FileName = '{0}.md5'.format(package.name)

            if package.environment.name == settings.PROD_ENV_NAME:
                ftp = ftplib.FTP(settings.FTP_PROD_SERVER)
                ftp.login(settings.FTP_PROD_USERNAME, settings.FTP_PROD_PASSWORD)
                ftpServerPrefix = 'ftp://{0}'.format(settings.FTP_PROD_SERVER)
            else:
                ftp = ftplib.FTP(settings.FTP_TEST_SERVER)
                ftp.login(settings.FTP_TEST_USERNAME, settings.FTP_TEST_PASSWORD)
                ftpServerPrefix = 'ftp://{0}'.format(settings.FTP_TEST_SERVER)

            dirPath = string.replace(package.output_path, ftpServerPrefix, '').strip('/')
            dirList = dirPath.split('/')

            # create directory if it does not exist.
            for dir in dirList:
                try:
                    ftp.cwd(dir)
                except:
                    ftp.mkd(dir)
                    ftp.cwd(dir)
        
            # upload files with time stamp
            ftp.storbinary('STOR {0}'.format(zipFileName), open(zipFilePath, 'rb'))
            ftp.storbinary('STOR {0}'.format(md5FileName), open(md5FilePath, 'rb'))

            # upload files by using latest as their names, thus we can retrieve them easily.
            ftp.storbinary('STOR latest.zip', open(zipFilePath, 'rb'))
            ftp.storbinary('STOR latest.md5', open(md5FilePath, 'rb'))

            os.remove(zipFilePath)
            os.remove(md5FilePath)

            ftp.close()
        except Exception as e:
            ftp.close()
            os.remove(zipFilePath)
            os.remove(md5FilePath)
            raise Exception(u'无法上传配置文件, ' + e.message)

class ComparisonHelper():

    # diff_files is a nested dictionary object that has following structure.
    # diff_files = {
    #   '/Web.config': { 'left':left_tempdir_path, 'right':right_tempdir_path },
    #   '/Config/ConnectionStrings.config': { 'left':left_tempdir_path, 'right':right_tempdir_path }
    # }
    # dict key: relative path of a configuration file path
    # value: a dictionary object that contains the left and right directory path.
    diff_files = {}

    def download_file(self, instance):

        # Get package instance by name.
        package = models.Package.objects.get(name=instance.name)

        # Download packages from FTP, then extract them.
        try:
            # Connect to different ftp based on environment
            if package.environment.name == settings.PROD_ENV_NAME:
                ftp = ftplib.FTP(settings.FTP_PROD_SERVER)
                ftp.login(settings.FTP_PROD_USERNAME, settings.FTP_PROD_PASSWORD)
                ftpServerPrefix = 'ftp://{0}'.format(settings.FTP_PROD_SERVER)
            else:
                ftp = ftplib.FTP(settings.FTP_TEST_SERVER)
                ftp.login(settings.FTP_TEST_USERNAME, settings.FTP_TEST_PASSWORD)
                ftpServerPrefix = 'ftp://{0}'.format(settings.FTP_TEST_SERVER)

            # Change ftp dir based on package.output_path
            dirpath = package.output_path.replace(ftpServerPrefix, '').strip('/')
            ftpdirs = dirpath.split('/')
            for ftpDir in ftpdirs:
                ftp.cwd(ftpDir)

            localFilePath = os.path.join(settings.PACKAGE_TEMP_PATH, ('{0}.zip'.format(package.name)))
            remoteFileName = '{0}.zip'.format(package.name)
            ftp.retrbinary('RETR {0}'.format(remoteFileName), open(localFilePath, 'wb').write, 1024)
            ftp.close()
        except:
            raise Exception(u'无法下载文件！')

    def extract_file(self, instance):
        try:
            # extract file
            zfilepath = os.path.join(settings.PACKAGE_TEMP_PATH, ('{0}.zip'.format(instance.name)))
            targetdir = os.path.join(settings.PACKAGE_TEMP_PATH, instance.name)
            zfile = zipfile.ZipFile(zfilepath)
            zfile.extractall(targetdir)
        except:
            raise Exception(u'无法解压文件！')
    
    def __get_diff_file(self, cmpresult):
        for diff_file in cmpresult.diff_files:
            self.diff_files.update({diff_file: {'left':cmpresult.left, 'right':cmpresult.right}})
        for subdir in cmpresult.subdirs.itervalues():
            self.__get_diff_file(subdir)

    def compare_file(self, left, right):
        try:
            # compare files
            left_dir = os.path.join(settings.PACKAGE_TEMP_PATH, left.name)
            right_dir = os.path.join(settings.PACKAGE_TEMP_PATH, right.name)

            cmpresult = filecmp.dircmp(left_dir, right_dir)
            self.diff_files = {}
            self.__get_diff_file(cmpresult)

            diff_results = {}
            for filename, path in self.diff_files.items():
                left_file_path = os.path.join(path['left'], filename)
                right_file_path = os.path.join(path['right'], filename)

                with codecs.open(left_file_path, mode='rb', encoding='utf-8') as f:
                    left_file_content = f.read()

                with codecs.open(right_file_path, mode='rb', encoding='utf-8') as f:
                    right_file_content = f.read()

                diff_result = ghdiff.diff(left_file_content, right_file_content, n=0, css=False)
                relative_path = left_file_path.replace(left_dir, '').replace('\\', '/')
                diff_results[relative_path] = diff_result

            return diff_results
        except Exception as e:
            raise Exception(u'配置文件包比较失败, {0}'.format(e.message))

    def clean_up(self, instance):
        try:
            # extract file
            zfilepath = os.path.join(settings.PACKAGE_TEMP_PATH, ('{0}.zip'.format(instance.name)))
            targetdir = os.path.join(settings.PACKAGE_TEMP_PATH, instance.name)
            os.remove(zfilepath)
            shutil.rmtree(targetdir)

        except Exception as e:
            raise Exception(u'无法删除临时文件, {0}'.format(e.message))

    def file_exists(self, instance):
        package = models.Package.objects.get(name=instance)

        # Connect to different ftp based on environment
        if package.environment.name == settings.PROD_ENV_NAME:
            ftp = ftplib.FTP(settings.FTP_PROD_SERVER)
            ftp.login(settings.FTP_PROD_USERNAME, settings.FTP_PROD_PASSWORD)
            ftpServerPrefix = 'ftp://{0}'.format(settings.FTP_PROD_SERVER)
        else:
            ftp = ftplib.FTP(settings.FTP_TEST_SERVER)
            ftp.login(settings.FTP_TEST_USERNAME, settings.FTP_TEST_PASSWORD)
            ftpServerPrefix = 'ftp://{0}'.format(settings.FTP_TEST_SERVER)

        try:
            # Change ftp dir based on package.output_path
            dirPath = package.output_path.replace(ftpServerPrefix, '').strip('/')
            ftpDirs = dirPath.split('/')
            for ftpDir in ftpDirs:
                ftp.cwd(ftpDir)

            files = ftp.nlst()
            ftp.close()

            # Check file existence
            fileName = '{0}.zip'.format(instance.name)
            if fileName in files:
                return True
            else:
                return False
        except:
            ftp.close()
            return False
