'''
 *  Copyright (c) 2011
 *  http://teachthe.net/?page_id=1657
 *  Originally developed by Sean Kooyman | teachthe.net(at)gmail.com
 *
 *  License:  GPL version 3.
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.

 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 *  THE SOFTWARE.
'''
import json
import shutil #to move files between locations
import os

import random, string, time

import hashlib

def hash_it(input):
    md5 = hashlib.md5()
    md5.update('Royale.'+input)
    return md5.hexdigest()

def delete_paste(pasteID, db_path):
    try:
        os.remove(db_path+pasteID)
        return 1
    except:
        return 0

def delete_all_pastes(db_path, dbfile):
    #read database
    try:
        pasteListF = open(db_path+'.'+hash_it(dbfile), 'r')
        pasteListS = pasteListF.read()[8:-2]
        pasteListF.close()
        pasteList = json.loads(pasteListS)
    except:
        print "unable to open ."+hash_it(dbfile)
        return 0

    for p in pasteList:
        #delete paste files
        try:
            os.remove(db_path+p['id'])
        except:
            pass

    #clear database
    try:
        pasteListF = open(db_path+'.'+hash_it(dbfile), 'w')
        pasteListF.write('clipbox([]);')
        pasteListF.close()
    except:
        print "unable to write to ."+hash_it(dbfile)

def add_paste_to_db(ptype, meta, pasteID, db_path, dbfile):
    try:
        pasteListF = open(db_path+'.'+hash_it(dbfile), 'r')
        pasteListS = pasteListF.read()[8:-2]
        pasteListF.close()

        pasteList = json.loads(pasteListS)
    except:
        print "unable to open ."+hash_it(dbfile)
        pasteList = []

    pasteList.append({"type":ptype, "meta":meta, "id":pasteID, "time":int(time.time())})

    try:
        pasteListF = open(db_path+'.'+hash_it(dbfile), 'w')
        pasteListF.write('clipbox('+json.dumps(pasteList)+');')
        pasteListF.close()
    except:
        print "unable to write to ."+hash_it(dbfile)

    return 1

def deletePasteObject(pasteID, db_path, dbfile):
    try:
        remove_paste_from_db(pasteID, db_path, dbfile)
        delete_paste(pasteID, db_path)
        return 1
    except:
        return 0

def retrievePasteObject(pasteID, db_path, dbfile):
    try:
        pdata = open(db_path+pasteID, 'rb')
        data = pdata.read()
        pdata.close()
        remove_paste_from_db(pasteID, db_path, dbfile)
        return data
    except:
        return 0


def remove_paste_from_db(pasteID, db_path, dbfile):
    try:
        pasteListF = open(db_path+'.'+hash_it(dbfile), 'r')
        pasteListS = pasteListF.read()[8:-2]
        pasteListF.close()
        pasteList = json.loads(pasteListS)
    except:
        print "unable to open ."+hash_it(dbfile)
        return 0

    for p in pasteList:
        if p['id'] == pasteID:
            pasteList.remove(p)

    try:
        pasteListF = open(db_path+'.'+hash_it(dbfile), 'w')
        pasteListF.write('clipbox('+json.dumps(pasteList)+');')
        pasteListF.close()
    except:
        print "unable to write to ."+hash_it(dbfile)

    return 1

def getPasteList(db_path, dbfile):
    try:
        pasteListF = open(db_path+'.'+hash_it(dbfile), 'r')
        pasteListS = pasteListF.read()[8:-2]
        pasteListF.close()

        pasteList = json.loads(pasteListS)
        return pasteList
    except:
        #print "Unable to load ."+hash_it(dbfile)
        return []