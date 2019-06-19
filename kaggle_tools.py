import subprocess
import webbrowser
import time
from pathlib import Path
import os
import json
import numpy as np
import pandas as pd
from io import StringIO
import shutil

# replace this by your username:
USER = 'YourUserName'

class Trainer:
    def __init__(self,kernels):
        self.kernels = kernels
        self.name = USER
        self.check_status_interval = 60*5
        self.is_running = []
        self.projects_directory = Path.home() / 'kaggle-projects'
        self.data_template = {
            "title": "INSERT_TITLE_HERE",
            "id": "username/INSERT_SLUG_HERE",
            "licenses": [
                {
                "name": "CC0-1.0"
                }
            ]
        }
        self.meta_template = {
            "id": "karlpoppery/INSERT_KERNEL_SLUG_HERE",
            "title": "INSERT_TITLE_HERE",
            "code_file": "INSERT_CODE_FILE_PATH_HERE",
            "language": "python",
            "kernel_type": "script",
            "is_private": "true",
            "enable_gpu": "true",
            "enable_internet": "false",
            "dataset_sources": [],
            "competition_sources": [],
            "kernel_sources": []
        }
        self.compatible_datasets_extentions = ['csv','json','sql']
    
    def check_status(self):
        latest = (subprocess.check_output('kaggle kernels list -m --sort-by dateRun --csv'.split(' ')).decode())
        latest = pd.read_csv(StringIO(latest))
        self.is_running = []
        for kernel in latest[:4]['ref']:
            try:
                status = str(subprocess.check_output('kaggle kernels status {}'.format(kernel).split(' ')))
            except subprocess.CalledProcessError:
                pass
            if status.split('"')[1] == 'running':
                self.is_running.append(kernel)
            elif status.split('"')[1] in ['complete','error']:
                pass
            else:
                print('Unexpected API message')
                print("Status for {} : {}".format(kernel, status))

    def alarm(self):
        self.check_status()
        tracking = self.is_running
        start_time = time.time()
        if not tracking:
            print('No kernels are currently training')
            return 0
        print('alarm set')
        while True:
            print('Time: {:.2f}'.format(time.time() - start_time))
            for kernel in tracking:
                if kernel in self.is_running:
                    print('{} is training'.format(kernel))
                else:
                    print(('{}: Commit done!').format(kernel))
                    webbrowser.open('https://www.kaggle.com/' + kernel)
                    # Video alert. Change to the page of your choice:
                    webbrowser.open('https://www.youtube.com/watch?v=aJq6ygTWdao&list=UUbfYPyITQ-7l4upoX8nvctg')
                    tracking.remove(kernel)
            for kernel in self.is_running:
                if not kernel in tracking:
                    tracking.append(kernel)
                    print('{} has started running'.format(kernel))
            if not tracking:
                break
            time.sleep(self.check_status_interval)
            self.check_status()
    
    def pull(self, kernels = ['']):
        if not self.projects_directory.exists():
            self.projects_directory.mkdir()
        if not kernels:
                kernels = self.kernels
        for kernel in kernels:
            project_path = self.projects_directory / kernel
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
            out = str(subprocess.check_output('kaggle kernels pull -p {} -m {}'.format(
                project_path, kernel).split(' ')))
            print(out)
        return kernels

    def push(self, kernels = ['']):
        if not kernels:
            kernels = self.kernels
        for kernel in kernels:
            project_path = self.projects_directory / kernel
            self.check_status()
            if len(self.is_running) < 4:
                out = str(subprocess.check_output('kaggle kernels push -p {}'.format(project_path).split(' ')))
                print(out)
            else:
                print('Already 4 kernels commited: {}\n{} is next in queue'.format(str(self.is_running),kernel))
                time.sleep(self.check_status_interval)
                push([kernel])
        return kernels

    def copy(self, kernel, amount):
        kernel = self.projects_directory / kernel
        assert kernel.is_dir()
        paths = []
        with open(kernel / 'kernel-metadata.json') as r:
            metadata = json.load(r)
        for i in range(amount):
            copy_path = kernel.parent / (kernel.name + 'CPV' + str(i))
            paths.append(copy_path)
        for path in paths:
            shutil.copytree(kernel,path)
            metadata['id'] = str(path)
            metadata['title'] = str(path.name)
            with (path / 'kernel-metadata.json').open('w') as w:
                w.write(json.dumps(metadata))
        return [kernel] + paths

    def rename(self,kernels,new):
        for i in range(len(kernels)):
            os.rename(self.projects_directory / kernels[i], self.projects_directory / new[i])
        with open(self.projects_directory  / new[i] / 'kernel-metadata.json') as r:
            metadata = json.load(r)
        metadata['id'] = str(new[i])
        metadata['title'] = str(Path(new[i]).name)
        with open(self.projects_directory  / new[i] / 'kernel-metadata.json','w') as w:
            w.write(json.dumps(metadata))
        return new

    def modify(self, kernels, mod_dict):
        '''TO DO'''
        return kernels

    def create_kernel(self, path):
        # TO DO
        new = self.projects_directory / path
        new.mkdir()
        out = str(subprocess.check_output('kaggle kernels init -p {}'.format(new).split(' ')))
        print(out)

    def create_dataset(self,path):
        dataset_path = self.projects_directory / path
        meta = self.data_template
        meta['title'] = Path(path).name
        meta['id'] = path
        with open(dataset_path / 'dataset-metadata.json', 'w') as f:
            f.write(json.dumps(meta))
        out = str(subprocess.check_output('kaggle datasets create -p {}'.format(
            dataset_path).split(' ')))
        print(out)
    def push_dataset(self,datasets):
        '''TO DO'''
        pass
        
    def output_to_dataset(self,kernels):
        '''TO DO'''
        for kernel in kernels:
            pass

