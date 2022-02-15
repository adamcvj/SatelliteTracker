#!"C:\Users\adzs3\OneDrive\Documents\Computer Science\Coursework\Client\venv\Scripts\pythonw.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'mayavi==4.7.1','gui_scripts','mayavi2'
__requires__ = 'mayavi==4.7.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('mayavi==4.7.1', 'gui_scripts', 'mayavi2')()
    )
