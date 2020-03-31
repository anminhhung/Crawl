import sys
import getopt
from anytree import Node, RenderTree, LevelOrderIter, DoubleStyle
from anytree.dotexport import RenderTreeGraph
import requests
from bs4 import BeautifulSoup
import download_images as download_images
import cv2
import os
import shutil

'''
Scrapes a url and finds all of its outgoing links, the links
are then created as Nodes that are children of the original node.
'''
def scrapeUrl(url, rootNode):
    download_images.crawling(url)
    response = requests.get(url)
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    
    list_of_nodes = []
    for link in soup.find_all('a', href=True):
        href = link.get('href')  # unicode to str
        if (href.startswith('/')):
            href = url + href
            print("href: ", href)
            download_images.crawling(href)
        elif (href.startswith('http')):
            urlNode = Node(href, parent=rootNode)
            _urlNode = urlNode
            _urlNode = str(_urlNode)
            _urlNode = (_urlNode.split("/", 1)[-1]).split("'")[0]
            download_images.crawling(_urlNode)
            list_of_nodes.append(urlNode)
    return list_of_nodes

'''
Depth Limited Search from a root node.
'''
def depth_limited_search(rootNode, limit=50):
    def recursive_dls(rootNode, limit):
        children = scrapeUrl(rootNode.name, rootNode)

        if limit == 0:
            return 'cutoff'
        else:
            cutoff_occurred = False
            for child in children:
                result = recursive_dls(child, limit - 1)
                if result == 'cutoff':
                    cutoff_occurred = True
                elif result is not None:
                    return result
            return 'cutoff' if cutoff_occurred else None

    # Body of depth_limited_search:
    return recursive_dls(rootNode, limit)


def iterative_deepening_search(rootNode, maxDepth):
    for depth in range(maxDepth):
        result = depth_limited_search(rootNode, depth)
        if result != 'cutoff':
            return result


def crawling(inputUrl, inputDepth):
   rootNode = Node(inputUrl)

   iterative_deepening_search(rootNode, inputDepth)

def convert_jpg(start="crawl_dir", des="download"):
    print("[INFO] convert png->jpg")
    if not os.path.exists(des):
        os.umask(0)
        os.makedirs(des, mode=0o777)

    for dir in os.listdir(start):
        start_dir = os.path.join(start, dir)
        des_dir = os.path.join(des, dir)
        if not os.path.exists(des_dir):
            os.umask(0)
            os.makedirs(des_dir, mode=0o777)
        number = 0
        for image in os.listdir(start_dir):
            tmp = image
            flag = False
            tmp = tmp.split(".")[-1]
            list_tail = ['jpg', 'JPG', 'png', 'PNG', 'jpeg', 'JPEG']
            for tail in list_tail:
                if tmp != tail:
                    flag = True
                    break
            if flag == False:
                path_image = os.path.join(start_dir, image)
                print(path_image)
                image = cv2.imread(path_image)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image_name = "image_" + str(number) + ".jpg"
                path = os.path.join(des_dir, image_name)
                cv2.imwrite(path, image)
            else:
                continue
    
    shutil.rmtree(start)
    print("[INFO] Done!")

def processing(file="url.txt"):
    # path_file = os.path.dirname(os.path.abspath(__file__))
    # path_file = os.path.join(path_file, file)
    path_file = file
    with open(path_file) as f:
        lines = f.readlines()
    
    i = 0
    for line in lines:
        print("[INFO] crawling link {}".format(i))
        crawling(line, 5)
        convert_jpg()
        i += 1

# processing()
# if __name__ == "__main__":
#     crawling("https://www.123rf.com/stock-photo/apple_leaf.html?sti=nb2q6mc8hqu5psc5lw|", 2)
#     print("[INFO] convert png->jpg")
#     convert_jpg()
