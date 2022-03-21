import os
import shutil
import requests
from bs4 import BeautifulSoup
import threading

LOGIN_TEXT = 'Web Login Service - Loading Session Information'
DIR_TYPE = '[DIR]'
TXT_TYPE = '[TXT]'
FILE_TYPE = '[   ]'

class Downloader:
    def __init__(self, cookie: str, url: str) -> None:
        """Creates a new StudRes downloader.

        Args:
            url (str): The URL of the desired StudRes resource.
            cookie (str): The value of your 'MOD_AUTH_CAS_S' session cookie.
        """

        self.session = requests.Session()
        self.session.cookies.set('MOD_AUTH_CAS_S', cookie)
        self.base_url = url
        self.folder_name = url.rstrip('/').rsplit('/', 1)[-1]
        self.authed = False
        self.threads = []
        self.file_count = 0
        self.folder_count = 0

    def download(self) -> None:
        """Downloads the desired resource from StudRes.
        """

        base_path = f'output/{self.folder_name}'
        if os.path.isdir(base_path):
            shutil.rmtree(base_path)
        os.mkdir(base_path)

        self._download_directory(self.base_url, base_path)

        for thread in self.threads:
            thread.join()
        print(f'Downloaded {self.folder_count} directories, {self.file_count} files, wrote to {base_path}')

    def _download_directory(self, url: str, path: str) -> None:
        """Downloads a directory and its contents (files and subfolders).

        Args:
            url (str): The url of the directory.
            path (str): The path to the current output directory.
        """
        if not os.path.isdir(path):
            os.mkdir(path)

        res = self._get_resource(url)

        if not self.authed:
            if LOGIN_TEXT in res.text:
                print('LOGIN ERROR: Invalid or expired session cookie')
                exit()
            else:
                self.authed = True

        print(f'Downloading directory {path}')
        self.folder_count += 1

        page = BeautifulSoup(res.text, 'html.parser')
        rows = page.find_all('tr')
        for row in rows:
            img = row.find('img')
            if not img or not img.has_attr('alt'):
                continue
            resource_type = img['alt']

            link = row.find('a')
            if not link or not link.has_attr('href'):
                continue
            href = link['href']

            if resource_type == DIR_TYPE:
                dir_url = f'{url.rstrip("/")}/{href}'
                dir_path = f'{path}/{href.rstrip("/")}'
                thread = threading.Thread(target=self._download_directory, args=[dir_url, dir_path])
                self.threads.append(thread)
                thread.start()
            elif resource_type == TXT_TYPE or resource_type == FILE_TYPE:
                file_res = self._get_resource(url + href)
                open(f'{path}/{href}', 'wb').write(file_res.content)
                self.file_count += 1

    def _get_resource(self, url: str) -> requests.Response:
        """Downloads the content of a single resource (file or directory).

        Args:
            url (str): The URL of the resource.

        Returns:
            requests.Response: The response from the resource.
        """

        return self.session.get(url)

