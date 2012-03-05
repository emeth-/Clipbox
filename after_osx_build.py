import os

def check_if_exists(before):
    for line in before.split('\n'):
        if '<LSUIElement>' in line:
            return True
    return False

os.system('mkdir dist/clipbox.app/Contents/Resources/temp/')
os.system('mkdir dist/clipbox.app/Contents/Resources/images/')
os.system('cp -rf copy_to_app/images/ dist/clipbox.app/Contents/Resources/images/')

x = open('dist/clipbox.app/Contents/Info.plist', 'r')
before = x.read()
x.close()

#add flag to hide icon from dock
if not check_if_exists(before):
    beforeByLine = before.split('\n')
    after = []
    inserted = 0
    for line in beforeByLine:
        if inserted == 0 and '<key>' in line:
            after.append('	<key>LSUIElement</key>')
            after.append('	<string>1</string>')
            inserted = 1
        after.append(line)
        
    x = open('dist/clipbox.app/Contents/Info.plist', 'w')
    x.write('\n'.join(after))
    x.close()

print "Changes made to .app file."