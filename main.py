from tokenconfig import GITTOKEN
# Create this file yurself and write :
# GITTOKEN="Your token"
base_url="https://focs.ji.sjtu.edu.cn/git/api/v1/repos/"
org="SilverFOCS-21"
base_path="Downloads"
import requests
import os
import shutil
import subprocess

def allRepos(sess):
    r=sess.get("https://focs.ji.sjtu.edu.cn/git/api/v1/orgs/"+org+"/repos?limit=10000").json()
    res=[]
    for repos in r:
        res.append(repos["name"])
    return res

def createSess(params):
    s = requests.Session()
    s.params.update(params)
    return s

def getRelID(sess, repoName):
    r=sess.get(base_url+org+"/"+repoName+"/releases").json()
    res=[]
    # print(r)

    for rel in r:
        # res.append((rel["tag_name"],rel["id"], rel["assets"]))
        assetlst=[]
        for asset in rel["assets"]:
            assetlst.append({
                "name": asset["name"],
                "url":asset["browser_download_url"]
            })
        res.append(
            {
                "name": repoName,
                "author":rel["author"]["full_name"],
                "submission": rel["name"],
                "tag_name": rel["tag_name"],
                "file_name": rel["tag_name"]+".tar.gz",
                "release_ID": rel["id"],
                "assets": assetlst
            }
        )
    return res
# def getAssetID(sess, org, repoName, relID):
#     r=sess.get(base_url+org+"/"+repoName+"/releases/"+str(relID)+"/assets").json()
def code_url(repoName, fileName):
    return base_url+org+"/"+repoName+"/"+"archive/"+fileName
def download(sess,url, path):
    file=sess.get(url, allow_redirects=True)

    # print("Download: %s"%url)
    open(path,'wb').write(file.content)
    return file.status_code

def makedir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

def preDownload(release):
    dir=os.path.join(base_path,release["author"])
    makedir(dir)
    dir=os.path.join(base_path,release["author"],release['submission'])
    makedir(dir)
    unzip_dir=os.path.join(dir, release['tag_name'])
    makedir(unzip_dir)
    dir=os.path.join(base_path,release["author"],release['submission'],"assets")
    makedir(dir)

def downloadCode(sess, release):
    dir=os.path.join(base_path,release["author"],release['submission'])
    path=os.path.join(dir, release['file_name'])
    unzip_dir=os.path.join(dir, release['tag_name'])
    download(sess, code_url(release['name'], release['file_name']),path)
    devNull = open(os.devnull, 'w')
    subprocess.run("tar -zxvf \""+path+"\" -C \""+unzip_dir+"\"", shell=True, stdout=devNull)
    
def downloadAsset(sess, release):
    # print(release)
    dir=os.path.join(base_path,release["author"],release['submission'],"assets")
    for asset in release['assets']:
        path=os.path.join(dir, asset['name'])
        download(sess, asset['url'], path)
def downloadRelease(sess, release):
    preDownload(release)
    downloadCode(sess,release)
    downloadAsset(sess, release)

def downloadRepo(sess,repoName):
    rels=getRelID(sess, repoName)
    if rels==[]:
        return False
    for rel in rels:
        downloadRelease(sess, rel)
    return True

def AllinOne(sess):
    undone=[]
    for repoName in allRepos(sess):
        done=downloadRepo(sess, repoName)
        if (not done) and (repoName!="management"):
            undone.append(repoName)
    return undone
giteaSess = createSess(params={"access_token": GITTOKEN})

print("Those who hasn't released anything: %s" %AllinOne(giteaSess))
print("Total Repo Number: %s" % allRepos(giteaSess).__len__())
# download(giteaSess, "https://focs.ji.sjtu.edu.cn/git/attachments/90192a3d-52dd-4fe5-80fa-026fa8a3253b", "try/h.tar.txt")
# r=giteaSess.get("https://focs.ji.sjtu.edu.cn/git/api/v1/repos/SilverFOCS-21/Git_Workshop_Demo/releases/52/assets")
