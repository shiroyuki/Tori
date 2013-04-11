import os
import re
import subprocess
from time import sleep
 
class File(object):
    def __init__(self, path):
        self.path        = path
        self.last_update = None
        self.existed     = True
 
    def updated(self):
        if self.existed and not os.path.exists(self.path):
            self.existed = False
 
            return True
        if not self.existed:
            return False
 
        fs_stat = os.stat(self.path)
 
        current_last_update = fs_stat.st_mtime
 
        if not self.last_update:
            self.last_update = current_last_update
 
            return False
        elif self.last_update == current_last_update:
            return False
 
        self.last_update = current_last_update
 
        return True
 
class FileSystemManager(object):
    def __init__(self, callback, *paths, **options):
        self.paths     = paths
        self.fileMap   = {}
        self.activated = True
        self.callback  = callback
 
    def update(self):
        for path in self.paths:
            local_updates = self.local_updates(path)
 
            if not local_updates:
                continue
 
            self.callback(local_updates)
 
    def local_updates(self, path):
        local_paths   = os.listdir(path)
        local_updates = []
 
        for local_path in local_paths:
            rel_path = os.path.join(path, local_path)
 
            if local_path[0] == '.' or re.search('\.pyc$', local_path):
                continue
 
            if os.path.isdir(rel_path):
                local_updates.extend(self.local_updates(rel_path))
                continue
 
            if rel_path not in self.fileMap:
                self.fileMap[rel_path] = File(rel_path)
 
                local_updates.append(rel_path)
 
                print('ADDED: {}'.format(rel_path))
 
            elif self.fileMap[rel_path].updated():
 
                print('UPDATED: {}'.format(rel_path))
 
                local_updates.append(rel_path)
 
        return local_updates
 
def recompile(update_files):
    print('Updating...')
    #subprocess.call(['make', 'clean'])
    subprocess.call(['make', 'html'])
    print('Updated')
 
book_manager = FileSystemManager(recompile, 'source', '../tori')
 
print('Monitoring changes...')
 
while book_manager.activated:
    try:
        sleep(1)
        book_manager.update()
    except KeyboardInterrupt:
        print('\rDeactivated')
        book_manager.activated  = False
 
print('The manager has just signed off.')