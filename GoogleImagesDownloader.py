#Searching and Downloading Google Images/Image Links

#Import Libraries

import time       #Importing the time library to check the time of code execution
import requests
import os
import re

connection_timeout = 10  # Timeout per request in seconds

#Downloading entire Web Document (Raw Page Content)

def _download_page_html(url):
    try:
        request = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})

        if request.raise_for_status():
            raise TimeoutError

        return request.text

    except TimeoutError:
        print("URL connection timeout: It took too long to get the html content from the url" + str(url) + "exiting program \n")
        exit(1)

    except Exception as e:
        print("There was an error, exiting program")
        exit(1)


#Finding 'Next Image' from the given raw page
def _get_next_link_from_page(page):

    try:
        thumbnail_image_start = page.find('rg_di')
        if thumbnail_image_start == -1:    #If no links are found then give an error!
            return "no_link", 0

        else:
            image_meta_start = page.find('"class="rg_meta"')  # gets meta information about each image
            meta_content_start = page.find('"ou"', image_meta_start + 1) # the link of the actual image
            image_meta_end = page.find(',"ow"', meta_content_start + 1)  # the image's specific index number

            raw_html = str(page[meta_content_start + 6 : image_meta_end - 1]) #the raw html of the page
            return raw_html, image_meta_end  #possibly rename image_meta_end check what this actually is

    except AttributeError:
        print("The page could not be parsed, program is now exiting")
        exit(1)


#Getting all links with the help of '_images_get_next_image'
def _get_all_links_from_page(page):

    image_links = []

    while len(image_links) < amount_download:

        link, raw_html = _get_next_link_from_page(page)

        if link == "no_links":
            break

        image_links.append(link)      #Append all the links in the list named 'Links'
        time.sleep(0.1)        #Timer could be used to slow down the request for image downloads
        page = page[raw_html:]

    return image_links


# noinspection PyUnboundLocalVariable
def _download_all_images(file_name, image_links):

    images_requested = 0

    # This allows you to write all the links into a test file. This text file will be created in the same directory as your code. You can comment out the below 3 lines to stop writing the output to the text file.
    try:
        log = open(str(path) + "\\" + file_name + " - log.txt", 'a')  # Open the text file called database.txt
    # log.write(search_query + ": " + str(image_links) + "\n\n\n")         #Write the title of the page
    except IOError:
        print("there was an error opening the log, now exiting program")
        exit(1)

    log.write("Starting Download-----")
    log.write("Total time taken: " + str(total_time) + " seconds to gather all links\n")
    log.write("Requested all images from google images with URL: " + url + "\n")
    log.write("Search Query: " + str(search_query[current_query]) + "\n")

    while images_requested < len(image_links):

        image_name = None
        image_ext = None

        try:
            req = requests.get(image_links[images_requested], headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}, timeout=connection_timeout)

            if req.raise_for_status():
                raise TimeoutError
            else:

                image_info = re.compile("([\w-]+)(\.(jpe?g|png|gif|bmp))", re.MULTILINE)

                image_file_ext_name = image_info.search(str(image_links[images_requested]))

                image_name = image_file_ext_name[0]
                image_ext = image_file_ext_name[2]

                log.write("\t Image info: " + "\n")
                log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

                if len(image_name) > 255:
                    print("Image name was too long, it has been shortened")
                    image_name = image_name[0:254]
                    log.write("\t\t Image name: [WAS SHORTENED]" + str(image_name) + "\n")
                else:
                    log.write("\t\t Image name: " + str(image_name) + "\n")

                log.write("\t\t Image ext: " + str(image_ext) + "\n")
                log.write("\t\t Image downloaded from " + str(image_links[images_requested]) + "\n")

                print("\t Image info: ")
                print("\t\t Image number: " + str(images_requested + 1))
                print("\t\t Image name: " + str(image_name))
                print("\t\t Image ext: " + str(image_ext))
                print("\t\t Image downloaded from " + str(image_links[images_requested]))

                # TODO make distinction between image and filename

                output_file = open(str(path) + "\\" + str(images_requested + 1) + "_" + str(image_name), 'wb')
                data = req.content
                output_file.write(data)

        except TypeError:
            log.write("\t Image info: [TYPE ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")
            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")

            print("\t Image info: [IO ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))

            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")

            print("\t\t Image requested from " + str(image_links[images_requested]))

            images_requested += 1
            continue

        except IOError:
            log.write("\t Image info: [IO ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")
            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")

            print("\t Image info: [IO ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))

            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[images_requested]))

            images_requested += 1
            continue

        except TimeoutError:
            log.write("\t Image info: [TIMEOUT ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")

            print("\t Image info: [TIMEOUT ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))

            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")

            print("\t\t Image requested from " + str(image_links[images_requested]))

            images_requested += 1
            continue

        except IndexError:
            log.write("\t Image info: [INDEX ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")
            images_requested += 1

            print("\t Image info: [INDEX ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))
            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[images_requested]))

            continue

        except Exception:
            log.write("\t Image info: [GENERIC ERROR]" + "\n")
            log.write("\t\t Image number: " + str(images_requested + 1) + "\n")

            if image_name is not None:
                log.write("\t\t Image name: " + str(image_name) + "\n")
            else:
                log.write("\t\t Image name: Error getting name\n")
            if image_ext is not None:
                log.write("\t\t Image ext: " + str(image_ext) + "\n")
            else:
                log.write("\t\t Image name: Error getting ext\n")

            log.write("\t\t Image requested from " + str(image_links[images_requested]) + "\n")
            images_requested += 1

            print("\t Image info: [INDEX ERROR]")
            print("\t\t Image number: " + str(images_requested + 1))
            if image_name is not None:
                print("\t\t Image name: " + str(image_name))
            else:
                print("\t\t Image name: Error getting name")
            if image_ext is not None:
                print("\t\t Image ext: " + str(image_ext))
            else:
                print("\t\t Image ext: Error getting ext")
            print("\t\t Image requested from " + str(image_links[images_requested]))

            continue

        images_requested += 1

    log.close()

if __name__ == "__main__":

    #This list is used to search keywords. You can edit this list to search for google images of your choice. You can simply add and remove elements of the list.
    # search_query = input("Enter the image you would like to search\n")
    search_query = []

    if os.path._getfullpathname(str("words.txt")):

        search_file = open(os.path._getfullpathname("words.txt"), 'r')

        print("Loading queries from file\n")

        for word in search_file:
            search_query.append(str(word))

        print("Done loading queries from file\n")
    else:
        while True:
            query = input("Enter in the queries you want to download. Press enter to move to the next query and 'go' to start downloading \n")

            if str(query).lower() == "go":
                break
            else:
                search_query.append(str(query))

    while True:
        try:
            amount_download = input("Enter in the amount of images you would like to download between 1 and 100\n")

        except ValueError:
            print("Enter in a valid number between 1 and 100\n")

        if str(amount_download).isnumeric() and (int(amount_download) in range(1 , 101)):
            break

    amount_download = int(amount_download)

    file_name_regex = re.compile(r"-\w*|OR|\*|\"|-|\/|\\|\:|\?|\||\w*\.\w*|site:|related:|#\w*|@\w*", re.MULTILINE)

    individual_search_terms = ""
    file_names = []

    for i in range(len(search_query)):
        '''
        removes all special terms from google search query and then removes all the additional whitespace
        between character
        '''
        individual_search_terms = re.sub(file_name_regex, '', search_query[i]).strip(' ')

        # find all the words from the search query
        file_names.append(' '.join(re.findall(r"\w+", individual_search_terms, re.MULTILINE)))

    current_query = 0

    while current_query < len(search_query):

        if not os.path.exists(file_names[current_query]):
            try:
                if len(file_names[current_query]) > 255:
                    revised_file_name = file_names[current_query][0:254]  # Grabs 255 characters from the initial name
                    os.mkdir(revised_file_name)
                else:
                    os.mkdir(file_names[current_query])
            except IOError:
                print("There was a problem creating the directory, moving onto next query")
                continue
            except IndexError:
                print("There was a problem with the directory file name, moving onto next query")
                continue

        path = str(os.path._getfullpathname(file_names[current_query]))

        t0 = time.time()   #start the timer

        #Download Image Links
        image_links = []
        print ("Evaluating query: " + file_names[current_query])
        # %20, the 20 is ASCII for a space character, the % allows it to be used within the URL which would not be usually allowed
        search = search_query[current_query].replace(' ', '%20')

        limit_to_week = "&as_qdr=w"
        safe_search = "&safe=active"
        url = 'https://www.google.com/search?q=' + search + '&tbm=isch'
        raw_html = (_download_page_html(url))

        image_links = image_links + _get_all_links_from_page(raw_html)

        if image_links[0][0:4] == "type":
            print("Google could not process your query, moving to next query")
            current_query += 1
            continue

        t1 = time.time()    #stop the timer
        total_time = t1-t0   #Calculating the total time required to crawl, find and download all the links of 60,000 images
        print("Total time taken: " + str(total_time)+" seconds")

        ## To save imges to the same directory
        # IN this saving process we are just skipping the URL if there is any error

        images_requested = 0

        print("Starting download for query: " + file_names[current_query])

        _download_all_images(file_names[current_query], image_links)

        current_query += 1


    if len(image_links) == []:
        print("All queries were skipped because google could not process them")
    print("\nFinished downloading all images")
