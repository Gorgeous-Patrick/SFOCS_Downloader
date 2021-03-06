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
    page=1
    res=[]
    
    while 1:
        newres=[]
        r=sess.get("https://focs.ji.sjtu.edu.cn/git/api/v1/orgs/"+org+"/repos?page="+str(page)+"&limit=10000").json()
        for repos in r:
            newres.append(repos["name"])
        res=res+newres
        if newres==[]:
            break
        page=page+1
    
    return res
def p1repos(name):
    return name.startswith("p1")

def p2repo(name):
    return name.startswith("p2")

def individualRepo(name):
    return "520" in name
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

def AllinOne(sel, sess):
    undone=[]
    print("Working")
    allrepo=allRepos(sess)
    requiredRepos=list(filter(sel, allrepo))
    print("Found %s Repos, %s of them are desired"%(allrepo.__len__(), requiredRepos.__len__()))
    for repoName in requiredRepos:
        done=downloadRepo(sess, repoName)
        if (not done) and (repoName!="management"):
            undone.append(repoName)
    return undone
giteaSess = createSess(params={"access_token": GITTOKEN})


print("Fetch : 1) Individual Repos 2) P1 Repos 3) P2 Repos (Input Number):")
choice = int(input())

if choice==1:
    filterFunc=individualRepo
elif choice==2:
    filterFunc=p1repos
elif choice==3:
    filterFunc=p2repo
else:
    print("ERROR")
    exit
print("Those who hasn't released anything: %s" %AllinOne(filterFunc,giteaSess))
# download(giteaSess, "https://focs.ji.sjtu.edu.cn/git/attachments/90192a3d-52dd-4fe5-80fa-026fa8a3253b", "try/h.tar.txt")
# r=giteaSess.get("https://focs.ji.sjtu.edu.cn/git/api/v1/repos/SilverFOCS-21/Git_Workshop_Demo/releases/52/assets")
