import grequests, requests
import threading
from bs4 import BeautifulSoup
import os, shutil
from PIL import Image

def get_links(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, "lxml")

    slides = soup.find_all("section", {"class":"slide"})
    slides_links = [slide.find("img")["data-full"] for slide in slides]

    return slides_links

def download_images(links):
    requests = (grequests.get(link) for link in links)
    images = grequests.map(requests)
    images_names = []

    os.mkdir("images")
    threads = []
    for image in images:
        name = image.url.split("/")[-1].split("?")[0]
        images_names.append(f"images/{name}")
        t = threading.Thread(target=download_image, args=(image, f"images/{name}"))
        t.start()
        threads.append(t)

    map(lambda t: t.join(), threads)
    return images_names

def download_image(image, name):
    with open(name, 'wb') as f:
        f.write(image.content)

def make_pdf(images):
    # check if dir slide exists
    if not os.path.isdir('slide'):
        os.mkdir('slide')

    image_objects = [Image.open(image) for image in images]
    image_list = [image.convert('RGB') for image in image_objects]

    filename = "slide/" + " ".join(images[0].replace("images/", "").split("-")[:-2]) + ".pdf"

    image_list[0].save(filename, save_all=True, append_images=image_list[1:])

    #remove images dir
    shutil.rmtree('images')
    return filename


if __name__ == '__main__':
    print("Created by stepzar: github.com/stepzar")
    while True:
        url = input("\n\n\nEnter the url's slide you want to download (or enter 'exit' to quit): ")
        if url == "exit":
            print("Thanks for using this software! Bye")
            break
        elif not url.startswith("https://www.slideshare.net"):
            print("Not a slideshare link... retry!")
            continue

        links = get_links(url)
        images = download_images(links)
        filename = make_pdf(images)
        print(f"Downloaded: {filename.split('/')[1]}")
